"""
KisanSathi AI Assistant Service with Multi-Language Support
Languages supported:
- en: English
- hi: Hindi
- bn: Bengali (বাংলা)
- mr: Marathi (मराठी)
- te: Telugu (తెలుగు)
- ta: Tamil (தமிழ்)
"""

def detect_language(text):
    """
    Heuristic language detection based on Unicode ranges and common language keywords.
    """
    for char in text:
        code = ord(char)
        # Bengali: 0980-09FF
        if 0x0980 <= code <= 0x09FF:
            return "bn"
        # Devanagari (Hindi / Marathi): 0900-097F
        if 0x0900 <= code <= 0x097F:
            # Check for Marathi-specific characters or words
            if any(w in text for w in ["आहे", "नाही", "कसे", "शेतकरी", "पाऊस", "पिके"]):
                return "mr"
            return "hi"
        # Telugu: 0C00-0C7F
        if 0x0C00 <= code <= 0x0C7F:
            return "te"
        # Tamil: 0B80-0BFF
        if 0x0B80 <= code <= 0x0BFF:
            return "ta"
    return "en"


RESPONSES = {
    "disease": {
        "en": (
            "🌿 KisanSathi Advice:\n\n"
            "If you notice spots, yellowing, or wilting on your crop leaves, "
            "navigate to 'Analyze Crop' to run an AI scan on the affected leaf. "
            "Also monitor recent humidity and rain levels in your Weather section.\n\n"
            "If damage is spreading rapidly, consult an agricultural officer or specialist immediately."
        ),
        "hi": (
            "🌿 KisanSathi सुझाव:\n\n"
            "अगर फसल की पत्तियों पर दाग, पीलापन या सूखापन दिखाई दे रहा है, "
            "तो पहले Crop Health Analysis में अपनी फसल और symptoms select करें। "
            "साथ में अपने क्षेत्र का weather data भी check करें।\n\n"
            "अगर symptoms बढ़ रहे हैं, तो स्थानीय कृषि विशेषज्ञ से पुष्टि करवाना बेहतर रहेगा।"
        ),
        "bn": (
            "🌿 KisanSathi পরামর্শ:\n\n"
            "যদি আপনার ফসলের পাতায় দাগ, হলুদ ভাব বা শুকিয়ে যাওয়া লক্ষ্য করেন, "
            "তবে 'Analyze Crop' বিভাগে যান এবং পাতার রোগ নির্ণয় করুন। "
            "একই সাথে আপনার এলাকার আবহাওয়ার তথ্য যাচাই করুন।\n\n"
            "রোগ দ্রুত ছড়িয়ে পড়লে স্থানীয় কৃষি কর্মকর্তার পরামর্শ নিন।"
        ),
        "mr": (
            "🌿 KisanSathi सल्ला:\n\n"
            "पिकांच्या पानांवर डाग, पिवळेपणा किंवा वाळणे आढळल्यास, "
            "'Analyze Crop' विभागात जाऊन पिकाचे विश्लेषण करा. "
            "सोबतच तुमच्या भागातील हवामानाचा अंदाज तपासा.\n\n"
            "लक्षणे वाढल्यास तात्काळ स्थानिक कृषी तज्ज्ञांचा सल्ला घ्या."
        ),
        "te": (
            "🌿 KisanSathi సలహా:\n\n"
            "పంట ఆకులపై మచ్చలు, పసుపు రంగు లేదా ఎండిపోవడం గమనిస్తే, "
            "'Analyze Crop' విభాగానికి వెళ్లి ఆకు ఫోటోను విశ్లేషించండి. "
            "వాతావరణ పరిస్థితులను కూడా సరిచూసుకోండి.\n\n"
            "సమస్య ఎక్కువైతే సమీప వ్యవసాయ అధికారిని సంప్రదించండి."
        ),
        "ta": (
            "🌿 KisanSathi ஆலோசனை:\n\n"
            "பயிரின் இலைகளில் புள்ளிகள், மஞ்சள் நிறம் அல்லது வாடுதல் தென்பட்டால், "
            "'Analyze Crop' பகுதிக்குச் சென்று இலை புகைப்படத்தை பகுப்பாய்வு செய்யுங்கள். "
            "வானிலை அறிக்கையையும் சரிபார்க்கவும்.\n\n"
            "நோய் அதிகரித்தால் உடனடியாக வேளாண்மை அலுவலரை அணுகவும்."
        ),
    },
    "weather": {
        "en": (
            "🌦️ KisanSathi Weather Forecast:\n\n"
            "Visit the Weather dashboard to see real-time temperature, humidity, rainfall forecasts, "
            "and spray suitability indices for your district.\n\n"
            "Always factor in impending rainfall before scheduling pesticide or fertilizer applications."
        ),
        "hi": (
            "🌦️ KisanSathi Weather:\n\n"
            "अपने क्षेत्र का current temperature, humidity और rainfall देखने के लिए Weather section खोलें।\n\n"
            "मौसम के आधार पर irrigation और crop-health decisions लेने से पहले local conditions भी ध्यान में रखें।"
        ),
        "bn": (
            "🌦️ KisanSathi আবহাওয়া:\n\n"
            "আপনার এলাকার তাপমাত্রা, আর্দ্রতা এবং বৃষ্টির পূর্বাভাস জানতে Weather বিভাগে যান।\n\n"
            "কীটনাশক বা সার প্রয়োগের আগে আগামী ২৪ ঘণ্টার বৃষ্টির সম্ভাবনা লক্ষ্য করুন।"
        ),
        "mr": (
            "🌦️ KisanSathi हवामान अंदाज:\n\n"
            "तुमच्या भागातील तापमान, आर्द्रता आणि पावसाचा अंदाज पाहण्यासाठी Weather विभाग उघडा.\n\n"
            "फवारणी किंवा खत व्यवस्थापनापूर्वी स्थानिक हवामानाची खात्री करा."
        ),
        "te": (
            "🌦️ KisanSathi వాతావరణం:\n\n"
            "మీ ప్రాంతంలోని ఉష్ణోగ్రత, తేమ మరియు వర్ష సూచన కోసం Weather విభాగాన్ని చూడండి.\n\n"
            "మందుల పిచికారీ మరియు నీటిపారుదల నిర్ణయాలు తీసుకునేముందు వాతావరణాన్ని గమనించండి."
        ),
        "ta": (
            "🌦️ KisanSathi வானிலை:\n\n"
            "உங்கள் பகுதியின் வெப்பநிலை, ஈரப்பதம் மற்றும் மழைப்பொழிவை அறிய Weather பகுதிக்குச் செல்லுங்கள்.\n\n"
            "மருந்து தெளிக்கும் முன் வானிலை முன்னறிவிப்பை கவனிப்பது நல்லது."
        ),
    },
    "irrigation": {
        "en": (
            "💧 Irrigation & Water Management:\n\n"
            "Base irrigation schedules on soil moisture, crop growth stage, and upcoming precipitation. "
            "Drip irrigation saves up to 40% water while curbing weed growth.\n\n"
            "Avoid waterlogging to prevent root rot and soil-borne fungal pathogens."
        ),
        "hi": (
            "💧 Irrigation Advice:\n\n"
            "सिंचाई का निर्णय crop, growth stage, soil condition और recent rainfall को ध्यान में रखकर लें।\n\n"
            "बहुत अधिक पानी देने से root-related problems और fungal diseases का risk बढ़ सकता है।"
        ),
        "bn": (
            "💧 সেচ ব্যবস্থাপনা:\n\n"
            "মাটির আর্দ্রতা, ফসলের বৃদ্ধির পর্যায় এবং বৃষ্টির পূর্বাভাস বিবেচনা করে সেচ দিন।\n\n"
            "অতিরিক্ত জল জমে থাকলে শিকড় পচা রোগ হতে পারে।"
        ),
        "mr": (
            "💧 सिंचन सल्ला:\n\n"
            "पिकांची अवस्था, जमिनीचा ओलावा आणि येणारा पाऊस लक्षात घेऊन पाणी द्यावे.\n\n"
            "अति पाणी दिल्यास मुळांची सड आणि बुरशीजन्य रोगांचा प्रादुर्भाव वाढू शकतो."
        ),
        "te": (
            "💧 నీటిపారుదల సలహా:\n\n"
            "నేల తేమ, పంట దశ మరియు వర్ష సూచనను బట్టి నీరు అందించండి.\n\n"
            "అధికంగా నీరు నిలవడం వల్ల వేరు కుళ్ళు తెగుళ్లు వచ్చే ప్రమాదం ఉంది."
        ),
        "ta": (
            "💧 பாசன மேலாண்மை:\n\n"
            "மண்ணின் ஈரப்பதம், பயிர் நிலை மற்றும் மழை வாய்ப்பை கருத்தில் கொண்டு பாசனம் செய்யுங்கள்.\n\n"
            "அதிக நீர் தேங்கினால் வேர் அழுகல் நோய் ஏற்பட வாய்ப்புள்ளது."
        ),
    },
    "learning": {
        "en": (
            "📚 KisanSathi Learning Hub:\n\n"
            "Explore 3D interactive models, crop encyclopedias, modern organic practices, "
            "and seasonal farming guides inside the 3D Learning section."
        ),
        "hi": (
            "📚 KisanSathi Farming Learning:\n\n"
            "आप crop selection, seed management, irrigation, crop diseases, fertilizers, "
            "harvesting और market-related topics सीख सकते हैं।\n\n"
            "KisanSathi के Learning section में topic-wise information देखें।"
        ),
        "bn": (
            "📚 কৃষি শিক্ষা কেন্দ্র:\n\n"
            "উন্নত চাষাবাদ, বীজ শোধন, সার প্রয়োগ এবং ফসল সুরক্ষা সম্পর্কিত তথ্যের জন্য "
            "আমাদের '3D Learning' বিভাগে যান।"
        ),
        "mr": (
            "📚 शेती ज्ञान केंद्र:\n\n"
            "सुधारीत शेती पद्धती, कीड नियंत्रण, खत व्यवस्थापन आणि 3D मॉडेल पाहण्यासाठी "
            "'3D Learning' विभागात जा."
        ),
        "te": (
            "📚 వ్యవసాయ అభ్యాసం:\n\n"
            "ఆధునిక వ్యవసాయ పద్ధతులు, విత్తన శుద్ధి మరియు క్రిమిసంహారకాల సమాచారం కోసం "
            "'3D Learning' విభాగాన్ని సందర్శించండి."
        ),
        "ta": (
            "📚 வேளாண் கல்வி மையம்:\n\n"
            "நவீன விவசாய நுட்பங்கள், விதை நேர்த்தி மற்றும் 3D காட்சி வழிகாட்டிகளுக்கு "
            "'3D Learning' பிரிவை பார்வையிடுங்கள்."
        ),
    },
    "default": {
        "en": (
            "👨‍🌾 Hello! I am KisanSathi AI Assistant.\n\n"
            "You can ask me questions in English, Hindi, Bengali, Marathi, Telugu, or Tamil about:\n"
            "🌱 Crop diseases & symptoms\n"
            "🌦️ Weather & spray timing\n"
            "💧 Irrigation planning\n"
            "🏛️ Government schemes\n"
            "📚 3D agricultural learning"
        ),
        "hi": (
            "👨‍🌾 नमस्ते! मैं KisanSathi AI सहायक हूँ।\n\n"
            "आप मुझसे हिंदी, अंग्रेजी, बंगाली, मराठी, तेलुगु या तमिल में पूछ सकते हैं:\n"
            "🌱 फसल के रोग और लक्षण\n"
            "🌦️ मौसम और छिड़काव का समय\n"
            "💧 सिंचाई प्रबंधन\n"
            "🏛️ सरकारी योजनाएं\n"
            "📚 आधुनिक खेती सीखें"
        ),
        "bn": (
            "👨‍🌾 নমস্কার! আমি কিষাণসাথী এআই সহায়ক।\n\n"
            "আপনি বাংলা, হিন্দি, ইংরেজি ইত্যাদি ভাষায় আমাকে যেকোনো প্রশ্ন করতে পারেন:\n"
            "🌱 ফসলের রোগ ও সমাধান\n"
            "🌦️ আবহাওয়া ও স্প্রে পরামর্শ\n"
            "💧 সেচ পদ্ধতি\n"
            "🏛️ সরকারি প্রকল্প"
        ),
        "mr": (
            "👨‍🌾 नमस्कार! मी किसानसाथी AI सहाय्यक आहे.\n\n"
            "तुम्ही मराठी, हिंदी किंवा इंग्रजीत शेतीविषयक प्रश्न विचारू शकता:\n"
            "🌱 पिकांवरील रोग व उपाय\n"
            "🌦️ हवामान अंदाज व फवारणी\n"
            "💧 पाणी व्यवस्थापन\n"
            "🏛️ शासकीय योजना"
        ),
        "te": (
            "👨‍🌾 నమస్కారం! నేను కిసాన్‌సాథీ AI సహాయకుడిని.\n\n"
            "మీరు నన్ను తెలుగు, హిందీ లేదా ఇంగ్లీషులో వ్యవసాయ ప్రశ్నలు అడగవచ్చు:\n"
            "🌱 పంట తెగుళ్లు మరియు నివారణ\n"
            "🌦️ వాతావరణ సమాచారం\n"
            "💧 నీటి యాజమాన్యం\n"
            "🏛️ ప్రభుత్వ పథకాలు"
        ),
        "ta": (
            "👨‍🌾 வணக்கம்! நான் கிசான்சாதி AI உதவியாளர்.\n\n"
            "நீங்கள் என்னிடம் தமிழ், இந்தி அல்லது ஆங்கிலத்தில் வேளாண் கேள்விகளைக் கேட்கலாம்:\n"
            "🌱 பயிர் நோய்கள் மற்றும் தீர்வுகள்\n"
            "🌦️ வானிலை முன்னறிவிப்பு\n"
            "💧 பாசன வழிகாட்டுதல்\n"
            "🏛️ அரசு நலத்திட்டங்கள்"
        ),
    }
}


def get_ai_response(question, lang=None):
    question_lower = (question or "").lower()

    # If explicit lang not provided, detect from script
    if not lang or lang not in ["en", "hi", "bn", "mr", "te", "ta"]:
        lang = detect_language(question)

    # Disease check
    disease_keywords = [
        "disease", "leaf", "spot", "pest", "fungus", "yellow",
        "बीमारी", "रोग", "पत्ता", "दाग", "कीट",
        "রোগ", "পাতা", "দাগ", "পোকামাকড়",
        "रोग", "पान", "डाग", "कीड",
        "తెగులు", "మచ్చ", "ఆకు", "పురుగులు",
        "நோய்", "இலை", "பூச்சி", "புள்ளி"
    ]
    if any(w in question_lower for w in disease_keywords):
        return RESPONSES["disease"].get(lang, RESPONSES["disease"]["en"])

    # Weather check
    weather_keywords = [
        "weather", "temperature", "rain", "forecast", "humidity",
        "बारिश", "मौसम", "तापमान", "हवा",
        "বৃষ্টি", "আবহাওয়া", "তাপমাত্রা",
        "पाऊस", "हवामान", "तापमान",
        "వర్షం", "వాతావరణం", "ఎండ",
        "மழை", "வானிலை", "வெப்பநிலை"
    ]
    if any(w in question_lower for w in weather_keywords):
        return RESPONSES["weather"].get(lang, RESPONSES["weather"]["en"])

    # Irrigation check
    irrigation_keywords = [
        "water", "irrigation", "drip", "moisture",
        "पानी", "सिंचाई", "ड्रिप", "नमी",
        "জল", "সেচ", "পানি",
        "पाणी", "सिंचन", "ओलावा",
        "నీరు", "నీటిపారుదల", "తేమ",
        "நீர்", "பாசனம்", "ஈரப்பதம்"
    ]
    if any(w in question_lower for w in irrigation_keywords):
        return RESPONSES["irrigation"].get(lang, RESPONSES["irrigation"]["en"])

    # Learning check
    learning_keywords = [
        "learn", "farming", "guide", "practice", "crop", "seed",
        "खेती", "कृषि", "सीखना", "बीज",
        "কৃষি", "চাষ", "বীজ",
        "शेती", "बियाणे", "मार्गदर्शन",
        "వ్యవసాయం", "సాగు", "విత్తనాలు",
        "விவசாயம்", "பயிர்", "விதை"
    ]
    if any(w in question_lower for w in learning_keywords):
        return RESPONSES["learning"].get(lang, RESPONSES["learning"]["en"])

    # Fallback response in selected/detected language
    return RESPONSES["default"].get(lang, RESPONSES["default"]["en"])