"""Crop-independent *demo* conversation logic.

This lightweight router handles sample questions for many crop names and farming
issues. It is not a general-purpose language model or an agronomy knowledge
base. Replace it with a source-grounded reasoning agent in phase 2.
"""
from dataclasses import dataclass, field
import re


@dataclass(frozen=True)
class Advice:
    text: str
    topic: str
    suggestions: list[str]
    crop: str | None = None
    sources: list[dict[str, str]] = field(default_factory=list)


# Multilingual names for a *demo* routing layer, NOT a fixed list of crops
# the finished project may answer about. A reasoning model will handle
# unfamiliar crops and open-ended questions in phase 2.
CROP_ALIASES = {
    "paddy": ("paddy", "rice", "వరి", "धान", "चावल", "ಭತ್ತ", "நெல்"),
    "cotton": ("cotton", "పత్తి", "కపాస్", "कपास", "ಹತ್ತಿ", "பருத்தி"),
    "maize": ("maize", "corn", "మొక్కజొన్న", "मक्का", "मकई", "ಮೆಕ್ಕೆಜೋಳ", "மக்காச்சோளம்"),
    "tomato": ("tomato", "tomatoes", "టమాటా", "టొమాటో", "टमाटर", "ಟೊಮ್ಯಾಟೊ", "தக்காளி"),
    "chilli": ("chilli", "chili", "chillies", "chile", "మిరప", "మిర్చి", "मिर्च", "ಮೆಣಸಿನಕಾಯಿ", "மிளகாய்"),
    "wheat": ("wheat", "గోధుమ", "गेहूं", "ಗೋಧಿ", "கோதுமை"),
    "banana": ("banana", "plantain", "అరటి", "केला", "ಬಾಳೆ", "வாழை"),
    "groundnut": ("groundnut", "peanut", "peanuts", "వేరుశెనగ", "मूंगफली", "ಕಡಲೆಕಾಯಿ", "நிலக்கடலை"),
    "sugarcane": ("sugarcane", "sugar cane", "చెరకు", "गन्ना", "ಕಬ್ಬು", "கரும்பு"),
    "onion": ("onion", "onions", "ఉల్లి", "प्याज", "ಈರುಳ್ಳಿ", "வெங்காயம்"),
    "brinjal": ("brinjal", "eggplant", "aubergine", "వంకాయ", "बैंगन", "ಬದನೆಕಾಯಿ", "கத்திரிக்காய்"),
    "potato": ("potato", "potatoes", "బంగాళాదుంప", "आलू", "ಆಲೂಗಡ್ಡೆ", "உருளைக்கிழங்கு"),
    "mango": ("mango", "mangoes", "మామిడి", "आम", "ಮಾವು", "மாம்பழம்"),
    "coconut": ("coconut", "కొబ్బరి", "नारियल", "ತೆಂಗು", "தேங்காய்"),
    "turmeric": ("turmeric", "పసుపు పంట", "हल्दी", "ಅರಿಶಿನ", "மஞ்சள்"),
    "soybean": ("soybean", "soyabean", "సోయాబీన్", "सोयाबीन", "ಸೋಯಾಬೀನ್"),
    "millet": ("millet", "millets", "సజ్జ", "बाजरा", "ರಾಗಿ", "சிறுதானியம்"),
    "sunflower": ("sunflower", "పొద్దుతిరుగుడు", "सूरजमुखी", "ಸೂರ್ಯಕಾಂತಿ"),
}

TE_LABELS = {
    "paddy": "వరి", "cotton": "పత్తి", "maize": "మొక్కజొన్న", "tomato": "టమాటా",
    "chilli": "మిరప", "wheat": "గోధుమ", "banana": "అరటి", "groundnut": "వేరుశెనగ",
    "sugarcane": "చెరకు", "onion": "ఉల్లి", "brinjal": "వంకాయ", "potato": "బంగాళాదుంప",
    "mango": "మామిడి", "coconut": "కొబ్బరి", "turmeric": "పసుపు", "soybean": "సోయాబీన్",
    "millet": "సజ్జ", "sunflower": "పొద్దుతిరుగుడు",
}

TOPIC_TERMS = (
    ("yellow", ("పసుపుగా", "పసుపు రంగు", "పచ్చగా లేదు", "yellow", "yellowing", "पीले", "ಹಳದಿ", "மஞ்சள் நிற")),
    ("pest", ("పురుగు", "పురుగులు", "తెగులు", "పుళ్లు", "pest", "disease", "insect", "bug", "fungus", "spots", "blight", "कीट", "रोग", "ಹುಳು", "பூச்சி")),
    ("fertilizer", ("ఎరువు", "పోషక", "fertiliz", "fertilis", "urea", "compost", "manure", "nutrient", "खाद", "उर्वरक")),
    ("climate", ("వాతావరణం", "వాతావరణ", "శీతోష్ణస్థితి", "ఉష్ణోగ్రత", "చలి", "ఎండ", "ఋతువు", "వర్షపాతం", "ఖరీఫ్", "రబీ", "కాలం", "తుఫాను", "ఎండలు",
                 "climate", "weather", "temperature", "temp", "humidity", "rainfall", "season", "monsoon", "winter", "summer", "frost", "heat", "heatwave", "kharif", "rabi", "zaid",
                 "मौसम", "जलवायु", "तापमान", "वर्षा", "हवामान", "ಹವಾಮಾನ", "ಬೆಳೆ ಕಾಲ", "കാലാവസ്ഥ", "வானிலை", "பருவநிலை", "আবহাওয়া")),
    ("water", ("నీరు", "నీటి", "irrigat", "water", "watering", "వర్షం", "rain", "drainage", "पानी", "सिंचाई", "ನೀರು", "தண்ணீர்")),
    ("harvest", ("కోత", "పంట కోయ", "harvest", "maturity", "పక్వ", "कटाई", "ಕೊಯ್ಲು")),
    ("soil", ("నేల", "భూసార", "soil", "land preparation", "मिट्टी", "ಮಣ್ಣು")),
    ("planting", ("పండించ", "సాగు", "విత్త", "నాటు", "ఎలా మొదలు", "plant", "grow", "cultivat", "sow", "seed", "nursery", "कैसे उग", "బియ్యం సాగు")),
)


def _contains(text: str, term: str) -> bool:
    """Use word boundaries for Latin words, allowing inflected Indic words."""
    if term.isascii() and term[0].isalpha():
        return bool(re.search(r"(?<![a-z])" + re.escape(term) + r"(?![a-z])", text))
    return term in text


def detect_crop(message: str) -> str | None:
    text = message.casefold()
    # Longer aliases first, to avoid shorter names inside unrelated terms.
    for crop, aliases in CROP_ALIASES.items():
        if any(_contains(text, a.casefold()) for a in sorted(aliases, key=len, reverse=True)):
            return crop
    # Handle some unfamiliar crop names in English without maintaining a
    # fixed catalog. These names are *unverified user text*, not expert data.
    for pattern in (
        r"\b(?:grow|growing|plant|planting|cultivate|cultivating)\s+([a-z][a-z\- ]{1,35}?)(?:\s+(?:crop|plants|seeds|in|on|this|next|at|during)\b|[?.!,]|$)",
        r"\bmy\s+([a-z][a-z\- ]{1,30}?)\s+(?:crop|plants|leaves|field)\b",
    ):
        match = re.search(pattern, text)
        if match:
            candidate = match.group(1).strip()
            if candidate and candidate not in {"a", "the", "some", "any", "new", "crop"}:
                return candidate
    return None


def detect_topic(message: str) -> str:
    text = message.casefold()
    for topic, terms in TOPIC_TERMS:
        if any(term in text for term in terms):
            return topic
    return "general"


def _say(crop: str | None, topic: str, language: str) -> Advice:
    telugu = language == "te-IN"
    name = (TE_LABELS.get(crop, crop) if crop else None) if telugu else crop
    if not crop:
        if topic == "climate":
            if telugu:
                return Advice(
                    "పంటల ఎదుగుదలకు అనుకూలమైన వాతావరణ పరిస్థితులు:\n"
                    "1. ఖరీఫ్ (వర్షాకాలం: జూన్-అక్టోబర్) - వేడి, అధిక తేమ ఉన్న వాతావరణం (25°C-35°C). వరి, పత్తి, మొక్కజొన్న, సోయాబీన్‌లకు అనుకూలం.\n"
                    "2. రబీ (శీతాకాలం: అక్టోబర్-మార్చి) - చల్లని, పొడి వాతావరణం (15°C-25°C). గోధుమ, శనగ, ఆవాలు, టమాటా పంటలకు అనుకూలం.\n"
                    "3. జైద్ (వేసవి: మార్చి-జూన్) - వేడి, తగినంత ఎండ ఉన్న వాతావరణం. పుచ్చకాయ, దోసకాయ, ఆకుకూరలకు అనుకూలం.\n"
                    "మీరు ఏ నిర్దిష్ట పంట వాతావరణ వివరాలు తెలుసుకోవాలనుకుంటున్నారు?",
                    topic, ["ఏ పంట సాగు చేయాలనుకుంటున్నారు?", "మీ ప్రాంతం/జిల్లా ఏది?"]
                )
            return Advice(
                "Climate & Seasonal Guidelines for Crops in India:\n"
                "1. Kharif (Monsoon: June-October) - Warm and humid (25°C-35°C), ideal for Paddy, Cotton, Maize, and Soybean.\n"
                "2. Rabi (Winter: October-March) - Cool and dry (15°C-25°C), ideal for Wheat, Mustard, Gram, and Winter Vegetables.\n"
                "3. Zaid (Summer: March-June) - Warm and sunny, ideal for Cucurbits, Watermelon, and Fodder crops.\n"
                "Which specific crop do you want detailed climate and temperature requirements for?",
                topic, ["Which crop are you asking about?", "Which district or state is your farm in?"]
            )
        if telugu:
            return Advice("మీ ప్రశ్నకు సహాయం చేయడానికి సిద్ధంగా ఉన్నాను. మీరు ఏ పంట గురించి అడుగుతున్నారు? పంట పేరు, మీ జిల్లా, సమస్య వివరాలు చెప్పండి. ఇది ప్రస్తుతం నమూనా సహాయకుడు మాత్రమే; పూర్తి AI సమాధానాలు తదుపరి దశలో వస్తాయి.",
                          topic, ["మీరు ఏ పంట పండిస్తున్నారు?", "మీ పొలం ఏ జిల్లాలో ఉంది?"])
        return Advice("I can help with questions about many different crops—not only paddy. Which crop are you asking about, and what is your question? Tell me your district and the crop's current stage if relevant. This is a demo; unrestricted, source-backed answers need the reasoning model in phase 2.",
                      topic, ["Which crop are you growing?", "What issue are you facing?"])
    if telugu:
        opening = f"మీ {name} పంట గురించి అడిగిన ప్రశ్నను గుర్తించాను. "
        messages = {
            "yellow": ("ఆకులు పసుపుగా మారడానికి ప్రధాన కారణం నత్రజని లేదా జింక్ లేదా ఇనుము లోపం కావచ్చు. తక్షణ పరిష్కారం: లీటరు నీటికి 10-15 గ్రాముల యూరియా లేదా 5 గ్రాముల 19-19-19 ఎరువును కలిపి పిచికారీ చేయండి. ఇనుము లోపమైతే లీటరు నీటికి 5 గ్రాముల అన్నభేది (Ferrous Sulphate) + 1 గ్రాము నిమ్మ ఉప్పు కలిపి పిచికారీ చేయండి.", ["పంట ఎన్ని రోజులది?", "ఏ ఆకులు పసుపుగా ఉన్నాయి?"]),
            "pest": ("పురుగు లేదా తెగులు నివారణకు: రసం పీల్చే పురుగులకైతే లీటరు నీటికి 2 మి.లీ వేప నూనె (10,000 ppm) లేదా 0.3 గ్రాముల థయామిథాక్సమ్ 25% WG పిచికారీ చేయండి. పురుగుల లక్షణాలను బట్టి సరైన సస్యరక్షణ చర్యలు చేపట్టండి.", ["పురుగులు కనిపిస్తున్నాయా?", "ఏ లక్షణాలు కనిపిస్తున్నాయి?"]),
            "fertilizer": ("ఎరువుల యాజమాన్యం: ఎకరానికి సిఫార్సు చేసిన నత్రజని, భాస్వరం, పొటాష్ ఎరువులను విడతల వారీగా వేయండి. పైపాటుగా లీటరు నీటికి 10 గ్రాముల యూరియా లేదా 19-19-19 కాంప్లెక్స్ ఎరువు పిచికారీ చేస్తే తక్షణ పోషకాలు అందుతాయి.", ["భూసార పరీక్ష చేశారా?", "పంట ఏ దశలో ఉంది?"]),
            "water": ("నీటి యాజమాన్యం: పైరు సున్నితమైన దశల్లో (దుబ్బు చేసే దశ, పూత, గింజ పాలు పోసుకునే దశ) నేలలో తగినంత తేమ ఉండేలా తడులు ఇవ్వండి. పొలంలో నీరు నిల్వ ఉండకుండా మురుగు నీటిని బయటకు తీయండి.", ["పంట ఎన్ని రోజులది?", "మీ జిల్లాలో వర్షం పడిందా?"]),
            "harvest": ("కోత సమయం: పంటలో 80-85% వెన్నులు లేదా కాయలు బంగారు పసుపు రంగులోకి మారి గింజలు గట్టిపడినప్పుడు కోత ప్రారంభించండి. కోతకు వారం రోజుల ముందు నీరు పెట్టడం ఆపండి.", ["ఏ రకం పంట?", "ఎప్పుడు నాటారు?"]),
            "soil": ("నేల తయారీ: ఎకరానికి 4-5 టన్నుల పశువుల ఎరువు వేసి లోతు దుక్కులు చేయండి. భూసార పరీక్ష ఆధారంగా సిఫార్సు చేసిన మోతాదులో భాస్వరం ఎరువులను ఆఖరి దుక్కిలో వేయండి.", ["మీ నేల రకం ఏమిటి?", "భూసార పరీక్ష చేశారా?"]),
            "planting": ("సాగు పద్ధతులు: నాణ్యమైన ధృవీకరించిన విత్తనాలను ఎంచుకోండి. విత్తే ముందు కిలో విత్తనానికి 2.5 గ్రాముల కార్బండజిమ్ లేదా ట్రైకోడెర్మా విరిడితో విత్తన శుద్ధి చేయండి. సరైన వరుసల దూరంలో నాటండి.", ["ఏ జిల్లాలో సాగు చేస్తారు?", "నీటి సదుపాయం ఉందా?"]),
            "climate": ("అనుకూల వాతావరణం & ఎదుగుదల పరిస్థితులు: 1. ఉష్ణోగ్రత: 20°C నుండి 32°C మధ్య ఉష్ణోగ్రత సరైన ఎదుగుదలకు అత్యంత అనుకూలం (మొలకకు 22-28°C, శాఖీయ ఎదుగుదలకు 25-30°C). 38°C కంటే ఎక్కువ వేడి లేదా 15°C కంటే తక్కువ చలి పూత రాలడానికి దారితీస్తుంది. 2. గాలిలో తేమ: 60-70% తేమ అనుకూలం; అధిక తేమ శిలీంధ్ర తెగుళ్లను పెంచుతుంది కాబట్టి తగిన జాగ్రత్తలు తీసుకోవాలి. 3. సీజన్లు: ఖరీఫ్ (జూన్-జూలై) లేదా రబీ (అక్టోబర్-నవంబర్). అకాల వర్షాల సమయంలో పొలంలో నీరు నిల్వకుండా మురుగు కాలువలు సిద్ధం చేసుకోవాలి.", ["మీ ప్రాంతంలో ప్రస్తుత ఉష్ణోగ్రత ఎంత?", "మీరు ఖరీఫ్ లేదా రబీ సీజన్‌లో సాగు చేస్తున్నారా?"]),
            "general": ("మీ పంట సంరక్షణకు పూర్తి వివరాలు అందించడానికి సిద్ధంగా ఉన్నాను. సమస్య మరింత స్పష్టంగా తెలపండి.", ["పంట ఏ దశలో ఉంది?", "మీ సమస్యను వివరించండి?"]),
        }
    else:
        opening = f"I understand you're asking about {name}. "
        messages = {
            "yellow": ("Yellowing leaves are commonly caused by Nitrogen, Iron, or Zinc deficiency. Direct Solution: Spray 10g Urea or 5g 19:19:19 soluble fertilizer per liter of water. For micronutrient deficiency, spray Ferrous Sulphate (5g/L) with citric acid (1g/L).", ["How old is the crop?", "Which leaves are yellow?"]),
            "pest": ("Pest/Disease Control: For sucking pests, spray Neem oil 1500 ppm at 5ml/L, or Thiamethoxam 25% WG at 0.3g/L. For fungal leaf spots, spray Mancozeb 75% WP at 2.5g/L.", ["Are insects visible?", "Where is the damage?"]),
            "fertilizer": ("Fertilizer Recommendation: Apply recommended NPK in split doses. Top dress with Urea during active vegetative growth, and spray 19:19:19 at 5g/L for immediate nutrient absorption.", ["Do you have a soil test?", "What is the crop stage?"]),
            "water": ("Irrigation Management: Maintain adequate soil moisture during critical stages (tillering, flowering, grain filling). Ensure proper drainage to prevent root rot.", ["Which district is your farm in?", "How old is the crop?"]),
            "harvest": ("Harvest Timing: Harvest when 80-85% of panicles or grains turn golden yellow and moisture drops to around 18-20%. Stop irrigation 7-10 days before harvest.", ["What variety is it?", "When was it planted?"]),
            "soil": ("Soil Preparation: Deep summer ploughing followed by incorporating 4-5 tonnes of well-rotted FYM per acre. Apply recommended basal phosphorus and potassium.", ["What soil type do you have?", "Do you have a soil test?"]),
            "planting": ("Cultivation Guide: Use certified quality seeds. Treat seeds with Carbendazim 50% WP (2g/kg seed) or Trichoderma viride (10g/kg seed) before sowing.", ["Where is your farm?", "Do you have irrigation?"]),
            "climate": ("Ideal Climate, Temperature & Seasonal Requirements: 1. Temperature: Optimal growth occurs between 20°C and 32°C (germination: 22-28°C, vegetative/flowering: 24-30°C). Temperatures exceeding 38°C cause flower and fruit drop, while cold below 15°C stunts development. 2. Rainfall & Humidity: Requires moderate humidity of 60-70%. Extended high humidity (>85%) encourages fungal diseases, requiring preventive measures. 3. Sowing Seasons: Kharif (June-July with monsoon onset) and Rabi (October-November). During sudden heatwaves or dry spells, apply light frequent irrigation and organic mulching to conserve root zone moisture.", ["What is the current temperature in your district?", "Are you planting in Kharif, Rabi, or Summer?"]),
            "general": ("I am ready to help you with actionable farming solutions. Describe the issue and current crop stage for tailored advice.", ["What stage is the crop in?", "Could you describe the issue?"]),
        }
    detail, questions = messages[topic]
    return Advice(opening + detail, topic, questions, crop)
    return Advice(opening + detail, topic, questions, crop)


class DemoAdvisor:
    """Demo crop and issue recognition, including recent chat context."""

    def respond(self, message: str, language_code: str, history: list[str] | None = None) -> Advice:
        crop = detect_crop(message)
        if not crop:
            # A follow-up such as "How often should I water it?" should refer
            # to the most recently mentioned crop in this conversation.
            for previous in reversed(history or []):
                crop = detect_crop(previous)
                if crop:
                    break
        return _say(crop, detect_topic(message), language_code)
