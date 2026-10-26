import { Link } from 'react-router-dom';
import { ArrowRight, AudioLines, BrainCircuit, CheckCircle2, ChevronRight, Headphones, Languages, Leaf, Mic2, ShieldCheck, Sparkles, Sprout, Volume2, Waves } from 'lucide-react';
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
          <p>Meet your farming companion. Ask about any crop, including vegetables, fruits, grains, pests and irrigation — and get simple guidance in voice and text.</p>
          <div className="hero-cta-row">
            <Link to="/assistant" className="btn btn-primary btn-large"><Mic2 size={21}/> Start talking with RythuMitra <ArrowRight size={18}/></Link>
            <a href="#how-it-works" className="text-link">See how it works <ChevronRight size={17}/></a>
          </div>
          <div className="hero-trust"><div><CheckCircle2 size={18}/> Voice-first experience</div><div><CheckCircle2 size={18}/> Crop-focused questions</div><div><CheckCircle2 size={18}/> Your language</div></div>
        </div>
        <div className="hero-art" role="img" aria-label="A farmer in his field using a smartphone">
          <div className="hero-picture"/>
          <div className="hero-art-shine"/>
          <div className="hero-chat-note hero-chat-note-top"><span className="note-icon"><Mic2 size={18}/></span><span>నా టమాటా ఆకులు పసుపుగా<br/>మారుతున్నాయి...</span></div>
          <div className="hero-chat-note hero-chat-note-bottom"><span className="note-icon solid"><Sprout size={18}/></span><div>నేను సహాయం చేస్తాను!<div className="note-waves"><span/><span/><span/><span/><span/><span/><span/><span/><span/><span/><span/></div></div></div>
          <div className="hero-corner-sticker"><Leaf size={18}/> Farming made simpler</div>
        </div>
      </section>
      <section id="benefits" className="features-section container">
        <div className="section-kicker">WHY RYTHUMITRA?</div>
        <h2>Farming advice, just a conversation away.</h2>
        <p className="section-intro">Built around the way farmers actually ask questions — through simple spoken conversations.</p>
        <div className="feature-grid">
          <article className="feature-card"><span className="feature-icon green"><Mic2 size={28}/></span><h3>Speak naturally</h3><p>Use your voice instead of filling out long forms. Ask about the crop problem you're facing.</p><span className="feature-footer"><AudioLines size={16}/> Speech recognition integration ready</span></article>
          <article className="feature-card"><span className="feature-icon gold"><BrainCircuit size={28}/></span><h3>Helpful crop guidance</h3><p>Ask about irrigation, leaf symptoms, crop stages and preparation. Get clear follow-up questions.</p><span className="feature-footer"><ShieldCheck size={16}/> Source-backed advice planned</span></article>
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
    <footer className="site-footer container"><div><Logo compact/><span>Made for farmer-friendly conversations.</span></div><small>Prototype mode · Gnani speech and LLM integrations are the next phase.</small></footer>
  </div>;
}
