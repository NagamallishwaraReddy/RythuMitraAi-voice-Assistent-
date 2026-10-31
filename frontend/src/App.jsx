import { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Assistant from './pages/Assistant';

export default function App() {
  const [language, setLanguageState] = useState(() => {
    try {
      return localStorage.getItem('rythumitra_language') || 'en-IN';
    } catch {
      return 'en-IN';
    }
  });

  const setLanguage = (newLang) => {
    setLanguageState(newLang);
    try {
      localStorage.setItem('rythumitra_language', newLang);
    } catch {
      // ignore
    }
  };

  return <Routes>
    <Route path="/" element={<Home language={language} setLanguage={setLanguage}/>}/>
    <Route path="/assistant" element={<Assistant language={language} setLanguage={setLanguage}/>}/>
    <Route path="*" element={<Home language={language} setLanguage={setLanguage}/>}/>
  </Routes>;
}
