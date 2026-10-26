import { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Assistant from './pages/Assistant';

export default function App() {
  const [language, setLanguage] = useState('te-IN');
  return <Routes>
    <Route path="/" element={<Home language={language} setLanguage={setLanguage}/>}/>
    <Route path="/assistant" element={<Assistant language={language} setLanguage={setLanguage}/>}/>
    <Route path="*" element={<Home language={language} setLanguage={setLanguage}/>}/>
  </Routes>;
}
