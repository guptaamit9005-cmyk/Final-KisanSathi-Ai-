"""
Karran AI & KisanSathi RAG (Retrieval-Augmented Generation) Knowledge Core.
Connects with local dataset (Mandi prices, Government schemes, Crop diseases & treatments,
Agricultural Roadmaps, Soil Health, Weather Advisory) and calls LLM (Gemini API with fallback to
Domain RAG Agronomic Engine).
"""
import os
import re
import json
import logging
import urllib.request
import urllib.parse
from django.conf import settings

logger = logging.getLogger(__name__)

# Languages supported with Indian regional voice synthesis codes
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "voice_code": "en-IN", "label": "English"},
    "hi": {"name": "Hindi", "voice_code": "hi-IN", "label": "हिंदी"},
    "bn": {"name": "Bengali", "voice_code": "bn-IN", "label": "বাংলা"},
    "mr": {"name": "Marathi", "voice_code": "mr-IN", "label": "मराठी"},
    "te": {"name": "Telugu", "voice_code": "te-IN", "label": "తెలుగు"},
    "ta": {"name": "Tamil", "voice_code": "ta-IN", "label": "தமிழ்"},
}

# Multilingual Crop Synonyms Dictionary
CROP_SYNONYMS = {
    "wheat": ["wheat", "gehu", "gehun", "गेहूं", "गेहु", "कनक", "kanak", "godhumai", "godhuma"],
    "rice": ["rice", "paddy", "dhan", "chawal", "धान", "चावल", "ধান", "তাণ্ডুল", "వరి", "அரிசி", "ভাত", "basmati", "1121", "mansoori", "swarna"],
    "maize": ["maize", "corn", "makka", "bhutta", "मक्का", "भुट्टा", "ভুট্টা", "మొక్కజొన్న", "மக்காச்சோளம்"],
    "mustard": ["mustard", "sarson", "sarso", "rai", "सरसों", "राई", "সর্ষে", "मोहरी", "ఆవాలు", "கடுகு", "toria"],
    "cotton": ["cotton", "kapas", "rui", "कपास", "रुई", "তুলা", "कापूस", "పత్తి", "பருத்தி"],
    "soybean": ["soybean", "soyabean", "soya", "सोयाबीन", "সয়াবিন", "సోయాబీన్", "சோயாபீன்"],
    "potato": ["potato", "aloo", "alu", "aalu", "आलू", "আলু", "बटाटा", "బంగాళాదుంప", "உருளைக்கிழங்கு"],
    "tomato": ["tomato", "tamatar", "टमाटर", "টমেটো", "टोमॅटो", "టమోటా", "தக்காளி"],
    "onion": ["onion", "pyaz", "kanda", "प्याज", "कांदा", "পেঁয়াজ", "ఉల్లిపాయ", "வெங்காயம்"],
    "gram": ["gram", "chana", "chickpea", "चना", "छोला", "ছোলা", "हरभरा", "శనగలు", "கொண்டைக்கடலை"],
    "sugarcane": ["sugarcane", "ganna", "ईख", "गन्ना", "আখ", "ऊस", "చెరకు", "கரும்பு"],
    "apple": ["apple", "seb", "सेब", "আপেল", "सफरचंद", "యాపిల్", "ஆப்பிள்"],
    "chilli": ["chilli", "chili", "mirch", "mirchi", "मिर्च", "লঙ্কা", "मिरची", "మిరపకాయ", "மிளகாய்"],
    "garlic": ["garlic", "lahsun", "लहसुन", "রসুন", "लसूण", "వెల్లుల్లి", "பூண்டு"],
    "groundnut": ["groundnut", "peanut", "moongfali", "mungfali", "मूंगफली", "চীনাবাদাম", "भुईमूग", "వేరుశెనగ", "நிலக்கடலை"],
}


def detect_language(text: str) -> str:
    """
    Detect script and keywords to identify Hindi, Bengali, Marathi, Telugu, Tamil, or English.
    """
    if not text:
        return "hi"

    # Check Unicode characters
    for ch in text:
        code = ord(ch)
        if 0x0980 <= code <= 0x09FF:
            return "bn"  # Bengali
        if 0x0C00 <= code <= 0x0C7F:
            return "te"  # Telugu
        if 0x0B80 <= code <= 0x0BFF:
            return "ta"  # Tamil
        if 0x0900 <= code <= 0x097F:
            # Devanagari: distinguish Marathi vs Hindi
            if any(w in text for w in ["आहे", "नाही", "कसे", "शेतकरी", "पाऊस", "पिके", "माहिती", "करावे", "भांडवल"]):
                return "mr"
            return "hi"

    # Latin script phonetic transliteration checks (Hinglish, etc.)
    text_lower = text.lower()
    hinglish_markers = [
        "kya", "kaise", "kare", "karein", "kisan", "fasal", "kheti", "pani", "dawa", "rog",
        "mandi", "bhav", "barish", "mausam", "sarkar", "yojana", "namaste", "peela", "peele",
        "keeda", "keede", "khad", "bij", "beej", "sundi", "dhabba", "dhabbe", "batao", "bataiye",
        "kitna", "kab", "subsidy", "gehu", "gehun", "dhan", "chawal", "makka", "sarson", "ilaj",
        "patte", "patti", "khet", "upchar", "bimaari", "bimari", "daam", "hai", "hain",
        "ka", "ki", "ke", "ko", "me", "mein", "se", "aur", "nahi", "hota", "hoga", "chahiye"
    ]
    if any(re.search(r'\b' + re.escape(w) + r'\b', text_lower) for w in hinglish_markers):
        return "hi"

    return "en"


def match_crop_in_query(query: str) -> list:
    """Extract all matched standard crop IDs from a natural query."""
    q_lower = query.lower()
    matched = []
    for crop_id, synonyms in CROP_SYNONYMS.items():
        for syn in synonyms:
            if syn in q_lower:
                matched.append(crop_id)
                break
    return matched


class AgriRAGRetriever:
    """
    Retrieves context-rich domain knowledge from local database, models, and encyclopedia.
    Grounds LLM responses in real mandi prices, verified treatments, schemes, and agrometeorology.
    """

    @staticmethod
    def retrieve_mandi_data(query: str) -> str:
        """Fetch matching real-time mandi prices and MSP from mandi dataset."""
        try:
            from mandi.views import ALL_CROPS_DATA
            q_lower = query.lower()
            crops_found = match_crop_in_query(query)

            matched_crops = []
            for crop in ALL_CROPS_DATA:
                c_id = crop.get("id", "").lower()
                c_name = crop.get("name", "").lower()
                if c_id in crops_found or c_id in q_lower or any(word in q_lower for word in c_name.split() if len(word) > 2):
                    matched_crops.append(crop)

            # If user asks generic mandi/price query without specific crop, return top 3 staple crops
            if not matched_crops and any(k in q_lower for k in ["mandi", "bhav", "price", "rate", "मंडी", "भाव", "दाम", "बाजार", "दर"]):
                matched_crops = ALL_CROPS_DATA[:3]

            if matched_crops:
                lines = ["--- 📈 LIVE MANDI MARKET PRICES & MSP (मंडी भाव रिपोर्ट) ---"]
                for c in matched_crops[:2]:
                    lines.append(f"• Crop/Fasal: {c['name']}")
                    lines.append(f"  Official MSP: ₹{c.get('msp', 'N/A')}/Quintal | Avg Market Price: ₹{c.get('avg_price')}/Quintal (Trend: {c.get('trend')})")
                    top_mkts = c.get("markets", [])[:3]
                    for m in top_mkts:
                        lines.append(f"    - {m['market']} ({m.get('district')}, {m.get('state')}): ₹{m.get('price')}/Qtl [Min: ₹{m.get('min_price')} - Max: ₹{m.get('max_price')}]")
                return "\n".join(lines)
        except Exception as e:
            logger.warning(f"RAG Mandi retrieval error: {e}")
        return ""

    @staticmethod
    def retrieve_treatment_data(query: str) -> str:
        """Fetch crop disease diagnosis and remedies from treatments database."""
        try:
            from prediction.treatments import TREATMENTS
            q_lower = query.lower()
            crops_found = match_crop_in_query(query)

            matched = []
            for key, val in TREATMENTS.items():
                crop_name = val.get("crop", "").lower()
                disease_name = key.replace("___", " ").replace("_", " ").lower()

                crop_match = (crop_name in q_lower) or any(c in crop_name for c in crops_found)
                disease_match = any(word in q_lower for word in disease_name.split() if len(word) > 3)

                # Symptom matches
                if any(w in q_lower for w in ["peela", "yellow", "पीला"]) and ("yellow" in disease_name or "rust" in disease_name or "mosaic" in disease_name):
                    disease_match = True
                if any(w in q_lower for w in ["blight", "jhulsa", "झुलसा"]) and ("blight" in disease_name):
                    disease_match = True
                if any(w in q_lower for w in ["scab", "spot", "धब्बे", "दाग"]) and ("spot" in disease_name or "scab" in disease_name):
                    disease_match = True

                if crop_match or disease_match:
                    matched.append((key, val))

            if matched:
                lines = ["--- 🌿 CROP DISEASE & TREATMENT KNOWLEDGE (रोग निदान एवं उपचार) ---"]
                for k, v in matched[:2]:
                    d_clean = k.split("___")[-1].replace("_", " ").title()
                    lines.append(f"• Crop: {v.get('crop')} | Disease: {d_clean}")
                    if v.get("organic"):
                        lines.append(f"  🌱 Organic Solution (जैविक उपचार): {v['organic']}")
                    if v.get("chemical"):
                        lines.append(f"  🧪 Chemical Spray (कीटनाशक/फफूंदनाशक): {v['chemical']}")
                    if v.get("prevention"):
                        lines.append(f"  🛡️ Prevention (बचाव): {v['prevention']}")
                return "\n".join(lines)
        except Exception as e:
            logger.warning(f"RAG Treatment retrieval error: {e}")
        return ""

    @staticmethod
    def retrieve_schemes_data(query: str) -> str:
        """Fetch relevant government subsidies, insurance, and financial schemes."""
        try:
            from government_schemes.models import GovernmentScheme
            q_lower = query.lower()
            schemes = GovernmentScheme.objects.filter(is_active=True)
            matched = []
            for s in schemes:
                title = (s.title or "").lower()
                desc = (s.short_description or s.description or "").lower()
                if any(k in q_lower for k in ["pm-kisan", "kisan", "yojana", "scheme", "subsidy", "bima", "pension", "card", "loan", "सोलर", "योजना", "अनुदान"]) or any(k in title for k in q_lower.split() if len(k) > 3):
                    matched.append(s)

            if matched:
                lines = ["--- 🏛️ GOVERNMENT SCHEMES & SUBSIDIES (सरकारी योजनाएं) ---"]
                for s in matched[:3]:
                    lines.append(f"• {s.title} ({s.category.upper() if hasattr(s, 'category') and s.category else 'SCHEME'}): {s.short_description or s.description[:120]}")
                    if hasattr(s, 'benefits') and s.benefits:
                        lines.append(f"  Benefits: {s.benefits[:120]}")
                return "\n".join(lines)
        except Exception as e:
            logger.warning(f"RAG Scheme retrieval error: {e}")
        return ""

    @staticmethod
    def retrieve_roadmap_data(query: str) -> str:
        """Fetch agricultural cultivation guides from learning roadmaps."""
        try:
            from encyclopedia.views import LEARNING_ROADMAPS
            q_lower = query.lower()
            crops_found = match_crop_in_query(query)

            for r in LEARNING_ROADMAPS:
                crop = r.get("crop", "").lower()
                hindi = r.get("hindi_name", "").lower()
                c_id = r.get("id", "").lower()
                if crop in q_lower or hindi in q_lower or c_id in crops_found:
                    lines = [f"--- 🌾 CULTIVATION GUIDE: {r.get('crop')} ({r.get('hindi_name')}) ---"]
                    lines.append(f"Season: {r.get('season')}, Duration: {r.get('duration')}, Water Requirements: {r.get('water_req')}")
                    for st in r.get("steps", [])[:3]:
                        lines.append(f"Stage {st.get('stage_num')} ({st.get('days')}): {st.get('title')} -> {st.get('description')}")
                    return "\n".join(lines)
        except Exception as e:
            logger.warning(f"RAG Roadmap retrieval error: {e}")
        return ""

    @staticmethod
    def retrieve_weather_advisory(query: str) -> str:
        """Provide weather and spray timing rules."""
        q_lower = query.lower()
        if any(w in q_lower for w in ["weather", "rain", "barish", "mausam", "तापमान", "मौसम", "बारिश", "हवा", "spray", "छिड़काव", "wind"]):
            return (
                "--- 🌦️ AGRO-WEATHER & SPRAY ADVISORY RULES ---\n"
                "• Optimal Spraying Window: Spray during calm early mornings or late afternoons (wind < 10 km/h).\n"
                "• Rain Precaution: Never spray fungicides or foliar fertilizers if rainfall is forecast within the next 24 hours.\n"
                "• Irrigation Timing: Hold irrigation if continuous cloudy weather or rain is predicted to prevent root waterlogging and fungal dampening."
            )
        return ""

    @staticmethod
    def retrieve_equipment_data(query: str) -> str:
        """Provide machinery rental rate benchmarks."""
        q_lower = query.lower()
        if any(w in q_lower for w in ["tractor", "equipment", "machine", "rent", "किराया", "ट्रैक्टर", "मशीन", "हार्वेस्टर", "सीडर", "ड्रोन"]):
            return (
                "--- 🚜 FARM MACHINERY & EQUIPMENT RENTAL BENCHMARKS ---\n"
                "• 45-55 HP Tractor with driver: ₹600 - ₹900 per hour / ₹1,200 - ₹1,600 per acre plowing\n"
                "• Super Seeder / Happy Seeder: ₹1,200 - ₹1,800 per acre (zero-tillage wheat sowing)\n"
                "• Multi-crop Combine Harvester: ₹1,500 - ₹2,200 per acre\n"
                "• Agricultural Drone Spraying: ₹350 - ₹500 per acre (saves 90% water & 30% chemical)"
            )
        return ""

    @classmethod
    def get_context(cls, query: str) -> str:
        """Collect and synthesize all relevant context blocks based on query."""
        blocks = []
        mandi = cls.retrieve_mandi_data(query)
        if mandi:
            blocks.append(mandi)
        treatment = cls.retrieve_treatment_data(query)
        if treatment:
            blocks.append(treatment)
        schemes = cls.retrieve_schemes_data(query)
        if schemes:
            blocks.append(schemes)
        roadmap = cls.retrieve_roadmap_data(query)
        if roadmap:
            blocks.append(roadmap)
        weather = cls.retrieve_weather_advisory(query)
        if weather:
            blocks.append(weather)
        equipment = cls.retrieve_equipment_data(query)
        if equipment:
            blocks.append(equipment)

        return "\n\n".join(blocks)


def call_gemini_api(prompt: str, context: str, lang: str, image_b64: str = None) -> str:
    """
    Call Gemini LLM via REST API.
    Attempts modern models (gemini-2.5-flash, gemini-2.0-flash, gemini-1.5-flash).
    Falls back gracefully if key is not configured or network unavailable.
    """
    api_key = (
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or (getattr(settings, "GEMINI_API_KEY", "") if getattr(settings, "configured", False) else "")
    )

    lang_info = SUPPORTED_LANGUAGES.get(lang, SUPPORTED_LANGUAGES["hi"])
    lang_name = lang_info["name"]

    system_instruction = (
        "You are Karran (करन), the trusted AI Chief Agronomist and farming companion for KisanSathi AI in India. "
        f"You MUST answer the farmer's question in the requested language: {lang_name}. "
        "Guidelines for your response:\n"
        "1. Friendly and respectful: Start with a warm greeting suitable for an Indian farmer (e.g. '🙏 नमस्ते किसान भाई!' in Hindi).\n"
        "2. Grounded facts: Always prioritize and directly use the provided agricultural context (Mandi prices, dosages, schemes, roadmap steps).\n"
        "3. Action-oriented structure: Give clear bullet points with practical actions (Organic remedy, Chemical spray with dosage, Prevention).\n"
        "4. Speech-optimized: Phrase sentences naturally so they sound clear, rhythmic, and soothing when read aloud by Text-to-Speech (TTS).\n"
        "5. Keep the response concise, authoritative, and helpful without unnecessary fluff."
    )

    full_prompt = (
        f"{system_instruction}\n\n"
        f"=== VERIFIED AGRICULTURAL CONTEXT (RAG) ===\n{context if context else 'No specific database match found. Use your general agronomic knowledge.'}\n\n"
        f"=== FARMER QUESTION ===\n{prompt}"
    )

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        parts = [{"text": full_prompt}]
        if image_b64:
            parts.append({"inlineData": {"mimeType": "image/jpeg", "data": image_b64}})
            
        payload = {
            "contents": [{
                "parts": parts
            }],
            "generationConfig": {
                "temperature": 0.35,
                "maxOutputTokens": 700,
            }
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=9) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    text_parts = candidates[0].get("content", {}).get("parts", [])
                    if text_parts:
                        text = text_parts[0].get("text", "").strip()
                        if text:
                            return text
        except Exception as e:
            logger.info(f"Model {model_name} invocation note: {e}")
            continue

    # -----------------------------------------------------
    # FREE LLM FALLBACK: Pollinations.ai (No API key needed)
    # -----------------------------------------------------
    try:
        fallback_prompt = full_prompt
        if image_b64:
            fallback_prompt += "\n(Note to AI: Vision is offline due to rate limits. Answer based on text/context only.)"
        
        # Prevent URL from getting too long for GET request
        if len(fallback_prompt) > 4000:
            fallback_prompt = fallback_prompt[:4000]

        fallback_url = f"https://text.pollinations.ai/{urllib.parse.quote(fallback_prompt)}"
        req = urllib.request.Request(fallback_url, headers={"User-Agent": "Mozilla/5.0 (AgriVisionAI/1.0)"})
        with urllib.request.urlopen(req, timeout=30) as response:
            fallback_text = response.read().decode("utf-8").strip()
            if fallback_text:
                return fallback_text
    except Exception as e:
        logger.warning(f"Pollinations AI fallback failed: {e}")

    return ""


def generate_local_rag_response(question: str, context: str, lang: str) -> str:
    """
    High-Intelligence Local Agronomic RAG Engine.
    When external LLM is offline or no API key is set, synthesizes verified context
    into a structured, natural answer in Hindi and other regional languages.
    """
    q_lower = question.lower()

    # 1. Greetings
    if any(w in q_lower for w in ["namaste", "नमस्ते", "hello", "hi", "राम राम", "pranam", "प्रणाम", "salaam", "kem cho", "vanakkam"]):
        if lang == "hi":
            return (
                "🙏 **नमस्ते किसान भाई! मैं करन (Karran) हूँ — आपका AI कृषि साथी।**\n\n"
                "मैं आपकी फसलों की देखभाल, मंडी भाव, सरकारी योजनाओं और मौसम की सही जानकारी के लिए 24 घंटे उपलब्ध हूँ।\n\n"
                "💡 **आप मुझसे पूछ या बोल सकते हैं:**\n"
                "• फसलों की बीमारी और दवा (उदा. 'गेहूं में पीलापन कैसे ठीक करें?')\n"
                "• आज के ताजा मंडी भाव (उदा. 'गेहूं या धान का भाव क्या है?')\n"
                "• सरकारी योजनाएं (उदा. 'PM किसान की पात्रता क्या है?')\n"
                "• ट्रैक्टर व उपकरण किराया (उदा. 'सुपर सीडर का किराया?')\n\n"
                "नीचे माइक 🎙️ दबाकर अपनी भाषा में बोलें या टाइप करें!"
            )
        elif lang == "bn":
            return (
                "🙏 **নমস্কার কৃষক ভাই! আমি করণ (Karran) — কিষাণসাথী এআই সহায়ক।**\n\n"
                "ফসলের রোগ, সারের প্রয়োগ, বাজার দর (Mandi Rate) বা সরকারি প্রকল্প সম্পর্কে যেকোনো প্রশ্ন করুন বা মুখে বলুন।"
            )
        elif lang == "mr":
            return (
                "🙏 **नमस्कार शेतकरी बांधवांनो! मी करण (Karran) — किसानसाथी AI कृषी मार्गदर्शक।**\n\n"
                "पिकांचे रोग व कीड नियंत्रण, आजचे बाजारभाव, खतांचे नियोजन किंवा शासकीय योजनांबद्दल थेट बोला किंवा विचारा."
            )
        elif lang == "te":
            return (
                "🙏 **నమస్కారం రైతు సోదరులారా! నేను కరణ్ (Karran) — కిసాన్‌సాథీ AI వ్యవసాయ సహాయకుడిని.**\n\n"
                "పంట తెగుళ్లు, మందుల మోతాదు, మార్కెట్ ధరలు లేదా ప్రభుత్వ పథకాల గురించి నన్ను మాట్లాడి లేదా టైప్ చేసి అడగండి."
            )
        elif lang == "ta":
            return (
                "🙏 **வணக்கம் விவசாய தோழரே! நான் கரன் (Karran) — கிசான்சாதி AI வேளாண் ஆலோசகர்.**\n\n"
                "பயிர் நோய்கள், உர மேலாண்மை, சந்தை விலை அல்லது அரசு திட்டங்கள் குறித்து என்னிடம் கேட்டு பயன்பெறுங்கள்."
            )
        else:
            return (
                "🙏 **Namaste Farmer Friend! I am Karran — your AI Agricultural Advisor on KisanSathi.**\n\n"
                "I am here 24/7 to help you with crop diseases, mandi prices, government schemes, equipment rental, and weather alerts.\n\n"
                "Tap the microphone 🎙️ to ask by voice or type your question in English or Hindi!"
            )

    # 2. Disease / Pest / Health with RAG context
    if any(w in q_lower for w in ["disease", "pest", "fungus", "कीड़ा", "कीट", "रोग", "बीमारी", "पीला", "दाग", "फफूंद", "सुंडी", "माहू", "leaf", "spot", "dhabba", "curl", "wilt"]):
        if context:
            if lang == "hi":
                return (
                    "🌿 **फसल रोग निदान एवं समाधान (KisanSathi RAG Advisory):**\n\n"
                    f"{context}\n\n"
                    "💡 **कृषि वैज्ञानिक सलाह (Important Tips):**\n"
                    "1. **जैविक उपचार**: 5 मिली नीम तेल (10,000 PPM) प्रति लीटर पानी में मिलाकर शाम के समय छिड़कें।\n"
                    "2. **रासायनिक छिड़काव**: किसी भी फफूंदनाशक या कीटनाशक का छिड़काव तेज हवा या बारिश से पहले न करें।\n"
                    "3. **सटीक जांच**: प्रभावित पत्ती की साफ तस्वीर हमारे **'Analyze Crop'** टूल में स्कैन करके तुरंत रिपोर्ट पाएं।"
                )
            else:
                return (
                    "🌿 **Crop Disease Diagnosis & Treatment (KisanSathi RAG Advisory):**\n\n"
                    f"{context}\n\n"
                    "💡 **Agronomist Recommendations:**\n"
                    "1. **Organic Action**: Apply cold-pressed Neem Oil (10,000 PPM) at 5ml/litre water during calm evening hours.\n"
                    "2. **Chemical Safety**: Avoid spraying right before impending rainfall or in windy conditions (>10 km/h).\n"
                    "3. **Instant AI Scan**: Upload a photo of the affected leaf in our **Analyze Crop** section for real-time deep-learning verification."
                )
        else:
            if lang == "hi":
                return (
                    "🌿 **फसल रोग एवं कीट नियंत्रण मार्गदर्शिका:**\n\n"
                    "• **पीले पत्ते व फफूंद**: यदि पत्तियां पीली पड़ रही हैं या धब्बे हैं, तो प्रभावित पत्तों को खेत से बाहर निकालें। मैंकोजेब (Mancozeb 75% WP) 2 ग्राम प्रति लीटर या कार्बेंडाजिम 1 ग्राम/लीटर का छिड़काव करें।\n"
                    "• **माहू व रस चूसक कीट**: इमिडाक्लोप्रिड 17.8% SL (0.5 मिली/लीटर) या नीम तेल का छिड़काव करें।\n"
                    "• **सुंडी / इल्ली नियंत्रण**: इमामेक्टिन बेंजोएट (Emamectin Benzoate 5% SG) 80 ग्राम प्रति एकड़ 150-200 लीटर पानी में मिलाकर छिड़कें।\n\n"
                    "📷 **सलाह**: सटीक पहचान के लिए अपनी फसल का नाम लिखकर पूछें या **Analyze Crop** में फोटो अपलोड करें।"
                )
            else:
                return (
                    "🌿 **Crop Pest & Disease Advisory:**\n\n"
                    "• **Yellowing & Spots**: Remove heavily damaged leaves. Spray Mancozeb 75% WP (2g/L) or Carbendazim (1g/L) for fungal leaf spot control.\n"
                    "• **Aphids & Sucking Pests**: Spray Imidacloprid 17.8% SL (0.5ml/L) or concentrated Neem Oil (5ml/L).\n"
                    "• **Caterpillars & Borers**: Use Emamectin Benzoate 5% SG (80g/acre in 150-200L water).\n\n"
                    "📷 For pinpoint confirmation, scan the leaf directly on our **Analyze Crop** tool."
                )

    # 3. Mandi Market Prices
    if any(w in q_lower for w in ["mandi", "bhav", "price", "rate", "मंडी", "भाव", "दाम", "बाजार", "दर", "msp"]):
        if context:
            if lang == "hi":
                return (
                    "📈 **ताजा मंडी भाव एवं MSP रिपोर्ट (Live Mandi Insights):**\n\n"
                    f"{context}\n\n"
                    "💡 **बिक्री सुझाव:**\n"
                    "• सरकारी न्यूनतम समर्थन मूल्य (MSP) से कम भाव पर अपनी उपज न बेचें।\n"
                    "• जिलेवार दैनिक आवक और 30 दिनों का मूल्य ट्रेंड देखने के लिए हमारे **'Mandi'** सेक्शन पर जाएं।"
                )
            else:
                return (
                    "📈 **Latest Mandi Market Rates & MSP:**\n\n"
                    f"{context}\n\n"
                    "💡 **Marketing Tip:**\n"
                    "• Do not sell below the official Minimum Support Price (MSP) benchmark.\n"
                    "• Check district-level arrivals and 30-day price trends in our **Mandi** dashboard."
                )
        else:
            if lang == "hi":
                return (
                    "📈 **प्रमुख फसलों के औसत मंडी भाव (Current Mandi Averages):**\n\n"
                    "• **गेहूं (Wheat)**: औसत भाव ₹2,420/क्विंटल (सरकारी MSP: ₹2,275/क्विंटल)\n"
                    "• **धान बासमती (Paddy Basmati)**: औसत भाव ₹3,650/क्विंटल (सामान्य धान MSP: ₹2,300/क्विंटल)\n"
                    "• **मक्का (Maize)**: औसत भाव ₹2,210/क्विंटल (MSP: ₹2,090/क्विंटल)\n"
                    "• **सरसों (Mustard)**: औसत भाव ₹5,450/क्विंटल (MSP: ₹5,650/क्विंटल)\n\n"
                    "💡 अपनी स्थानीय मंडी का सही भाव जानने के लिए फसल का नाम बोलें (उदा. 'गेहूं का मंडी भाव')।"
                )
            else:
                return (
                    "📈 **Current Major Mandi Benchmarks:**\n\n"
                    "• **Wheat**: Avg ₹2,420/Qtl (Govt MSP: ₹2,275/Qtl)\n"
                    "• **Paddy Basmati**: Avg ₹3,650/Qtl (Common Paddy MSP: ₹2,300/Qtl)\n"
                    "• **Maize**: Avg ₹2,210/Qtl (MSP: ₹2,090/Qtl)\n"
                    "• **Mustard**: Avg ₹5,450/Qtl (MSP: ₹5,650/Qtl)\n\n"
                    "💡 Mention your crop name to receive specific state and district mandi rates."
                )

    # 4. Government Schemes
    if any(w in q_lower for w in ["scheme", "yojana", "योजना", "सरकार", "pm kisan", "सब्सिडी", "अनुदान", "लोन", "bima", "बीमा", "kcc"]):
        if context:
            if lang == "hi":
                return (
                    "🏛️ **सरकारी कृषि योजनाएं एवं अनुदान (Government Schemes):**\n\n"
                    f"{context}\n\n"
                    "💡 **आवेदन कैसे करें?**\n"
                    "पात्रता की शर्तें देखने और ऑनलाइन आवेदन लिंक के लिए मुख्य मेनू में **'Government Schemes'** पेज पर जाएं।"
                )
            else:
                return (
                    "🏛️ **Government Farmer Welfare Schemes:**\n\n"
                    f"{context}\n\n"
                    "💡 **How to Apply:**\n"
                    "View eligibility documents and direct portal links on the **Government Schemes** page."
                )
        else:
            if lang == "hi":
                return (
                    "🏛️ **किसानों के लिए प्रमुख कल्याणकारी योजनाएं:**\n\n"
                    "1. **PM-KISAN**: प्रतिवर्ष ₹6,000 की सम्मान निधि (₹2,000 की 3 किश्तों में सीधे बैंक खाते में)।\n"
                    "2. **प्रधानमंत्री फसल बीमा योजना (PMFBY)**: सूखा, बाढ़ या कीट प्रकोप से फसल क्षति पर 90% तक वित्तीय सुरक्षा।\n"
                    "3. **Kisan Credit Card (KCC)**: बिना गारंटी 4% की रियायती ब्याज दर पर ₹3 लाख तक कृषि ऋण।\n"
                    "4. **PM कुसुम योजना (Solar Pump)**: खेतों में सोलर पंप लगाने पर केंद्र व राज्य सरकार से 60% से 90% तक भारी सब्सिडी।\n\n"
                    "विस्तृत जानकारी के लिए हमारे **'Government Schemes'** सेक्शन पर जाएं।"
                )
            else:
                return (
                    "🏛️ **Key Central Government Farmer Schemes:**\n\n"
                    "1. **PM-KISAN**: ₹6,000 annual direct income support credited directly to bank accounts.\n"
                    "2. **PM Fasal Bima Yojana (PMFBY)**: Comprehensive yield protection against weather and pest catastrophes.\n"
                    "3. **Kisan Credit Card (KCC)**: Subsidized 4% interest crop credit up to ₹3 Lakhs.\n"
                    "4. **PM Kusum Scheme**: 60% to 90% subsidy on installing off-grid solar agricultural pumps.\n\n"
                    "Access online application links in our **Government Schemes** section."
                )

    # 5. Weather & Irrigation
    if any(w in q_lower for w in ["weather", "rain", "barish", "mausam", "तापमान", "मौसम", "बारिश", "हवा", "सिंचाई", "irrigation", "water", "pani"]):
        if lang == "hi":
            return (
                "🌦️ **मौसम एवं सिंचाई वैज्ञानिक परामर्श:**\n\n"
                "• **छिड़काव का सही समय**: कीटनाशक या टॉनिक का छिड़काव शाम के समय शांत हवा (10 किमी/घंटा से कम) में करें।\n"
                "• **बारिश की चेतावनी**: यदि अगले 24 घंटे में बारिश का पूर्वानुमान है तो यूरिया या रासायनिक स्प्रे तुरंत रोक दें।\n"
                "• **क्रांतिक सिंचाई अवस्थाएं**: गेहूं में 21 दिन पर (CRI अवस्था) और फूल आते समय नमी बनाए रखना बहुत जरूरी है।\n"
                "• लाइव 7-दिवसीय वर्षा पूर्वानुमान के लिए ऊपर दिए गए **'Weather'** सेक्शन को चेक करें।"
            )
        else:
            return (
                "🌦️ **Weather & Irrigation Agronomic Advisory:**\n\n"
                "• **Spray Conditions**: Spray foliar chemicals during calm evenings when wind speed is under 10 km/h.\n"
                "• **Rain Alert**: Avoid top-dressing urea or applying contact sprays if rain is predicted within 24 hours.\n"
                "• **Critical Irrigation Stages**: Ensure adequate soil moisture during root crown initiation and flowering stages.\n"
                "• For district-level 7-day radar and spray suitability indices, visit our **Weather** dashboard."
            )

    # 6. Equipment Rental
    if any(w in q_lower for w in ["tractor", "equipment", "machine", "rent", "किराया", "ट्रैक्टर", "मशीन", "हार्वेस्टर", "सीडर", "ड्रोन"]):
        if lang == "hi":
            return (
                "🚜 **किसानसाथी कृषि उपकरण एवं ट्रैक्टर रेंटल सेवा:**\n\n"
                "हमारे प्लेटफॉर्म पर आप नजदीकी वेंडर्स व साथी किसानों से आधुनिक उपकरण उचित किराए पर ले सकते हैं:\n"
                "• **ट्रैक्टर (45-55 HP)**: ₹600 - ₹900 प्रति घंटा / ₹1,200 प्रति एकड़ जोताई\n"
                "• **सुपर सीडर / हैप्पी सीडर**: ₹1,200 - ₹1,800 प्रति एकड़ (पराली प्रबंधन व सीधी बुवाई)\n"
                "• **कंबाइन हार्वेस्टर**: ₹1,500 - ₹2,200 प्रति एकड़ कटाई व गहाई\n"
                "• **कृषि ड्रोन स्प्रेयर**: ₹350 - ₹500 प्रति एकड़\n\n"
                "मशीन बुक करने के लिए हमारे **'Equipment'** मेनू पर जाएं।"
            )
        else:
            return (
                "🚜 **Agricultural Machinery & Equipment Rental:**\n\n"
                "Rent verified machinery easily from local farm equipment hubs:\n"
                "• **Tractors (45-55 HP)**: ₹600 - ₹900/hour or ₹1,200/acre tillage\n"
                "• **Super Seeder**: ₹1,200 - ₹1,800/acre (zero-tillage wheat sowing into stubble)\n"
                "• **Combine Harvester**: ₹1,500 - ₹2,200/acre\n"
                "• **Agri Drone Spraying**: ₹350 - ₹500/acre\n\n"
                "Browse and book rentals in the **Equipment** section."
            )

    # 7. Cultivation or Roadmaps with context
    if context:
        if lang == "hi":
            return (
                f"🌾 **किसानसाथी कृषि ज्ञानकोष (Agronomic RAG Insights):**\n\n"
                f"{context}\n\n"
                "💡 यदि आपको किसी विशेष खाद की मात्रा, बीज उपचार या रोग की दवा की जानकारी चाहिए तो सीधे बोलकर पूछें!"
            )
        else:
            return (
                f"🌾 **KisanSathi Agronomic Knowledge Core (RAG):**\n\n"
                f"{context}\n\n"
                "💡 Feel free to ask or speak for specific fertilizer dosages, seed varieties, or pest solutions."
            )

    # 8. General fallback
    if lang == "hi":
        return (
            "🌱 **नमस्ते! मैं करन (Karran AI) — आपका डिजिटल कृषि सलाहकार।**\n\n"
            "मैं आपकी निम्न विषयों में त्वरित सहायता कर सकता हूँ:\n"
            "1. **फसल रोग व उपचार**: पत्ती के दाग, पीलापन, सुंडी, माहू व फफूंद का सटीक इलाज।\n"
            "2. **मंडी भाव**: गेहूं, धान, मक्का, सरसों व सब्जियों के लाइव मंडी दाम और MSP।\n"
            "3. **सरकारी योजनाएं**: PM-Kisan (₹6000), फसल बीमा, किसान क्रेडिट कार्ड व सोलर पंप सब्सिडी।\n"
            "4. **मौसम व सिंचाई**: बारिश का पूर्वानुमान और छिड़काव का अनुकूल समय।\n"
            "5. **ट्रैक्टर व मशीनरी**: किराए पर आधुनिक कृषि उपकरण बुक करने की सुविधा।\n\n"
            "🎙️ **कृपया अपना सवाल बोलें (माइक दबाकर) या लिखकर पूछें!**"
        )
    else:
        return (
            "🌱 **Hello! I am Karran — your KisanSathi AI Farming Advisor.**\n\n"
            "I can assist you with:\n"
            "1. **Crop Health & Disease**: Chemical and organic remedies for pests and blights.\n"
            "2. **Mandi Market Rates**: Live market prices, state-level arrivals, and MSP.\n"
            "3. **Government Schemes**: PM-Kisan, PMFBY crop insurance, and subsidized loans.\n"
            "4. **Weather Forecasts**: Rainfall alerts and pesticide spray timing.\n"
            "5. **Farm Machinery Rental**: Tractors, seeders, and harvesters.\n\n"
            "🎙️ **Ask by tapping the microphone icon to speak, or type your question below!**"
        )


def ask_karran_ai(question: str, user_lang: str = None, image_b64: str = None) -> dict:
    """
    Core entrypoint for Karran AI:
    1. Detects language (Hindi, Bengali, Marathi, Telugu, Tamil, English).
    2. Runs RAG retrieval on local database (Mandi, Schemes, Treatments, Roadmaps, Weather, Machinery).
    3. Calls LLM (Gemini API) if configured; falls back seamlessly to the Domain RAG Engine.
    4. Returns dict with reply text, detected language, and voice language code for speech output.
    """
    question = (question or "").strip()
    if not question and not image_b64:
        return {
            "success": False,
            "reply": "कृपया अपना सवाल पूछें या फोटो अपलोड करें / Please enter a question or upload an image.",
            "lang": "hi",
            "voice_code": "hi-IN",
            "has_context": False
        }
    if not question:
        question = "Please analyze this image."

    # Detect language or use passed language
    detected_lang = user_lang if (user_lang and user_lang in SUPPORTED_LANGUAGES) else detect_language(question)
    voice_code = SUPPORTED_LANGUAGES.get(detected_lang, {}).get("voice_code", "hi-IN")

    # Step 1: Retrieve Augmented Context (RAG)
    context = AgriRAGRetriever.get_context(question)

    # Step 2: Try LLM (Gemini) if available
    llm_reply = call_gemini_api(question, context, detected_lang, image_b64)

    # Step 3: Fall back to local RAG knowledge core if LLM key not set or timed out
    if llm_reply:
        final_reply = llm_reply
    else:
        if image_b64:
            if detected_lang == "hi":
                final_reply = "📷 **इमेज प्राप्त हुई!**\n\nमुझे आपकी भेजी गई तस्वीर मिल गई है। (ध्यान दें: उन्नत इमेज विश्लेषण के लिए कृपया अपनी `.env` फाइल में `GEMINI_API_KEY` सेट करें)। लेकिन मैं देख पा रहा हूँ कि यह फसल से संबंधित हो सकती है। यदि आपको किसी बीमारी के बारे में जानकारी चाहिए, तो कृपया लक्षण भी लिखकर भेजें।"
            else:
                final_reply = "📷 **Image Received!**\n\nI have received your image. (Note: Please set `GEMINI_API_KEY` in your `.env` file for advanced computer vision analysis). I can see this is related to crops. Please type any symptoms you see for more specific advice."
        else:
            final_reply = generate_local_rag_response(question, context, detected_lang)

    return {
        "success": True,
        "reply": final_reply,
        "answer": final_reply,
        "lang": detected_lang,
        "voice_code": voice_code,
        "has_context": bool(context)
    }
