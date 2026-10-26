import { Sprout } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Logo({ compact = false }) {
  return <Link to="/" className="brand" aria-label="RythuMitra AI home">
    <span className="brand-mark"><Sprout size={compact ? 23 : 29} strokeWidth={2.4}/></span>
    <span className="brand-copy"><strong>Rythu<span>Mitra</span> AI</strong>{!compact && <small>Your farming companion</small>}</span>
  </Link>;
}
