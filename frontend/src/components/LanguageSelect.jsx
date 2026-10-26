import { Globe2, ChevronDown } from 'lucide-react';
import { LANGUAGES } from '../lib/config';

export default function LanguageSelect({ language, onChange }) {
  return <label className="language-picker" aria-label="Conversation language">
    <Globe2 size={17} strokeWidth={2} />
    <select value={language} onChange={e => onChange(e.target.value)} aria-label="Select language">
      {LANGUAGES.map(lang => <option key={lang.code} value={lang.code}>{lang.label} ({lang.english})</option>)}
    </select>
    <ChevronDown size={14}/>
  </label>;
}
