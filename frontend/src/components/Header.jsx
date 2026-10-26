import { Link, NavLink } from 'react-router-dom';
import { ArrowUpRight, Menu, X } from 'lucide-react';
import { useState } from 'react';
import Logo from './Logo';
import LanguageSelect from './LanguageSelect';

export default function Header({ language, setLanguage }) {
  const [menuOpen, setMenuOpen] = useState(false);
  return <header className="site-header">
    <div className="header-inner container">
      <Logo />
      <nav className={menuOpen ? 'site-nav open' : 'site-nav'} aria-label="Primary navigation">
        <NavLink to="/" end onClick={() => setMenuOpen(false)}>Home</NavLink>
        <a href="/#how-it-works" onClick={() => setMenuOpen(false)}>How it works</a>
        <a href="/#benefits" onClick={() => setMenuOpen(false)}>Features</a>
        <NavLink to="/assistant" onClick={() => setMenuOpen(false)}>Voice assistant</NavLink>
      </nav>
      <div className="header-actions">
        <LanguageSelect language={language} onChange={setLanguage}/>
        <Link className="btn btn-primary nav-launch" to="/assistant">Try the assistant <ArrowUpRight size={17}/></Link>
        <button className="menu-button" type="button" aria-label="Toggle menu" onClick={() => setMenuOpen(x => !x)}>{menuOpen ? <X/> : <Menu/>}</button>
      </div>
    </div>
  </header>;
}
