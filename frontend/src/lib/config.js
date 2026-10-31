import { UI_TRANSLATIONS, getUITranslations } from './translations';

export { UI_TRANSLATIONS, getUITranslations };

export const LANGUAGES = [
  { code: 'en-IN', label: 'English', english: 'English', preview: true },
  { code: 'te-IN', label: 'తెలుగు', english: 'Telugu', preview: true },
  { code: 'hi-IN', label: 'हिन्दी', english: 'Hindi' },
  { code: 'ta-IN', label: 'தமிழ்', english: 'Tamil' },
  { code: 'kn-IN', label: 'ಕನ್ನಡ', english: 'Kannada' },
  { code: 'ml-IN', label: 'മലയാളം', english: 'Malayalam' },
  { code: 'mr-IN', label: 'मराठी', english: 'Marathi' },
  { code: 'bn-IN', label: 'বাংলা', english: 'Bengali' },
  { code: 'gu-IN', label: 'ગુજરાતી', english: 'Gujarati' },
  { code: 'pa-IN', label: 'ਪੰਜਾਬੀ', english: 'Punjabi' },
];

export const DEMO_PROMPTS = [
  {
    id: 'cotton',
    icon: 'leaf',
    title: 'Cotton pest problem',
    detail: 'There are insects on my cotton leaves. What should I check?',
    telugu: 'నా పత్తి పంట ఆకులపై పురుగులు కనిపిస్తున్నాయి. ఏం చూడాలి?',
    translations: {
      'te-IN': { title: 'పత్తి పురుగుల సమస్య', query: 'నా పత్తి పంట ఆకులపై పురుగులు కనిపిస్తున్నాయి. ఏం చూడాలి?' },
      'en-IN': { title: 'Cotton pest problem', query: 'There are insects on my cotton leaves. What should I check?' },
      'hi-IN': { title: 'कपास में कीट की समस्या', query: 'मेरी कपास की फसल की पत्तियों पर कीड़े दिखाई दे रहे हैं। मुझे क्या करना चाहिए?' },
      'ta-IN': { title: 'பருத்தி பூச்சி தாக்குதல்', query: 'எனது பருத்தி இலைகளில் பூச்சிகள் காணப்படுகின்றன. நான் என்ன செய்ய வேண்டும்?' },
      'kn-IN': { title: 'ಹತ್ತಿ ಕೀಟ ಸಮಸ್ಯೆ', query: 'ನನ್ನ ಹತ್ತಿ ಎಲೆಗಳ ಮೇಲೆ ಕೀಟಗಳು ಕಾಣಿಸುತ್ತಿವೆ. ನಾನು ಏನು ಪರಿಶೀಲಿಸಬೇಕು?' },
      'ml-IN': { title: 'പരുത്തിയിലെ കീടബാധ', query: 'എന്റെ പരുത്തി ഇലകളിൽ പ്രാണികളെ കാണുന്നു. ഞാൻ എന്താണ് പരിശോധിക്കേണ്ടത്?' },
      'mr-IN': { title: 'कपाशीवरील कीड समस्या', query: 'माझ्या कपाशीच्या पानांवर कीड दिसत आहे. मी काय उपाययोजना करावी?' },
      'bn-IN': { title: 'তুলা ফসলে পোকার আক্রমণ', query: 'আমার তুলা গাছের পাতায় পোকা দেখা যাচ্ছে। আমার কী করণীয়?' },
      'gu-IN': { title: 'કપાસમાં જીવાત સમસ્યા', query: 'મારા કપાસના પાંદડા પર જીવાત દેખાય છે. મારે શું કરવું જોઈએ?' },
      'pa-IN': { title: 'ਨਰਮੇ ਵਿੱਚ ਕੀੜਿਆਂ ਦੀ ਸਮੱਸਿਆ', query: 'ਮੇਰੇ ਨਰਮੇ ਦੇ ਪੱਤਿਆਂ \'ਤੇ ਕੀੜੇ ਦਿਖ ਰਹੇ ਹਨ। ਮੈਨੂੰ ਕੀ ਜਾਂਚ ਕਰਨੀ ਚਾਹੀਦੀ ਹੈ?' },
    }
  },
  {
    id: 'tomatoes',
    icon: 'sprout',
    title: 'Growing tomatoes',
    detail: 'I want to start growing tomatoes. What should I prepare?',
    telugu: 'నేను టమాటా పండించాలనుకుంటున్నాను. ఎలా మొదలుపెట్టాలి?',
    translations: {
      'te-IN': { title: 'టమాటా సాగు విధానం', query: 'నేను టమాటా పండించాలనుకుంటున్నాను. ఎలా మొదలుపెట్టాలి?' },
      'en-IN': { title: 'Growing tomatoes', query: 'I want to start growing tomatoes. What should I prepare?' },
      'hi-IN': { title: 'टमाटर की खेती', query: 'मैं टमाटर की खेती शुरू करना चाहता हूँ। मुझे क्या तैयारी करनी चाहिए?' },
      'ta-IN': { title: 'தக்காளி சாகுபடி', query: 'நான் தக்காளி பயிரிட விரும்புகிறேன். என்ன ஏற்பாடுகளை செய்ய வேண்டும்?' },
      'kn-IN': { title: 'ಟೊಮ್ಯಾಟೊ ಕೃಷಿ', query: 'ನಾನು ಟೊಮ್ಯಾಟೊ ಬೆಳೆಯಲು ಬಯಸುತ್ತೇನೆ. ಯಾವ ಸಿದ್ಧತೆಗಳನ್ನು ಮಾಡಿಕೊಳ್ಳಬೇಕು?' },
      'ml-IN': { title: 'തക്കാളി കൃഷി', query: 'എനിക്ക് തക്കാളി കൃഷി തുടങ്ങണം. എന്തൊക്കെ ഒരുക്കങ്ങൾ നടത്തണം?' },
      'mr-IN': { title: 'टोमॅटो लागवड', query: 'मला टोमॅटोची लागवड सुरू करायची आहे. मी काय तयारी करावी?' },
      'bn-IN': { title: 'টমেটো চাষের পদ্ধতি', query: 'আমি টমেটো চাষ শুরু করতে চাই। কীভাবে শুরু করব?' },
      'gu-IN': { title: 'ટામેટાની ખેતી', query: 'હું ટામેટાની ખેતી શરૂ કરવા માંગુ છું. મારે શું તૈયારી કરવી જોઈએ?' },
      'pa-IN': { title: 'ਟਮਾਟਰਾਂ ਦੀ ਕਾਸ਼ਤ', query: 'ਮੈਂ ਟਮਾਟਰਾਂ ਦੀ ਕਾਸ਼ਤ ਸ਼ੁਰੂ ਕਰਨਾ ਚਾਹੁੰਦਾ ਹਾਂ। ਮੈਨੂੰ ਕੀ ਤਿਆਰੀ ਕਰਨੀ ਚਾਹੀਦੀ ਹੈ?' },
    }
  },
  {
    id: 'maize',
    icon: 'droplets',
    title: 'Maize irrigation',
    detail: 'How should I manage irrigation for my maize crop?',
    telugu: 'నా మొక్కజొన్న పంటకు నీరు ఎలా పెట్టాలి?',
    translations: {
      'te-IN': { title: 'మొక్కజొన్న నీటి యాజమాన్యం', query: 'నా మొక్కజొన్న పంటకు నీరు ఎలా పెట్టాలి?' },
      'en-IN': { title: 'Maize irrigation', query: 'How should I manage irrigation for my maize crop?' },
      'hi-IN': { title: 'मक्का में सिंचाई प्रबंधन', query: 'मेरी मक्के की फसल के लिए सिंचाई का प्रबंधन कैसे करना चाहिए?' },
      'ta-IN': { title: 'மக்காச்சோள பாசனம்', query: 'எனது மக்காச்சோளப் பயிருக்கு பாசன மேலாண்மை எவ்வாறு செய்ய வேண்டும்?' },
      'kn-IN': { title: 'ಮೆಕ್ಕೆಜೋಳ ನೀರಾವರಿ', query: 'ನನ್ನ ಮೆಕ್ಕೆಜೋಳ ಬೆಳೆಗೆ ನೀರಾವರಿ ಹೇಗೆ ನಿರ್ವಹಿಸಬೇಕು?' },
      'ml-IN': { title: 'മക്കച്ചോള നനയ്ക്കൽ', query: 'എന്റെ മക്കച്ചോള കൃഷിക്ക് ജലസೇചനം എങ്ങനെ നടത്തണം?' },
      'mr-IN': { title: 'मका पाणी व्यवस्थापन', query: 'माझ्या मका पिकासाठी पाणी व्यवस्थापन कसे करावे?' },
      'bn-IN': { title: 'ভুট্টায় সেচ ব্যবস্থাপনা', query: 'আমার ভুট্টা ফসলে সেচ কীভাবে পরিচালনা করা উচিত?' },
      'gu-IN': { title: 'મકાઈમાં પિયત વ્યવસ્થા', query: 'મારા મકાઈના પાક માટે પિયત વ્યવસ્થાપન કેવી રીતે કરવું?' },
      'pa-IN': { title: 'ਮੱਕੀ ਦੀ ਸਿੰਚਾਈ', query: 'ਮੇਰੀ ਮੱਕੀ ਦੀ ਫ਼ਸਲ ਲਈ ਸਿੰਚਾਈ ਦਾ ਪ੍ਰਬੰਧ ਕਿਵੇਂ ਕਰਨਾ ਚਾਹੀਦਾ ਹੈ?' },
    }
  },
  {
    id: 'banana',
    icon: 'sprout',
    title: 'Banana fertilizer',
    detail: 'What should I know before applying fertilizer to banana plants?',
    telugu: 'అరటి పంటకు ఎరువులు వేసే ముందు ఏం తెలుసుకోవాలి?',
    translations: {
      'te-IN': { title: 'అరటి ఎరువుల యాజమాన్యం', query: 'అరటి పంటకు ఎరువులు వేసే ముందు ఏం తెలుసుకోవాలి?' },
      'en-IN': { title: 'Banana fertilizer', query: 'What should I know before applying fertilizer to banana plants?' },
      'hi-IN': { title: 'केले के लिए उर्वरक', query: 'केले की फसल में खाद डालने से पहले मुझे क्या बातें ध्यान में रखनी चाहिए?' },
      'ta-IN': { title: 'வாழை உர மேலாண்மை', query: 'வாழை மரங்களுக்கு உரம் போடுவதற்கு முன் என்ன தெரிந்து கொள்ள வேண்டும்?' },
      'kn-IN': { title: 'ಬಾಳೆ ಗೊಬ್ಬರ ನಿರ್ವಹಣೆ', query: 'ಬಾಳೆ ಬೆಳೆಗೆ ಗೊಬ್ಬರ ಹಾಕುವ ಮೊದಲು ಏನು ತಿಳಿದುಕೊಳ್ಳಬೇಕು?' },
      'ml-IN': { title: 'വാഴ വളപ്രയോഗം', query: 'വാഴയ്ക്ക് വളം ചേർക്കുന്നതിന് മുൻപ് എന്തൊക്കെ ശ്രദ്ധിക്കണം?' },
      'mr-IN': { title: 'केळी खत व्यवस्थापन', query: 'केळी पिकाला खत देण्यापूर्वी मी काय गोष्टी लक्षात ठेवाव्यात?' },
      'bn-IN': { title: 'কলা গাছে সার প্রয়োগ', query: 'কলা গাছে সার দেওয়ার আগে কী জানা জরুরি?' },
      'gu-IN': { title: 'કેળ ખાતર વ્યવસ્થાપન', query: 'કેળના પાકમાં ખાતર આપતાં પહેલાં મારે શું ધ્યાનમાં રાખવું જોઈએ?' },
      'pa-IN': { title: 'ਕੇਲੇ ਲਈ ਖਾਦ ਪ੍ਰਬੰਧਨ', query: 'ਕੇਲੇ ਦੀ ਫ਼ਸਲ ਨੂੰ ਖਾਦ ਪਾਉਣ ਤੋਂ ਪਹਿਲਾਂ ਮੈਨੂੰ ਕਿਨ੍ਹਾਂ ਗੱਲਾਂ ਦਾ ਧਿਆਨ ਰੱਖਣਾ ਚਾਹੀਦੀ ਹੈ?' },
    }
  },
  {
    id: 'paddy',
    icon: 'leaf',
    title: 'Paddy leaf yellowing',
    detail: 'Why are my paddy leaves turning yellow? What should I do?',
    telugu: 'నా వరి ఆకులు పసుపు రంగులోకి మారుతున్నాయి. ఏం చేయాలి?',
    translations: {
      'te-IN': { title: 'వరి ఆకులు పసుపు రంగు', query: 'నా వరి ఆకులు పసుపు రంగులోకి మారుతున్నాయి. ఏం చేయాలి?' },
      'en-IN': { title: 'Paddy leaf yellowing', query: 'Why are my paddy leaves turning yellow? What should I do?' },
      'hi-IN': { title: 'धान में पत्तियां पीली पड़ना', query: 'मेरी धान की पत्तियां पीली पड़ रही हैं। मुझे क्या उपाय करना चाहिए?' },
      'ta-IN': { title: 'நெல் இலை மஞ்சள் நிறமாதல்', query: 'எனது நெல் பயிரின் இலைகள் மஞ்சளாக மாறுகின்றன. என்ன செய்ய வேண்டும்?' },
      'kn-IN': { title: 'ಭತ್ತದ ಎಲೆ ಹಳದಿ ಬಣ್ಣ', query: 'ನನ್ನ ಭತ್ತದ ಎಲೆಗಳು ಹಳದಿ ಬಣ್ಣಕ್ಕೆ ತಿರುಗುತ್ತಿವೆ. ಏನು ಮಾಡಬೇಕು?' },
      'ml-IN': { title: 'നെൽച്ചെടിയുടെ ഇല മഞ്ഞളിക്കൽ', query: 'എന്റെ നെല്ലിന്റെ ഇലകൾ മഞ്ഞനിറമാകുന്നു. ഞാൻ എന്ത് ചെയ്യണം?' },
      'mr-IN': { title: 'भात पाने पिवळी पडणे', query: 'माझ्या भाताची पाने पिवळी पडत आहेत. मी काय उपाय करावा?' },
      'bn-IN': { title: 'ধানের পাতা হলুদ হওয়া', query: 'আমার ধান গাছের পাতা হলুদ হয়ে যাচ্ছে। প্রতিকার কী?' },
      'gu-IN': { title: 'ડાંગરના પાન પીળા પડવા', query: 'મારા ડાંગરના પાન પીળા પડી રહ્યા છે. મારે શું ઉપાય કરવો?' },
      'pa-IN': { title: 'ਝੋਨੇ ਦੇ ਪੱਤੇ ਪੀਲੇ ਹੋਣਾ', query: 'ਮੇਰੇ ਝੋਨੇ ਦੇ ਪੱਤੇ ਪੀਲੇ ਹੋ ਰਹੇ ਹਨ। ਮੈਨੂੰ ਕੀ ਇਲਾਜ ਕਰਨਾ ਚਾਹੀਦਾ ਹੈ?' },
    }
  },
  {
    id: 'climate',
    icon: 'sprout',
    title: 'Crop climate & season',
    detail: 'What is the ideal climate, temperature range, and season for growing paddy?',
    telugu: 'వరి పంట సాగుకు అనుకూలమైన వాతావరణం, ఉష్ణోగ్రత మరియు ఏ కాలం (ఖరీఫ్/రబీ) ఉత్తమం?',
    translations: {
      'te-IN': { title: 'వరి సాగుకు వాతావరణం', query: 'వరి పంట సాగుకు అనుకూలమైన వాతావరణం, ఉష్ణోగ్రత మరియు ఏ కాలం (ఖరీఫ్/రబీ) ఉత్తమం?' },
      'en-IN': { title: 'Crop climate & season', query: 'What is the ideal climate, temperature range, and season for growing paddy?' },
      'hi-IN': { title: 'धान के लिए उपयुक्त मौसम', query: 'धान की फसल के लिए आदर्श जलवायु, तापमान और कौन सा मौसम (खरीफ/रबी) सबसे अच्छा है?' },
      'ta-IN': { title: 'பயிருக்கான பருவநிலை', query: 'நெல் சாகுபடிக்கு உகந்த தட்பவெப்பநிலை, வெப்பநிலை மற்றும் ஏற்ற பருவம் எது?' },
      'kn-IN': { title: 'ಬೆಳೆಗೆ ಸೂಕ್ತ ಹವಾಮಾನ', query: 'ಭತ್ತದ ಬೆಳೆ ಬೆಳೆಯಲು ಸೂಕ್ತವಾದ ಹವಾಮಾನ, ತಾಪಮಾನ ಮತ್ತು ಕಾಲ ಯಾವುದು?' },
      'ml-IN': { title: 'അനുയോജ്യമായ കാലാവസ്ഥ', query: 'നെൽകൃഷിക്ക് ആവശ്യമായ അനുയോജ്യമായ കാലാവസ്ഥയും താപനിലയും ഏതാണ്?' },
      'mr-IN': { title: 'पिकासाठी अनुकूल हवामान', query: 'भात पिकासाठी अनुकूल हवामान, तापमान आणि कोणता हंगाम योग्य आहे?' },
      'bn-IN': { title: 'উপযুক্ত আবহাওয়া ও মরশুম', query: 'ধান চাষের জন্য উপযুক্ত আবহাওয়া, তাপমাত্রা এবং কোন মরশুম সবচেয়ে ভালো?' },
      'gu-IN': { title: 'પાક માટે અનુકૂળ આબોહવા', query: 'ડાંગરના પાક માટે અનુકૂળ આબોહવા, તાપમાન અને કઈ ઋતુ સૌથી શ્રેષ્ઠ છે?' },
      'pa-IN': { title: 'ਫ਼ਸਲ ਲਈ ਅਨੁਕੂਲ ਮੌਸਮ', query: 'ਝੋਨੇ ਦੀ ਕਾਸ਼ਤ ਲਈ ਢੁਕਵਾਂ ਮੌਸਮ, ਤਾਪਮਾਨ ਅਤੇ ਕਿਹੜਾ ਸੀਜ਼ਨ ਸਭ ਤੋਂ ਵਧੀਆ ਹੈ?' },
    }
  },
];

export const SECTION_LABELS = Object.fromEntries(
  Object.entries(UI_TRANSLATIONS).map(([code, trans]) => [code, trans.assistant])
);

export function getLocalizedPrompts(langCode = 'en-IN') {
  return DEMO_PROMPTS.map(p => {
    const loc = p.translations?.[langCode] || p.translations?.['en-IN'] || {};
    return {
      ...p,
      title: loc.title || p.title,
      query: loc.query || (langCode === 'te-IN' ? p.telugu : p.detail),
      icon: p.icon,
    };
  });
}

