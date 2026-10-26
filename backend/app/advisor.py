"""Crop-independent *demo* conversation logic.

This lightweight router handles sample questions for many crop names and farming
issues. It is not a general-purpose language model or an agronomy knowledge
base. Replace it with a source-grounded reasoning agent in phase 2.
"""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Advice:
    text: str
    topic: str
    suggestions: list[str]
    crop: str | None = None


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
        if telugu:
            return Advice("మీ ప్రశ్నకు సహాయం చేయడానికి సిద్ధంగా ఉన్నాను. మీరు ఏ పంట గురించి అడుగుతున్నారు? పంట పేరు, మీ జిల్లా, సమస్య వివరాలు చెప్పండి. ఇది ప్రస్తుతం నమూనా సహాయకుడు మాత్రమే; పూర్తి AI సమాధానాలు తదుపరి దశలో వస్తాయి.",
                          topic, ["మీరు ఏ పంట పండిస్తున్నారు?", "మీ పొలం ఏ జిల్లాలో ఉంది?"])
        return Advice("I can help with questions about many different crops—not only paddy. Which crop are you asking about, and what is your question? Tell me your district and the crop's current stage if relevant. This is a demo; unrestricted, source-backed answers need the reasoning model in phase 2.",
                      topic, ["Which crop are you growing?", "What issue are you facing?"])
    if telugu:
        opening = f"మీ {name} పంట గురించి అడిగిన ప్రశ్నను గుర్తించాను. "
        messages = {
            "yellow": ("ఆకులు పసుపుగా మారడానికి నీరు, పోషకాలు లేదా ఇతర సమస్యలు కారణం కావచ్చు. పంట వయస్సు ఎంత? పాత ఆకులా, కొత్త ఆకులా మారుతున్నాయి?", ["పంట ఎన్ని రోజులది?", "ఏ ఆకులు పసుపుగా ఉన్నాయి?"]),
            "pest": ("పురుగులు లేదా వ్యాధి అనుమానం ఉంటే దెబ్బతిన్న భాగం, లక్షణాలు, పంట వయస్సు చెప్పండి. నిర్ధారణ లేకుండా రసాయన మందులు వాడకండి.", ["పురుగులు కనిపిస్తున్నాయా?", "ఏ లక్షణాలు కనిపిస్తున్నాయి?"]),
            "fertilizer": ("ఎరువుల సిఫార్సు భూసార పరీక్ష, పంట దశ, గతంలో ఉపయోగించిన ఎరువులపై ఆధారపడుతుంది. భూసార పరీక్ష చేశారా? పంటకు ఎన్ని రోజులు అయ్యాయి?", ["భూసార పరీక్ష చేశారా?", "పంట ఏ దశలో ఉంది?"]),
            "water": ("నీటి అవసరం పంట దశ, నేల, వాతావరణంపై ఆధారపడి ఉంటుంది. మీ ప్రాంతం ఏది? పంటకు ఎన్ని రోజులు అయ్యాయి? ప్రస్తుతం నేలలో తేమ ఎలా ఉంది?", ["పంట ఎన్ని రోజులది?", "మీ జిల్లాలో వర్షం పడిందా?"]),
            "harvest": ("కోత సమయం రకం, నాటిన తేదీ, పక్వత లక్షణాలపై ఆధారపడి ఉంటుంది. ఏ రకం పండిస్తున్నారు? ఎప్పుడు నాటారు?", ["ఏ రకం పంట?", "ఎప్పుడు నాటారు?"]),
            "soil": ("నేల తయారీకి మీ నేల రకం, భూసార పరీక్ష, నీటి సదుపాయం వంటి వివరాలు అవసరం. మీ జిల్లా ఏది? నేల పరీక్ష చేశారా?", ["మీ నేల రకం ఏమిటి?", "భూసార పరీక్ష చేశారా?"]),
            "planting": ("సాగు ప్రారంభించే ముందు జిల్లా, సీజన్, భూమి పరిమాణం, నీటి సదుపాయం చెప్పండి. వాటి ఆధారంగా స్థానికంగా సరిపోయే పద్ధతుల గురించి ధృవీకరించిన సమాచారం పొందవచ్చు.", ["ఏ జిల్లాలో సాగు చేస్తారు?", "నీటి సదుపాయం ఉందా?"]),
            "general": ("మీ ప్రశ్నకు సరైన సమాచారం ఇవ్వాలంటే పంట వయస్సు, జిల్లా, సమస్యను ఇంకా వివరించండి. ప్రస్తుతం ఇది నమూనా స్పందన మాత్రమే; నిర్ధారిత వ్యవసాయ మార్గదర్శకాలను ఉపయోగించే AI మోడల్ తదుపరి దశలో చేరుతుంది.", ["పంట ఏ దశలో ఉంది?", "మీ సమస్యను వివరించండి?"]),
        }
    else:
        opening = f"I understand you're asking about {name}. "
        messages = {
            "yellow": ("Yellow leaves can result from several different conditions. How old is the crop? Are older or newer leaves affected? Don't apply chemicals based on color alone.", ["How old is the crop?", "Which leaves are yellow?"]),
            "pest": ("Describe the affected parts, visible insects, and how long symptoms have been present. Avoid pesticide treatment without identifying the cause.", ["Are insects visible?", "Where is the damage?"]),
            "fertilizer": ("Fertilizer choices depend on the soil test, crop stage and previous applications. Do you have a soil test? How old is this crop?", ["Do you have a soil test?", "What is the crop stage?"]),
            "water": ("Irrigation depends on location, soil, weather, and crop stage. Where is your farm, how old is the crop, and how moist is the soil?", ["Which district is your farm in?", "How old is the crop?"]),
            "harvest": ("Harvest timing depends on the variety, planting date, and signs of maturity. What variety is it, and when was it planted?", ["What variety is it?", "When was it planted?"]),
            "soil": ("Soil preparation depends on soil type, local conditions, irrigation and testing. Have you tested your soil? What district is the farm in?", ["What soil type do you have?", "Do you have a soil test?"]),
            "planting": ("To plan cultivation, tell me your district, season, field size, and irrigation access. A later grounded advisor can use those details to provide locally relevant steps.", ["Where is your farm?", "Do you have irrigation?"]),
            "general": ("Tell me the current growth stage, your district, and more about the question. This demo can recognize many crop names but cannot yet give trustworthy answers to every open-ended question.", ["What stage is the crop in?", "Could you describe the issue?"]),
        }
    detail, questions = messages[topic]
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
