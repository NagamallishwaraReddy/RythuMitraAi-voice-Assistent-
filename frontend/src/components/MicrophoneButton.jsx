import { Mic2, MicOff, LoaderCircle } from 'lucide-react';
export default function MicrophoneButton({ listening, available, busy, onClick, size = 'large' }) {
  return <button type="button" aria-label={listening ? 'Stop recording' : 'Start voice recording'} title={available ? 'Record a question with Gnani Prisma' : 'Microphone recording is not available in this browser'} className={`microphone-button ${size} ${listening ? 'is-listening' : ''}`} disabled={busy} onClick={onClick}>
    <span className="mic-inner">{busy ? <LoaderCircle className="spin" size={32}/> : listening ? <MicOff size={39} strokeWidth={2.1}/> : <Mic2 size={39} strokeWidth={2.1}/>}</span>
  </button>;
}
