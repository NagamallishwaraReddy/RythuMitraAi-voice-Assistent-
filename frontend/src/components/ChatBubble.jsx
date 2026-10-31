import { Pause, Play, RotateCcw, UserRound, Volume2, Sprout } from 'lucide-react';

export default function ChatBubble({ message, onPlay, onPause, onReplay, audioMessageId, audioState, labels = {} }) {
  const mine = message.role === 'user';
  const hasAudio = audioMessageId === message.id;

  const playText = labels.play || 'Play';
  const pauseText = labels.pause || 'Pause';
  const replayText = labels.replay || 'Replay';
  const generatingText = labels.generatingVoice || 'Generating voice...';
  const voiceReplyText = labels.voiceReply || 'Voice reply';
  const gnaniText = labels.gnaniTimbre || 'Gnani Timbre';

  return <div className={`chat-row ${mine ? 'user-row' : 'assistant-row'}`}>
    {!mine && <div className="avatar ai-avatar"><Sprout size={20}/></div>}
    <div className="message-column">
      <div className={`bubble ${mine ? 'user-bubble' : 'assistant-bubble'}`}>
        <p className="bubble-text">{message.content}</p>
        {!mine && <div className="bubble-actions">
          <button
            type="button"
            onClick={() => hasAudio && audioState === 'playing' ? onPause() : onPlay(message)}
            disabled={audioState === 'generating'}
            className="listen-button"
            aria-label={hasAudio && audioState === 'playing' ? pauseText : audioState === 'generating' && hasAudio ? generatingText : playText}
          >
            {hasAudio && audioState === 'playing' ? <Pause size={16}/> : audioState === 'generating' && hasAudio ? <Volume2 size={16}/> : <Play size={16}/>}
            {audioState === 'generating' && hasAudio ? generatingText : hasAudio && audioState === 'playing' ? pauseText : playText}
          </button>
          {hasAudio && (
            <button type="button" onClick={() => onReplay(message)} className="listen-button replay-button" aria-label={replayText}>
              <RotateCcw size={15}/> {replayText}
            </button>
          )}
          <span className="demo-annotation">{hasAudio ? gnaniText : voiceReplyText}</span>
        </div>}
      </div>
      <span className="bubble-time">{new Date(message.created_at || Date.now()).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</span>
    </div>
    {mine && <div className="avatar user-avatar"><UserRound size={18}/></div>}
  </div>;
}
