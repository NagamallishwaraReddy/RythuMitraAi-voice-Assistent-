import { Link } from 'react-router-dom';
import { ArrowRight, AudioLines, BrainCircuit, CheckCircle2, ChevronRight, ExternalLink, Headphones, Languages, Leaf, Mic2, PhoneCall, ShieldCheck, Sparkles, Sprout, Volume2, Waves } from 'lucide-react';
import Header from '../components/Header';
import Logo from '../components/Logo';

export default function Home({ language, setLanguage }) {
  return <div className="home-page">
    <Header language={language} setLanguage={setLanguage}/>
    <main>
      <section className="hero container">
        <div className="hero-copy">
          <div className="eyebrow"><span className="eyebrow-dot"/><Sparkles size={14}/> AI-powered guidance, made for farmers</div>
          <h1>Your voice.<br/>Your crops.<br/><span>Better harvests.</span></h1>
          <p>Meet your farming companion. Ask about any crop, climate and temperature needs, seasonal planning, pests, and irrigation — and get direct guidance in voice and text.</p>
          <div className="hero-cta-row">
            <Link to="/assistant" className="btn btn-primary btn-large"><Mic2 size={21}/> Start talking with RythuMitra <ArrowRight size={18}/></Link>
            <a href="#how-it-works" className="text-link">See how it works <ChevronRight size={17}/></a>
          </div>
          <div className="hero-trust"><div><CheckCircle2 size={18}/> Voice-first experience</div><div><CheckCircle2 size={18}/> Crop & Climate Guidance</div><div><CheckCircle2 size={18}/> Your language</div></div>
        </div>
        <div className="hero-art" role="img" aria-label="A farmer in his field using a smartphone">
          <div className="hero-picture"/>
          <div className="hero-art-shine"/>
          <div className="hero-chat-note hero-chat-note-top"><span className="note-icon"><Mic2 size={18}/></span><span>వరి సాగుకు ఎలాంటి వాతావరణం<br/>అనుకూలంగా ఉంటుంది?</span></div>
          <div className="hero-chat-note hero-chat-note-bottom"><span className="note-icon solid"><Sprout size={18}/></span><div>20°C - 35°C ఉష్ణోగ్రత, ఖరీఫ్ సీజన్ ఉత్తమం!<div className="note-waves"><span/><span/><span/><span/><span/><span/><span/><span/><span/><span/><span/></div></div></div>
          <div className="hero-corner-sticker"><Leaf size={18}/> Farming made simpler</div>
        </div>
      </section>
      <section id="benefits" className="features-section container">
        <div className="section-kicker">WHY RYTHUMITRA?</div>
        <h2>Farming advice, just a conversation away.</h2>
        <p className="section-intro">Built around the way farmers actually ask questions — through simple spoken conversations.</p>
        <div className="feature-grid">
          <article className="feature-card"><span className="feature-icon green"><Mic2 size={28}/></span><h3>Speak naturally</h3><p>Use your voice instead of filling out long forms. Ask about the crop problem or weather you're facing.</p><span className="feature-footer"><AudioLines size={16}/> Speech recognition integration ready</span></article>
          <article className="feature-card"><span className="feature-icon gold"><BrainCircuit size={28}/></span><h3>Crop & Climate Guidance</h3><p>Ask about ideal temperature, season windows (Kharif/Rabi), irrigation, leaf symptoms, and preparation.</p><span className="feature-footer"><ShieldCheck size={16}/> Direct university-backed advice</span></article>
          <article className="feature-card"><span className="feature-icon blue"><Headphones size={28}/></span><h3>Listen and read</h3><p>Hear an answer in your selected language and see the same explanation as readable text.</p><span className="feature-footer"><Volume2 size={16}/> Spoken replies integration ready</span></article>
        </div>
      </section>
      <section id="how-it-works" className="how-section">
        <div className="container how-inner">
          <div className="how-header"><span className="section-kicker">THREE SIMPLE STEPS</span><h2>Growing good crops starts<br/>with a good question.</h2></div>
          <div className="steps-grid">
            <div className="step-card"><span className="step-number">01</span><span className="step-icon"><Mic2 size={31}/></span><h3>You ask</h3><p>Talk about your crop in a language you are comfortable speaking.</p></div>
            <div className="step-arrow"><ArrowRight size={24}/></div>
            <div className="step-card"><span className="step-number">02</span><span className="step-icon"><BrainCircuit size={31}/></span><h3>RythuMitra understands</h3><p>The assistant follows up and uses relevant agricultural information.</p></div>
            <div className="step-arrow"><ArrowRight size={24}/></div>
            <div className="step-card"><span className="step-number">03</span><span className="step-icon"><Volume2 size={31}/></span><h3>Get voice and text</h3><p>Read the answer, listen to it, and ask your next question.</p></div>
          </div>
        </div>
      </section>
      <section className="bottom-cta container"><div><span className="section-kicker">YOUR FIELD, YOUR QUESTIONS</span><h2>Let's grow smarter, together.</h2><p>Start with one simple farming question.</p></div><Link className="btn btn-light btn-large" to="/assistant"><Mic2 size={21}/> Start a conversation <ArrowRight size={19}/></Link></section>
    </main>
    <footer className="portal-footer">
      <div className="container footer-main-grid">
        <div className="footer-col footer-col-brand">
          <Logo />
          <p className="footer-mission">
            RythuMitra AI is an intelligent, voice-first agricultural companion designed specifically for farmers. Delivering direct diagnostic answers, chemical dosages, organic alternatives, and crop protection in your own mother tongue.
          </p>
          <div className="tech-stack-pills">
            <span className="tech-pill"><Sparkles size={13}/> Gemini AI</span>
            <span className="tech-pill"><Mic2 size={13}/> Gnani Prisma STT</span>
            <span className="tech-pill"><Volume2 size={13}/> Gnani Timbre TTS</span>
          </div>
        </div>

        <div className="footer-col">
          <h4 className="footer-heading">Quick Navigation</h4>
          <ul className="footer-links">
            <li><Link to="/"><ChevronRight size={14}/> Home</Link></li>
            <li><Link to="/assistant"><ChevronRight size={14}/> AI Voice Assistant</Link></li>
            <li><a href="#benefits"><ChevronRight size={14}/> Features & Benefits</a></li>
            <li><a href="#how-it-works"><ChevronRight size={14}/> How It Works</a></li>
          </ul>
        </div>

        <div className="footer-col">
          <h4 className="footer-heading">Crops & Solutions</h4>
          <div className="footer-crop-tags">
            <span className="crop-tag"><Sprout size={13}/> Paddy (వరి / धान)</span>
            <span className="crop-tag"><Leaf size={13}/> Cotton (పత్తి / कपास)</span>
            <span className="crop-tag"><Sprout size={13}/> Tomato (టమాటా / टमाटर)</span>
            <span className="crop-tag"><Leaf size={13}/> Maize (మొక్కజొన్న / मक्का)</span>
            <span className="crop-tag"><Sprout size={13}/> Banana (అరటి / केला)</span>
            <span className="crop-tag"><Leaf size={13}/> Chilli (మిరప / मिर्च)</span>
          </div>
          <p className="crop-note">Ask direct questions about pest attacks, dosage, irrigation, or soil nutrients.</p>
        </div>

        <div className="footer-col">
          <h4 className="footer-heading">Farmer Helplines</h4>
          <div className="helpline-card">
            <span className="helpline-icon"><PhoneCall size={20}/></span>
            <div>
              <span className="helpline-title">Kisan Call Center</span>
              <strong className="helpline-number">1800-180-1551</strong>
              <span className="helpline-time">24x7 Toll-Free Farmer Support</span>
            </div>
          </div>
          <div className="gov-links">
            <a href="https://icar.org.in" target="_blank" rel="noopener noreferrer">
              <ExternalLink size={12}/> ICAR Research Portal
            </a>
            <a href="https://agricoop.gov.in" target="_blank" rel="noopener noreferrer">
              <ExternalLink size={12}/> Ministry of Agriculture
            </a>
            <a href="https://soilhealth.dac.gov.in" target="_blank" rel="noopener noreferrer">
              <ExternalLink size={12}/> Soil Health Card Scheme
            </a>
          </div>
        </div>
      </div>

      <div className="footer-divider container"/>

      <div className="container footer-bottom-bar">
        <div className="footer-bottom-copy">
          <span>© 2026 <strong>RythuMitra AI</strong> · Built for Indian Farmers</span>
          <span className="bottom-tagline">Empowering every grower with instant, trustworthy agronomic intelligence.</span>
        </div>
        <div className="footer-lang-list">
          <span className="lang-label"><Languages size={15}/> 10 Regional Languages:</span>
          <div className="footer-langs-inline">
            <span>తెలుగు</span> · <span>English</span> · <span>हिन्दी</span> · <span>தமிழ்</span> · <span>ಕನ್ನಡ</span> · <span>മലയാളം</span> · <span>मराठी</span> · <span>বাংলা</span> · <span>ગુજરાતી</span> · <span>ਪੰਜਾਬੀ</span>
          </div>
        </div>
      </div>
    </footer>
  </div>;
}
