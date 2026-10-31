import { Link, NavLink } from 'react-router-dom';
import { ArrowUpRight, Menu, X } from 'lucide-react';
import { useState } from 'react';
import Logo from './Logo';
import LanguageSelect from './LanguageSelect';
import { getUITranslations } from '../lib/config';

export default function Header({ language, setLanguage }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const t = getUITranslations(language);

  return <header className="site-header">
    <div className="header-inner container">
      <Logo subtitle={t.assistant?.companionSub || 'Your farming companion'} />
      <nav className={menuOpen ? 'site-nav open' : 'site-nav'} aria-label="Primary navigation">
        <NavLink to="/" end onClick={() => setMenuOpen(false)}>{t.nav.home}</NavLink>
        <a href="/#how-it-works" onClick={() => setMenuOpen(false)}>{t.nav.howItWorks}</a>
        <a href="/#benefits" onClick={() => setMenuOpen(false)}>{t.nav.features}</a>
        <NavLink to="/assistant" onClick={() => setMenuOpen(false)}>{t.nav.voiceAssistant}</NavLink>
      </nav>
      <div className="header-actions">
        <LanguageSelect language={language} onChange={setLanguage}/>
        <Link className="btn btn-primary nav-launch" to="/assistant">
          {t.nav.tryAssistant} <ArrowUpRight size={17}/>
        </Link>
        <button className="menu-button" type="button" aria-label="Toggle menu" onClick={() => setMenuOpen(x => !x)}>
          {menuOpen ? <X/> : <Menu/>}
        </button>
      </div>
    </div>
  </header>;
}
