import { useCallback, useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, ArrowLeft, ArrowRight, AudioLines, BookOpenText, Check, ChevronRight, CircleHelp, ClipboardList, Globe2, Headphones, Leaf, Menu, MessageCircle, Mic2, Plus, Send, ShieldCheck, Sparkles, Sprout, Trash2, Volume2, X } from 'lucide-react';
import Logo from '../components/Logo';
import LanguageSelect from '../components/LanguageSelect';
import MicrophoneButton from '../components/MicrophoneButton';
import ChatBubble from '../components/ChatBubble';
import { api } from '../lib/api';
import { DEMO_PROMPTS, LANGUAGES } from '../lib/config';

export default function Assistant({ language, setLanguage }) {
  const [conversations, setConversations] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [listening, setListening] = useState(false);
  const [interim, setInterim] = useState('');
  const [speakingId, setSpeakingId] = useState(null);
  const [autoSpeak, setAutoSpeak] = useState(true);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('loading');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEnd = useRef(null);
  const recognitionRef = useRef(null);
  const sendRef = useRef(null);
  const selectedLanguage = LANGUAGES.find(x => x.code === language) || LANGUAGES[0];
  const SpeechRecognition = typeof window !== 'undefined' ? (window.SpeechRecognition || window.webkitSpeechRecognition) : null;
  const speechAvailable = !!SpeechRecognition;
  const synthesisAvailable = typeof window !== 'undefined' && !!window.speechSynthesis;

  const refreshConversations = useCallback(async () => {
    const list = await api.listConversations();
    setConversations(list);
  }, []);

  useEffect(() => {
    api.health().then(() => { setStatus('connected'); return refreshConversations(); })
      .catch(err => { setStatus('offline'); setError(err.message); });
  }, [refreshConversations]);

  useEffect(() => { messagesEnd.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }); }, [messages, busy]);
  useEffect(() => () => { recognitionRef.current?.abort(); window.speechSynthesis?.cancel(); }, []);

  const say = useCallback((message, lang) => {
    if (!synthesisAvailable || !message?.content) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(message.content);
    utterance.lang = lang;
    utterance.rate = 0.9;
    const voices = window.speechSynthesis.getVoices();
    const matching = voices.find(v => v.lang === lang) || voices.find(v => v.lang?.startsWith(lang.slice(0, 2)));
    if (matching) utterance.voice = matching;
    utterance.onend = () => setSpeakingId(null);
    utterance.onerror = () => setSpeakingId(null);
    setSpeakingId(message.id);
    window.speechSynthesis.speak(utterance);
  }, [synthesisAvailable]);

  const handleSpeak = (message) => {
    if (!synthesisAvailable) return;
    if (speakingId === message.id) { window.speechSynthesis.cancel(); setSpeakingId(null); return; }
    say(message, language);
  };

  const sendMessage = useCallback(async (text) => {
    const question = (text || '').trim();
    if (!question || busy) return;
    setError('');
    setInput('');
    setInterim('');
    setBusy(true);
    const optimistic = { id: `temp-${Date.now()}`, role: 'user', content: question, created_at: new Date().toISOString() };
    setMessages(old => [...old, optimistic]);
    try {
      let id = conversationId;
      if (!id) {
        const created = await api.createConversation(language);
        id = created.id;
        setConversationId(id);
      }
      const result = await api.sendMessage({ conversation_id: id, language_code: language, message: question });
      const conversation = await api.getConversation(id);
      setMessages(conversation.messages);
      refreshConversations().catch(() => {});
      if (autoSpeak && synthesisAvailable && result.assistant_message) say(result.assistant_message, language);
    } catch (err) {
      setMessages(old => old.filter(m => m.id !== optimistic.id));
      setInput(question);
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }, [busy, conversationId, language, refreshConversations, autoSpeak, synthesisAvailable, say]);
  sendRef.current = sendMessage;

  const beginVoice = () => {
    if (listening) { recognitionRef.current?.stop(); return; }
    if (!speechAvailable) {
      setError('This browser does not offer speech recognition preview. Type your question for now; Gnani Prisma will replace this in the next phase.');
      return;
    }
    setError('');
    const recog = new SpeechRecognition();
    recognitionRef.current = recog;
    recog.lang = language;
    recog.continuous = false;
    recog.interimResults = true;
    recog.onstart = () => setListening(true);
    recog.onresult = event => {
      let partial = '', complete = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) complete += event.results[i][0].transcript;
        else partial += event.results[i][0].transcript;
      }
      if (partial) setInterim(partial);
      if (complete.trim()) {
        setInput(complete.trim());
        setInterim('');
        recog.stop();
        sendRef.current?.(complete.trim());
      }
    };
    recog.onerror = event => {
      setListening(false);
      if (event.error !== 'aborted' && event.error !== 'no-speech') {
        setError(`Browser speech preview: ${event.error}. You can type your question instead.`);
      }
    };
    recog.onend = () => setListening(false);
    try { recog.start(); } catch { setError('Unable to start microphone. Check browser permissions.'); }
  };

  const handleSelectConversation = async id => {
    recognitionRef.current?.abort();
    window.speechSynthesis?.cancel();
    setSpeakingId(null);
    setSidebarOpen(false);
    setError('');
    try {
      const conv = await api.getConversation(id);
      setConversationId(id);
      setMessages(conv.messages);
      setLanguage(conv.language_code);
    } catch (err) { setError(err.message); }
  };

  const handleNew = () => {
    recognitionRef.current?.abort();
    window.speechSynthesis?.cancel();
    setSpeakingId(null);
    setConversationId(null);
    setMessages([]);
    setInput('');
    setInterim('');
    setError('');
    setSidebarOpen(false);
  };

  const handleDelete = async (event, id) => {
    event.stopPropagation();
    try {
      await api.deleteConversation(id);
      if (id === conversationId) handleNew();
      await refreshConversations();
    } catch (err) { setError(err.message); }
  };

  const usePrompt = (prompt) => sendMessage(language === 'te-IN' ? prompt.telugu : prompt.detail);

  return <div className="assistant-layout">
    {sidebarOpen && <button type="button" className="sidebar-backdrop" aria-label="Close menu" onClick={() => setSidebarOpen(false)}/>}
    <aside className={`assistant-sidebar ${sidebarOpen ? 'show' : ''}`}>
      <div className="sidebar-top"><Logo compact/><button className="sidebar-close" aria-label="Close sidebar" onClick={()=>setSidebarOpen(false)}><X size={20}/></button></div>
      <button type="button" className="new-conversation" onClick={handleNew}><Plus size={19}/> New conversation <ArrowRight size={16}/></button>
      <div className="sidebar-section-label">YOUR CONVERSATIONS</div>
      <div className="conversation-list">
        {conversations.length ? conversations.map(conv => <div className={`history-entry ${conversationId === conv.id ? 'active' : ''}`} key={conv.id}>
          <button type="button" className="history-open" onClick={() => handleSelectConversation(conv.id)}><MessageCircle size={17}/><span title={conv.title}>{conv.title}</span></button>
          <button type="button" aria-label={`Delete ${conv.title}`} className="history-delete" onClick={e => handleDelete(e, conv.id)}><Trash2 size={15}/></button>
        </div>) : <p className="history-empty">Your questions will appear here once you start a conversation.</p>}
      </div>
      <div className="sidebar-section-label quick-label">EXAMPLE QUESTIONS</div>
      <div className="prompt-sidebar">
        {DEMO_PROMPTS.map(p => <button key={p.title} type="button" onClick={() => { usePrompt(p); setSidebarOpen(false); }}><Sprout size={17}/><span>{p.title}</span><ChevronRight size={15}/></button>)}
      </div>
      <div className="sidebar-spacer"/>
      <div className="sidebar-info"><span className="sidebar-info-icon"><ShieldCheck size={18}/></span><div><strong>Prototype in progress</strong><p>Gnani and reasoning APIs will be connected in phase 2.</p></div></div>
      <Link to="/" className="sidebar-back"><ArrowLeft size={16}/> Back to home</Link>
    </aside>

    <div className="assistant-main">
      <header className="assistant-topbar">
        <div className="topbar-heading"><button type="button" className="sidebar-toggle" onClick={() => setSidebarOpen(true)} aria-label="Open sidebar"><Menu size={23}/></button><div className="topbar-app-icon"><Sprout size={23}/></div><div><strong>RythuMitra AI</strong><span>Your personal farming companion</span></div></div>
        <div className="assistant-top-actions"><span className={`connection-badge ${status === 'connected' ? 'ok' : 'off'}`}><i/>{status === 'connected' ? 'Demo online' : status === 'loading' ? 'Connecting...' : 'Backend offline'}</span><LanguageSelect language={language} onChange={setLanguage}/></div>
      </header>

      <div className="chat-area">
        {messages.length === 0 ? <div className="welcome-screen">
          <div className="welcome-tag"><Sparkles size={15}/> YOUR FARMING COMPANION</div>
          <h1>How can I help your<br/><span>crops grow better?</span></h1>
          <p>Ask me about any crop: paddy, cotton, tomato, maize, banana and more.<br/>Speak naturally, just like a conversation.</p>
          <div className={`voice-stage ${listening ? 'voice-active' : ''}`}>
            <div className="wave-bars left-bars">{[17,28,46,23,37,61,31,48,25,19,36,14].map((h,i)=><span style={{height:h}} key={i}/>)}</div>
            <MicrophoneButton listening={listening} available={speechAvailable} busy={busy} onClick={beginVoice}/>
            <div className="wave-bars right-bars">{[14,36,19,25,48,31,61,37,23,46,28,17].map((h,i)=><span style={{height:h}} key={i}/>)}</div>
          </div>
          <div className="voice-state"><span className={listening ? 'voice-indicator active' : 'voice-indicator'}/>{listening ? 'Listening… Speak now' : 'Tap the microphone to speak'}</div>
          {interim && <div className="interim-text">{interim}</div>}
          <div className="welcome-examples"><span>Try asking:</span><div>{DEMO_PROMPTS.map(p=><button key={p.title} disabled={busy} type="button" onClick={() => usePrompt(p)}><Leaf size={15}/>{p.title}<ArrowRight size={14}/></button>)}</div></div>
        </div> : <div className="messages-wrap"><div className="chat-datestamp">Your farming conversation</div>{messages.map(message => <ChatBubble key={message.id} message={message} onSpeak={handleSpeak} speakingId={speakingId} canSpeak={synthesisAvailable} language={language}/>)}{busy && <div className="chat-row assistant-row"><div className="avatar ai-avatar"><Sprout size={20}/></div><div className="thinking-bubble"><span/><span/><span/> Checking your crop question (demo)…</div></div>}<div ref={messagesEnd}/></div>}
      </div>

      <div className="composer-area">
        {error && <div role="alert" className="error-notice"><AlertCircle size={18}/><span>{error}</span><button type="button" onClick={() => setError('')} aria-label="Dismiss error"><X size={16}/></button></div>}
        <form className="message-composer" onSubmit={e => { e.preventDefault(); sendMessage(input); }}>
          <button type="button" className={`composer-mic ${listening ? 'active' : ''}`} aria-label="Record your question" title="Browser speech preview" onClick={beginVoice} disabled={busy}><Mic2 size={22}/></button>
          <textarea rows="1" value={input} onChange={e => setInput(e.target.value)} placeholder={language === 'te-IN' ? 'మీ వ్యవసాయ ప్రశ్నను అడగండి... (లేదా ఇక్కడ టైప్ చేయండి)' : 'Ask a question about your crop...'} onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(input); } }} aria-label="Farming question"/>
          <button className="send-button" aria-label="Send your question" disabled={busy || !input.trim()} type="submit"><Send size={19}/></button>
        </form>
        <div className="composer-footnote"><div><span className="footnote-dot"/> Demo mode: recognizes many crops and question types; unrestricted crop advice needs the LLM. Gnani voice integration comes next.</div><label className="autoplay-control"><input type="checkbox" checked={autoSpeak} onChange={e => setAutoSpeak(e.target.checked)}/> Read replies aloud</label></div>
      </div>
    </div>
  </div>;
}
