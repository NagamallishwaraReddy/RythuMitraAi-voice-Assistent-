import { Link } from 'react-router-dom';
import { ArrowRight, AudioLines, BrainCircuit, CheckCircle2, ChevronRight, ExternalLink, Headphones, Languages, Leaf, Mic2, PhoneCall, ShieldCheck, Sparkles, Sprout, Volume2 } from 'lucide-react';
import Header from '../components/Header';
import Logo from '../components/Logo';
import { getUITranslations } from '../lib/config';

export default function Home({ language, setLanguage }) {
  const t = getUITranslations(language);

  return <div className="home-page">
    <Header language={language} setLanguage={setLanguage}/>
    <main>
      <section className="hero container">
        <div className="hero-copy">
          <div className="eyebrow"><span className="eyebrow-dot"/><Sparkles size={14}/> {t.hero.eyebrow}</div>
          <h1>{t.hero.title1}<br/>{t.hero.title2}<br/><span>{t.hero.title3}</span></h1>
          <p>{t.hero.desc}</p>
          <div className="hero-cta-row">
            <Link to="/assistant" className="btn btn-primary btn-large">
              <Mic2 size={21}/> {t.hero.startTalking} <ArrowRight size={18}/>
            </Link>
            <a href="#how-it-works" className="text-link">
              {t.hero.seeHowItWorks} <ChevronRight size={17}/>
            </a>
          </div>
          <div className="hero-trust">
            <div><CheckCircle2 size={18}/> {t.hero.trustVoice}</div>
            <div><CheckCircle2 size={18}/> {t.hero.trustClimate}</div>
            <div><CheckCircle2 size={18}/> {t.hero.trustLang}</div>
          </div>
        </div>
        <div className="hero-art" role="img" aria-label="A farmer in his field using a smartphone">
          <div className="hero-picture"/>
          <div className="hero-art-shine"/>
          <div className="hero-chat-note hero-chat-note-top">
            <span className="note-icon"><Mic2 size={18}/></span>
            <span>{t.hero.chatNoteQ}</span>
          </div>
          <div className="hero-chat-note hero-chat-note-bottom">
            <span className="note-icon solid"><Sprout size={18}/></span>
            <div>
              {t.hero.chatNoteA}
              <div className="note-waves"><span/><span/><span/><span/><span/><span/><span/><span/><span/><span/><span/></div>
            </div>
          </div>
          <div className="hero-corner-sticker"><Leaf size={18}/> {t.hero.sticker}</div>
        </div>
      </section>

      <section id="benefits" className="features-section container">
        <div className="section-kicker">{t.features.kicker}</div>
        <h2>{t.features.heading}</h2>
        <p className="section-intro">{t.features.intro}</p>
        <div className="feature-grid">
          <article className="feature-card">
            <span className="feature-icon green"><Mic2 size={28}/></span>
            <h3>{t.features.f1Title}</h3>
            <p>{t.features.f1Desc}</p>
            <span className="feature-footer"><AudioLines size={16}/> {t.features.f1Foot}</span>
          </article>
          <article className="feature-card">
            <span className="feature-icon gold"><BrainCircuit size={28}/></span>
            <h3>{t.features.f2Title}</h3>
            <p>{t.features.f2Desc}</p>
            <span className="feature-footer"><ShieldCheck size={16}/> {t.features.f2Foot}</span>
          </article>
          <article className="feature-card">
            <span className="feature-icon blue"><Headphones size={28}/></span>
            <h3>{t.features.f3Title}</h3>
            <p>{t.features.f3Desc}</p>
            <span className="feature-footer"><Volume2 size={16}/> {t.features.f3Foot}</span>
          </article>
        </div>
      </section>

      <section id="how-it-works" className="how-section">
        <div className="container how-inner">
          <div className="how-header">
            <span className="section-kicker">{t.howItWorks.kicker}</span>
            <h2>{t.howItWorks.heading1}<br/>{t.howItWorks.heading2}</h2>
          </div>
          <div className="steps-grid">
            <div className="step-card">
              <span className="step-number">{t.howItWorks.s1Num}</span>
              <span className="step-icon"><Mic2 size={31}/></span>
              <h3>{t.howItWorks.s1Title}</h3>
              <p>{t.howItWorks.s1Desc}</p>
            </div>
            <div className="step-arrow"><ArrowRight size={24}/></div>
            <div className="step-card">
              <span className="step-number">{t.howItWorks.s2Num}</span>
              <span className="step-icon"><BrainCircuit size={31}/></span>
              <h3>{t.howItWorks.s2Title}</h3>
              <p>{t.howItWorks.s2Desc}</p>
            </div>
            <div className="step-arrow"><ArrowRight size={24}/></div>
            <div className="step-card">
              <span className="step-number">{t.howItWorks.s3Num}</span>
              <span className="step-icon"><Volume2 size={31}/></span>
              <h3>{t.howItWorks.s3Title}</h3>
              <p>{t.howItWorks.s3Desc}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="bottom-cta container">
        <div>
          <span className="section-kicker">{t.bottomCta.kicker}</span>
          <h2>{t.bottomCta.heading}</h2>
          <p>{t.bottomCta.sub}</p>
        </div>
        <Link className="btn btn-light btn-large" to="/assistant">
          <Mic2 size={21}/> {t.bottomCta.button} <ArrowRight size={19}/>
        </Link>
      </section>
    </main>

    <footer className="portal-footer">
      <div className="container footer-main-grid">
        <div className="footer-col footer-col-brand">
          <Logo subtitle={t.assistant?.companionSub || 'Your farming companion'} />
          <p className="footer-mission">{t.footer.mission}</p>
          <div className="tech-stack-pills">
            <span className="tech-pill"><Sparkles size={13}/> Gemini AI</span>
            <span className="tech-pill"><Mic2 size={13}/> Gnani Prisma STT</span>
            <span className="tech-pill"><Volume2 size={13}/> Gnani Timbre TTS</span>
          </div>
        </div>

        <div className="footer-col">
          <h4 className="footer-heading">{t.footer.quickNav}</h4>
          <ul className="footer-links">
            <li><Link to="/"><ChevronRight size={14}/> {t.nav.home}</Link></li>
            <li><Link to="/assistant"><ChevronRight size={14}/> {t.nav.voiceAssistant}</Link></li>
            <li><a href="#benefits"><ChevronRight size={14}/> {t.nav.features}</a></li>
            <li><a href="#how-it-works"><ChevronRight size={14}/> {t.nav.howItWorks}</a></li>
          </ul>
        </div>

        <div className="footer-col">
          <h4 className="footer-heading">{t.footer.cropsSolutions}</h4>
          <div className="footer-crop-tags">
            <span className="crop-tag"><Sprout size={13}/> Paddy (వరి / धान)</span>
            <span className="crop-tag"><Leaf size={13}/> Cotton (పత్తి / कपास)</span>
            <span className="crop-tag"><Sprout size={13}/> Tomato (టమాటా / टमाटर)</span>
            <span className="crop-tag"><Leaf size={13}/> Maize (మొక్కజొన్న / मक्का)</span>
            <span className="crop-tag"><Sprout size={13}/> Banana (అరటి / केला)</span>
            <span className="crop-tag"><Leaf size={13}/> Chilli (మిరప / मिर्च)</span>
          </div>
          <p className="crop-note">{t.footer.cropNote}</p>
        </div>

        <div className="footer-col">
          <h4 className="footer-heading">{t.footer.helplineTitle}</h4>
          <div className="helpline-card">
            <span className="helpline-icon"><PhoneCall size={20}/></span>
            <div>
              <span className="helpline-title">{t.footer.kisanCenter}</span>
              <strong className="helpline-number">1800-180-1551</strong>
              <span className="helpline-time">{t.footer.tollFree}</span>
            </div>
          </div>
          <div className="gov-links">
            <a href="https://icar.org.in" target="_blank" rel="noopener noreferrer">
              <ExternalLink size={12}/> {t.footer.icarPortal}
            </a>
            <a href="https://agricoop.gov.in" target="_blank" rel="noopener noreferrer">
              <ExternalLink size={12}/> {t.footer.minAgri}
            </a>
            <a href="https://soilhealth.dac.gov.in" target="_blank" rel="noopener noreferrer">
              <ExternalLink size={12}/> {t.footer.soilHealth}
            </a>
          </div>
        </div>
      </div>

      <div className="footer-divider container"/>

      <div className="container footer-bottom-bar">
        <div className="footer-bottom-copy">
          <span>{t.footer.rights}</span>
          <span className="bottom-tagline">{t.footer.tagline}</span>
        </div>
        <div className="footer-lang-list">
          <span className="lang-label"><Languages size={15}/> {t.footer.regionalLangs}</span>
          <div className="footer-langs-inline">
            <span>తెలుగు</span> · <span>English</span> · <span>हिन्दी</span> · <span>தமிழ்</span> · <span>ಕನ್ನಡ</span> · <span>മലയാളം</span> · <span>मराठी</span> · <span>বাংলা</span> · <span>ગુજરાતી</span> · <span>ਪੰਜਾਬੀ</span>
          </div>
        </div>
      </div>
    </footer>
  </div>;
}
