import { useCallback, useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, ArrowLeft, ArrowRight, ChevronRight, Leaf, Menu, MessageCircle, Mic2, Plus, Send, ShieldCheck, Sparkles, Sprout, Trash2, X } from 'lucide-react';
import Logo from '../components/Logo';
import LanguageSelect from '../components/LanguageSelect';
import MicrophoneButton from '../components/MicrophoneButton';
import ChatBubble from '../components/ChatBubble';
import { api } from '../lib/api';
import { DEMO_PROMPTS, LANGUAGES, SECTION_LABELS, getLocalizedPrompts } from '../lib/config';

export default function Assistant({ language, setLanguage }) {
  const [conversations, setConversations] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [voiceStage, setVoiceStage] = useState('idle');
  const [transcriptNeedsReview, setTranscriptNeedsReview] = useState(false);
  const [audioUrl, setAudioUrl] = useState('');
  const [audioMessageId, setAudioMessageId] = useState(null);
  const [audioState, setAudioState] = useState('idle');
  const [autoSpeak, setAutoSpeak] = useState(true);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('loading');
  const [backendInfo, setBackendInfo] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEnd = useRef(null);
  const recorderRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const recordingChunksRef = useRef([]);
  const recordingTimerRef = useRef(null);
  const audioRef = useRef(null);
  const audioUrlRef = useRef('');
  const sendMessageRef = useRef(null);
  const speechAvailable = typeof window !== 'undefined' && !!navigator.mediaDevices?.getUserMedia && typeof MediaRecorder !== 'undefined';
  const listening = voiceStage === 'recording';

  const refreshConversations = useCallback(async () => {
    const list = await api.listConversations();
    setConversations(list);
  }, []);

  useEffect(() => {
    let active = true;
    let connected = false;
    const checkBackend = async () => {
      try {
        const info = await api.health();
        if (!active) return;
        setStatus('connected');
        setBackendInfo(info);
        setError(current => current === 'Cannot connect to the backend. Start FastAPI at http://localhost:8000.' ? '' : current);
        if (!connected) {
          connected = true;
          await refreshConversations();
        }
      } catch (err) {
        if (!active) return;
        connected = false;
        setStatus('offline');
        setError(err.message);
      }
    };
    checkBackend();
    const retryTimer = setInterval(checkBackend, 5000);
    return () => { active = false; clearInterval(retryTimer); };
  }, [refreshConversations]);

  useEffect(() => { messagesEnd.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }); }, [messages, busy]);
  useEffect(() => () => {
    clearTimeout(recordingTimerRef.current);
    recorderRef.current?.stream?.getTracks().forEach(track => track.stop());
    mediaStreamRef.current?.getTracks().forEach(track => track.stop());
    if (audioRef.current) audioRef.current.pause();
    if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current);
  }, []);

  const playAnswer = useCallback(async (message, replay = false) => {
    if (!message?.content) return;
    const spokenText = message.content.split('\n\nSources:\n', 1)[0].trim();
    try {
      if (audioMessageId === message.id && audioUrl && audioRef.current) {
        if (replay) audioRef.current.currentTime = 0;
        await audioRef.current.play();
        setAudioState('playing');
        setVoiceStage('ready');
        return;
      }
      setVoiceStage('generating_voice');
      setAudioState('generating');
      setAudioMessageId(message.id);
      audioRef.current?.pause();
      const audio = await api.synthesize(spokenText, language);
      const nextUrl = URL.createObjectURL(audio);
      if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current);
      audioUrlRef.current = nextUrl;
      setAudioUrl(nextUrl);
      setAudioMessageId(message.id);
      setAudioState('ready');
      if (audioRef.current) {
        audioRef.current.src = nextUrl;
        if (autoSpeak || replay) {
          try {
            await audioRef.current.play();
            setAudioState('playing');
          } catch {
            setAudioState('ready');
          }
        }
      }
      setVoiceStage('ready');
    } catch (err) {
      setAudioState('error');
      setVoiceStage('ready');
      if (replay) {
        setError(`Voice playback unavailable: ${err.message}`);
      } else {
        console.warn('Auto voice playback unavailable:', err.message);
      }
    } finally {
      setVoiceStage('ready');
    }
  }, [audioMessageId, audioUrl, language, autoSpeak]);

  const pauseAnswer = () => {
    audioRef.current?.pause();
    setAudioState('paused');
  };

  const sendMessage = useCallback(async (text) => {
    const question = (text || '').trim();
    if (!question || busy) return;
    setError('');
    setInput('');
    setTranscriptNeedsReview(false);
    setBusy(true);
    setVoiceStage('thinking');
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
      setVoiceStage('ready');
      if (autoSpeak && backendInfo?.tts_provider === 'gnani_timbre' && result.assistant_message) {
        await playAnswer(result.assistant_message);
      }
    } catch (err) {
      setMessages(old => old.filter(m => m.id !== optimistic.id));
      setInput(question);
      setError(err.message);
      setVoiceStage('ready');
    } finally {
      setBusy(false);
      setVoiceStage('ready');
    }
  }, [busy, conversationId, language, refreshConversations, autoSpeak, playAnswer, backendInfo]);
  sendMessageRef.current = sendMessage;

  const beginVoice = async () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setAudioState('ready');
    }

    if (listening) {
      setVoiceStage('transcribing');
      recorderRef.current?.stop();
      return;
    }
    if (!speechAvailable) {
      setError('Microphone recording is not available in this browser. You can type your question instead.');
      setVoiceStage('ready');
      return;
    }
    setError('');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      const mimeType = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus'].find(type => MediaRecorder.isTypeSupported(type));
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      recorderRef.current = recorder;
      recordingChunksRef.current = [];
      recorder.ondataavailable = event => { if (event.data.size) recordingChunksRef.current.push(event.data); };
      recorder.onerror = () => {
        setVoiceStage('ready');
        setError('The recording failed. Check microphone permissions and try again.');
      };
      recorder.onstop = async () => {
        clearTimeout(recordingTimerRef.current);
        stream.getTracks().forEach(track => track.stop());
        mediaStreamRef.current = null;
        const recording = new Blob(recordingChunksRef.current, { type: recorder.mimeType || 'audio/webm' });
        if (!recording.size) {
          setVoiceStage('ready');
          setError('No audio was recorded. Please try again.');
          return;
        }
        setVoiceStage('transcribing');
        try {
          const result = await api.transcribe(recording, language);
          const transcript = result.transcript?.trim();
          if (!transcript) {
            throw new Error(language === 'te-IN' ? 'మాట స్పష్టంగా వినిపించలేదు. దయచేసి మళ్లీ మాట్లాడండి.' : 'No speech was recognized. Please record again or type your question.');
          }
          setInput('');
          setTranscriptNeedsReview(false);
          setVoiceStage('ready');
          await sendMessageRef.current?.(transcript);
        } catch (err) {
          setVoiceStage('ready');
          setError(err.message);
        }
      };
      recorder.start();
      setVoiceStage('recording');
      recordingTimerRef.current = setTimeout(() => {
        if (recorder.state === 'recording') recorder.stop();
      }, 60000);
    } catch (err) {
      setVoiceStage('ready');
      setError(err.name === 'NotAllowedError' ? 'Microphone permission was denied. Allow access or type your question.' : 'Unable to start microphone recording. Check your device permissions.');
    }
  };

  const handleSelectConversation = async id => {
    if (recorderRef.current?.state === 'recording') recorderRef.current.stop();
    audioRef.current?.pause();
    if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current);
    audioUrlRef.current = '';
    setAudioUrl('');
    setAudioMessageId(null);
    setAudioState('idle');
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
    if (recorderRef.current?.state === 'recording') recorderRef.current.stop();
    audioRef.current?.pause();
    if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current);
    audioUrlRef.current = '';
    setAudioUrl('');
    setAudioMessageId(null);
    setAudioState('idle');
    setConversationId(null);
    setMessages([]);
    setInput('');
    setTranscriptNeedsReview(false);
    setError('');
    setVoiceStage('idle');
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

  const localizedPrompts = getLocalizedPrompts(language);
  const labels = SECTION_LABELS[language] || SECTION_LABELS['en-IN'];

  const usePrompt = (prompt) => sendMessage(prompt.query || prompt.detail);
  const stageLabel = {
    idle: language === 'te-IN' ? 'సిద్ధంగా ఉంది' : 'Ready',
    recording: language === 'te-IN' ? 'వినబడుతోంది · ఆపడానికి నొక్కండి' : 'Recording · tap to stop',
    transcribing: language === 'te-IN' ? 'జ్ఞాని ప్రిస్మా విశ్లేషిస్తోంది…' : 'Transcribing with Gnani Prisma…',
    thinking: language === 'te-IN' ? 'జెమిని ఆలోచిస్తోంది…' : 'Thinking with Gemini…',
    generating_voice: language === 'te-IN' ? 'జ్ఞాని టింబ్రే వాయిస్ తయారవుతోంది…' : 'Generating voice with Gnani Timbre…',
    ready: language === 'te-IN' ? 'సిద్ధంగా ఉంది' : 'Ready',
    error: language === 'te-IN' ? 'సమస్య ఎదురైంది' : 'Needs attention',
  }[voiceStage] || (language === 'te-IN' ? 'సిద్ధంగా ఉంది' : 'Ready');

  return <div className="assistant-layout">
    {sidebarOpen && <button type="button" className="sidebar-backdrop" aria-label="Close menu" onClick={() => setSidebarOpen(false)}/>}
    <aside className={`assistant-sidebar ${sidebarOpen ? 'show' : ''}`}>
      <div className="sidebar-top"><Logo compact/><button className="sidebar-close" aria-label="Close sidebar" onClick={()=>setSidebarOpen(false)}><X size={20}/></button></div>
      <Link to="/" className="sidebar-back-top" title={labels.backToHome}><ArrowLeft size={16}/><span>{labels.backToHome}</span></Link>
      <button type="button" className="new-conversation" onClick={handleNew}><Plus size={22}/><span>{labels.newConversation}</span><ArrowRight size={18}/></button>
      <div className="sidebar-section-label">
        {labels.yourConversations}
        {conversations.length > 0 && <span style={{marginLeft: 6, fontWeight: 700}}>({conversations.length})</span>}
      </div>
      <div className="conversation-list">
        {conversations.length ? conversations.map(conv => <div className={`history-entry ${conversationId === conv.id ? 'active' : ''}`} key={conv.id}>
          <button type="button" className="history-open" onClick={() => handleSelectConversation(conv.id)}><MessageCircle size={17}/><span title={conv.title}>{conv.title}</span></button>
          <button type="button" aria-label={`Delete ${conv.title}`} className="history-delete" onClick={e => handleDelete(e, conv.id)}><Trash2 size={15}/></button>
        </div>) : <p className="history-empty">{language === 'te-IN' ? 'మీరు ప్రశ్న అడిగిన తర్వాత మునుపటి సంభాషణలు ఇక్కడ కనిపిస్తాయి.' : 'Your questions will appear here once you start a conversation.'}</p>}
      </div>
      <div className="sidebar-spacer"/>
      <div className="sidebar-section-label quick-label">{labels.exampleQuestions}</div>
      <div className="prompt-sidebar">
        {localizedPrompts.map(p => <button key={p.id || p.title} type="button" onClick={() => { usePrompt(p); setSidebarOpen(false); }}><Sprout size={16}/><span>{p.title}</span><ChevronRight size={14}/></button>)}
      </div>
      <div className="sidebar-info"><span className="sidebar-info-icon"><ShieldCheck size={18}/></span><div><strong>{language === 'te-IN' ? 'రైతు మిత్ర AI సిద్ధంగా ఉంది' : 'RythuMitra AI Assistant'}</strong><p>{language === 'te-IN' ? 'పంట సలహాలు, పురుగుల నివారణ మరియు వాయిస్ సహాయం కోసం సిద్ధంగా ఉంది.' : 'Direct crop advice, pest solutions, dosages, and voice assistance.'}</p></div></div>
    </aside>

    <div className="assistant-main">
      <header className="assistant-topbar">
        <div className="topbar-heading">
          <button type="button" className="sidebar-toggle" onClick={() => setSidebarOpen(true)} aria-label="Open sidebar"><Menu size={23}/></button>
          <div className="topbar-app-icon"><Sprout size={23}/></div>
          <div><strong>RythuMitra AI</strong><span>{labels.companionSub || 'Your personal farming companion'}</span></div>
        </div>
        <div className="assistant-top-actions">
          {status === 'offline' && (
            <span className="connection-badge off" title="Cannot connect to server">
              <i/>{language === 'te-IN' ? 'ఆఫ్‌లైన్' : 'Offline'}
            </span>
          )}
          <LanguageSelect language={language} onChange={setLanguage}/>
        </div>
      </header>

      <div className="chat-area">
        {messages.length === 0 ? <div className="welcome-screen">
          <div className="welcome-tag"><Sparkles size={15}/> YOUR FARMING COMPANION</div>
          <h1>{labels.welcomeHeading1}<br/><span>{labels.welcomeHeading2}</span></h1>
          <p>{labels.welcomeDesc}</p>
          <div className={`voice-stage ${listening ? 'voice-active' : ''}`}>
            <div className="wave-bars left-bars">{[17,28,46,23,37,61,31,48,25,19,36,14].map((h,i)=><span style={{height:h}} key={i}/>)}</div>
            <MicrophoneButton listening={listening} available={speechAvailable} busy={busy || voiceStage === 'transcribing' || voiceStage === 'generating_voice'} onClick={beginVoice}/>
            <div className="wave-bars right-bars">{[14,36,19,25,48,31,61,37,23,46,28,17].map((h,i)=><span style={{height:h}} key={i}/>)}</div>
          </div>
          <div className="voice-state"><span className={listening ? 'voice-indicator active' : 'voice-indicator'}/>{stageLabel}</div>
          <div className="welcome-examples"><span>{labels.tryAsking}</span><div>{localizedPrompts.map(p=><button key={p.id || p.title} disabled={busy} type="button" onClick={() => usePrompt(p)}><Leaf size={15}/>{p.title}<ArrowRight size={14}/></button>)}</div></div>
        </div> : <div className="messages-wrap"><div className="chat-datestamp">Your farming conversation</div>{messages.map(message => <ChatBubble key={message.id} message={message} onPlay={playAnswer} onPause={pauseAnswer} onReplay={message => playAnswer(message, true)} audioMessageId={audioMessageId} audioState={audioState}/>)}{busy && <div className="chat-row assistant-row"><div className="avatar ai-avatar"><Sprout size={20}/></div><div className="thinking-bubble"><span/><span/><span/> {stageLabel}</div></div>}<div ref={messagesEnd}/></div>}
      </div>

      <div className="composer-area">
        {error && <div role="alert" className="error-notice"><AlertCircle size={18}/><span>{error}</span><button type="button" onClick={() => setError('')} aria-label="Dismiss error"><X size={16}/></button></div>}
        {transcriptNeedsReview && <div className="transcript-review" role="status">Review the transcript, correct it if needed, then send your question.</div>}

        {listening ? (
          <div className="active-voice-panel" role="status">
            <div className="voice-panel-info">
              <span className="voice-pulse-dot" />
              <div className="voice-wave-mini">
                <span/><span/><span/><span/><span/>
              </div>
              <strong>{labels.listening}</strong>
            </div>
            <button type="button" className="voice-stop-chip" onClick={beginVoice}>
              {labels.stopAndSend}
            </button>
          </div>
        ) : (
          <div className="composer-voice-bar">
            <button
              type="button"
              className="speak-now-banner-btn"
              onClick={beginVoice}
              disabled={busy || voiceStage === 'transcribing' || voiceStage === 'generating_voice'}
              title="Speak your question using microphone"
            >
              <div className="mic-circle"><Mic2 size={16}/></div>
              <span>{messages.length > 0 ? labels.tapToSpeakAgain : labels.tapToSpeak}</span>
            </button>
            {stageLabel && stageLabel !== 'Ready' && stageLabel !== 'సిద్ధంగా ఉంది' && <span className="voice-stage-pill">{stageLabel}</span>}
          </div>
        )}

        <form className="message-composer" onSubmit={e => { e.preventDefault(); sendMessage(input); }}>
          <button
            type="button"
            className={`composer-mic ${listening ? 'active' : ''}`}
            aria-label={listening ? 'Stop recording' : 'Record your question'}
            title={listening ? 'Stop recording' : 'Record with Gnani Prisma'}
            onClick={beginVoice}
            disabled={busy || voiceStage === 'transcribing' || voiceStage === 'generating_voice'}
          >
            <Mic2 size={22}/>
          </button>
          <textarea
            rows="1"
            value={input}
            onChange={e => { setInput(e.target.value); setTranscriptNeedsReview(false); }}
            placeholder={labels.inputPlaceholder}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(input); } }}
            aria-label="Farming question"
          />
          <button className="send-button" aria-label="Send your question" disabled={busy || !input.trim()} type="submit"><Send size={19}/></button>
        </form>
        <div className="composer-footnote">
          <div>
            <span className="footnote-dot"/>
            <span>{stageLabel}</span>
            <button
              type="button"
              className="quick-speak-pill"
              onClick={beginVoice}
              disabled={busy || voiceStage === 'transcribing' || voiceStage === 'generating_voice'}
            >
              <Mic2 size={12}/>
              {listening ? (language === 'te-IN' ? 'ఆపండి (Stop)' : 'Stop') : (language === 'te-IN' ? 'నోటితో అడగండి (Speak)' : 'Speak')}
            </button>
          </div>
          <label className="autoplay-control">
            <input type="checkbox" checked={autoSpeak} onChange={e => setAutoSpeak(e.target.checked)}/>
            {labels.autoPlay}
          </label>
        </div>
      </div>
      <audio
        ref={audioRef}
        hidden
        onEnded={() => { setAudioState('ready'); setVoiceStage('ready'); }}
        onPause={() => setAudioState(current => current === 'playing' ? 'paused' : current)}
      />
    </div>
  </div>;
}
