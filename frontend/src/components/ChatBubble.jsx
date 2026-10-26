import { Bot, UserRound, Volume2, VolumeX, Sprout } from 'lucide-react';

export default function ChatBubble({ message, onSpeak, speakingId, canSpeak, language }) {
  const mine = message.role === 'user';
  return <div className={`chat-row ${mine ? 'user-row' : 'assistant-row'}`}>
    {!mine && <div className="avatar ai-avatar"><Sprout size={20}/></div>}
    <div className="message-column">
      <div className={`bubble ${mine ? 'user-bubble' : 'assistant-bubble'}`}>
        <p className="bubble-text">{message.content}</p>
        {!mine && <div className="bubble-actions"><button type="button" onClick={() => onSpeak(message)} disabled={!canSpeak} className="listen-button">{speakingId === message.id ? <VolumeX size={16}/> : <Volume2 size={16}/>} {speakingId === message.id ? 'Stop speaking' : 'Listen to answer'}</button><span className="demo-annotation">Demo guidance</span></div>}
      </div>
      <span className="bubble-time">{new Date(message.created_at || Date.now()).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</span>
    </div>
    {mine && <div className="avatar user-avatar"><UserRound size={18}/></div>}
  </div>;
}
