import { Globe2, ChevronDown } from 'lucide-react';
import { LANGUAGES } from '../lib/config';

export default function LanguageSelect({ language, onChange }) {
  const current = LANGUAGES.find(l => l.code === language) || LANGUAGES[0];

  return (
    <div className="language-picker" title="Change Language / భాష మార్చండి">
      <Globe2 size={15} strokeWidth={2.2} className="lang-icon" />
      <span className="lang-display-text">{current.label}</span>
      <ChevronDown size={13} strokeWidth={2.5} className="lang-chevron" />
      <select
        value={language}
        onChange={e => onChange(e.target.value)}
        aria-label="Select language"
        className="lang-select-hidden"
      >
        {LANGUAGES.map(lang => (
          <option key={lang.code} value={lang.code}>
            {lang.label} ({lang.english})
          </option>
        ))}
      </select>
    </div>
  );
}
