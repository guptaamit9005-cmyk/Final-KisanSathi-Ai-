"""
Server-side Speech-to-Text endpoint for KisanSathi Karran AI.
Receives WAV audio recorded from the farmer's browser or mobile device,
transcribes it using Google Speech Recognition API with automatic language fallback,
and supports Gemini multimodal audio transcription if configured.
"""
import io
import json
import logging
import os
import re
import urllib.parse
import urllib.request

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def speech_to_text(request):
    """
    Receives audio blob from browser (WAV PCM 16-bit, 16kHz, mono) and transcribes it.
    Supports Hindi (hi-IN), English (en-IN), Bengali (bn-IN), Marathi (mr-IN),
    Telugu (te-IN), Tamil (ta-IN), Gujarati (gu-IN), Punjabi (pa-IN).

    Request: multipart/form-data with 'audio' file and optional 'lang' field.
    Response: JSON { success: bool, text: str, lang: str, voice_code: str }
    """
    audio_file = request.FILES.get("audio")
    if not audio_file:
        return JsonResponse({
            "success": False,
            "text": "",
            "error": "Koi audio prapt nahi hui / No audio file received"
        }, status=400)

    lang = (request.POST.get("lang") or "hi").strip().lower()
    lang_map = {
        "hi": "hi-IN",
        "en": "en-IN",
        "bn": "bn-IN",
        "mr": "mr-IN",
        "te": "te-IN",
        "ta": "ta-IN",
        "gu": "gu-IN",
        "pa": "pa-IN",
    }
    recognition_lang = lang_map.get(lang, "hi-IN")

    try:
        import speech_recognition as sr
    except ImportError:
        return JsonResponse({
            "success": False,
            "text": "",
            "error": "Speech recognition library not installed on server."
        }, status=500)

    # Read audio bytes
    audio_bytes = audio_file.read()
    if len(audio_bytes) < 400:
        return JsonResponse({
            "success": False,
            "text": "",
            "error": "ऑडियो बहुत छोटा था। कृपया कम से कम 1-2 सेकंड बोलें।"
        })

    logger.info(f"Speech-to-text request: {len(audio_bytes)} bytes, lang: {recognition_lang}")

    from django.conf import settings

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 200
    recognizer.dynamic_energy_threshold = False

    try:
        audio_data_file = sr.AudioFile(io.BytesIO(audio_bytes))
        with audio_data_file as source:
            audio = recognizer.record(source)
    except Exception as e:
        logger.error(f"Audio parsing failed: {e}")
        return JsonResponse({
            "success": False,
            "text": "",
            "error": "ऑडियो फॉर्मेट पढ़ने में समस्या हुई। कृपया दोबारा बोलें।"
        })

    # Languages to attempt (primary first, then fallback e.g. Hindi/English)
    langs_to_try = [recognition_lang]
    if recognition_lang == "en-IN":
        langs_to_try.append("hi-IN")
    elif recognition_lang == "hi-IN":
        langs_to_try.append("en-IN")

    recognized_text = ""
    for try_lang in langs_to_try:
        try:
            recognized_text = recognizer.recognize_google(audio, language=try_lang)
            if recognized_text and recognized_text.strip():
                return JsonResponse({
                    "success": True,
                    "text": recognized_text.strip(),
                    "lang": lang,
                    "voice_code": try_lang
                })
        except sr.UnknownValueError:
            continue
        except Exception as e:
            logger.warning(f"Google STT request error for {try_lang}: {e}")
            break

    # Fallback: Multimodal Gemini API for transcription if API key is present
    api_key = getattr(settings, "GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if api_key:
        try:
            import base64
            import urllib.request

            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
            models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
            
            for m in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
                payload = {
                    "contents": [{
                        "parts": [
                            {
                                "inlineData": {
                                    "mimeType": "audio/wav",
                                    "data": audio_b64
                                }
                            },
                            {
                                "text": (
                                    f"Transcribe this farmer's voice recording accurately into text. "
                                    f"The language is Indian ({recognition_lang}). Return ONLY the raw transcribed text."
                                )
                            }
                        ]
                    }]
                }

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
                            gemini_text = text_parts[0].get("text", "").strip()
                            if gemini_text:
                                return JsonResponse({
                                    "success": True,
                                    "text": gemini_text,
                                    "lang": lang,
                                    "voice_code": recognition_lang
                                })
        except Exception as e:
            logger.warning(f"Gemini audio transcription fallback failed: {e}")

    return JsonResponse({
        "success": False,
        "text": "",
        "error": "आवाज स्पष्ट समझ नहीं आई। कृपया शांत जगह पर थोड़ा तेज और साफ बोलें।"
    })


# In-memory LRU cache for audio bytes (stores up to 250 snippets)
_TTS_AUDIO_CACHE = {}


def clean_for_voice(text: str, max_chars: int = 240) -> str:
    """
    Cleans raw markdown response, strips URLs, headers, and bullet symbols,
    and returns a clean, natural sentence string optimized for audio pronunciation.
    Translates symbols (₹, %, /Qtl) into spoken words so TTS sounds human.
    """
    if not text:
        return ""

    clean = text

    # Strip RAG and technical markdown markers
    clean = re.sub(r'---.*?---', ' ', clean)
    clean = re.sub(r'🌾\s*\*+.*?RAG.*?\*+', ' ', clean, flags=re.IGNORECASE)
    clean = re.sub(r'💡[^\n]*', ' ', clean)
    clean = re.sub(r'^#+\s+', '', clean, flags=re.MULTILINE)
    clean = re.sub(r'\*\*(.*?)\*\*', r'\1', clean)
    clean = re.sub(r'\*(.*?)\*', r'\1', clean)
    clean = re.sub(r'__(.*?)__', r'\1', clean)
    clean = re.sub(r'_(.*?)_', r'\1', clean)
    clean = re.sub(r'^[•\-\*]\s+', '', clean, flags=re.MULTILINE)
    clean = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', clean)
    clean = re.sub(r'`{1,3}.*?`{1,3}', '', clean, flags=re.DOTALL)

    # Conversational replacements for agricultural terms & symbols
    clean = re.sub(r'Crop/Fasal:\s*', 'फसल ', clean, flags=re.IGNORECASE)
    clean = re.sub(r'Official MSP:\s*', 'सरकारी एमएसपी ', clean, flags=re.IGNORECASE)
    clean = re.sub(r'Avg Market Price:\s*', 'औसत मंडी भाव ', clean, flags=re.IGNORECASE)
    clean = re.sub(r'₹\s*(\d+)', r'\1 रुपये', clean)
    clean = re.sub(r'/(Quintal|Qtl)', ' प्रति क्विंटल', clean, flags=re.IGNORECASE)
    clean = re.sub(r'/\s*acre', ' प्रति एकड़', clean, flags=re.IGNORECASE)
    clean = re.sub(r'(\d+)\s*%', r'\1 प्रतिशत', clean)
    clean = re.sub(r'(\d+)\s*ml', r'\1 मिली', clean, flags=re.IGNORECASE)
    clean = re.sub(r'(\d+)\s*gm', r'\1 ग्राम', clean, flags=re.IGNORECASE)
    clean = re.sub(r'(\d+)\s*kg', r'\1 किलो', clean, flags=re.IGNORECASE)
    clean = re.sub(r'(\d+)\s*lit(?:er|re)?', r'\1 लीटर', clean, flags=re.IGNORECASE)

    # Strip symbols and emojis
    clean = re.sub(r'[\U00010000-\U0010ffff]', '', clean)
    clean = re.sub(r'[\u2600-\u27bf]', '', clean)
    clean = re.sub(r'[\u200b-\u200d\ufeff]', '', clean)
    clean = re.sub(r'[\|_~`\^#<>]', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()

    # Split into clean sentence-level summary within max_chars
    if len(clean) > max_chars:
        sentences = re.split(r'([।\.!\?])', clean)
        accumulated = ""
        for i in range(0, len(sentences) - 1, 2):
            part = sentences[i] + sentences[i + 1]
            if len(accumulated) + len(part) <= max_chars:
                accumulated += " " + part
            else:
                break
        if accumulated.strip():
            clean = accumulated.strip()
        else:
            clean = clean[:max_chars].rsplit(' ', 1)[0] + '।'

    return clean.strip()


@csrf_exempt
def text_to_speech(request):
    """
    High-fidelity server-side Text-To-Speech endpoint.
    Accepts 'text' and 'lang' (hi, en, bn, mr, te, ta) via GET or POST.
    Fetches native MP3 pronunciation from Google TTS with LRU in-memory caching.
    Bypasses OS voice missing issues on Windows/Chrome.
    """
    text = (request.GET.get("text") or request.POST.get("text") or "").strip()
    lang = (request.GET.get("lang") or request.POST.get("lang") or "hi").strip().lower()

    lang_map = {
        "hi": "hi",
        "en": "en",
        "bn": "bn",
        "mr": "mr",
        "te": "te",
        "ta": "ta",
        "gu": "gu",
        "pa": "pa",
    }
    tts_lang = lang_map.get(lang.split("-")[0].lower(), "hi")

    cleaned = clean_for_voice(text, max_chars=240)
    if not cleaned:
        return JsonResponse({"error": "No text provided"}, status=400)

    # Cache lookup
    cache_key = f"{tts_lang}:{cleaned}"
    if cache_key in _TTS_AUDIO_CACHE:
        response = HttpResponse(_TTS_AUDIO_CACHE[cache_key], content_type="audio/mpeg")
        response["Cache-Control"] = "public, max-age=86400"
        response["X-TTS-Cached"] = "HIT"
        return response

    try:
        # Split into ~120 char chunks for Google TTS single-request speed
        chunks = []
        words = cleaned.split()
        cur_chunk = []
        cur_len = 0
        for w in words:
            if cur_len + len(w) + 1 > 120:
                chunks.append(" ".join(cur_chunk))
                cur_chunk = [w]
                cur_len = len(w)
            else:
                cur_chunk.append(w)
                cur_len += len(w) + 1
        if cur_chunk:
            chunks.append(" ".join(cur_chunk))

        # Fetch audio from Google TTS
        # NOTE: Using HTTP (not HTTPS) as SSL handshake from Django server may timeout on some setups.
        # Falls back to HTTPS if HTTP redirects or fails.
        audio_stream = bytearray()
        for chunk in chunks[:2]:  # Limit to max 2 chunks to guarantee sub-second delivery
            if not chunk.strip():
                continue
            chunk_encoded = urllib.parse.quote(chunk.strip())
            tts_url_http = (
                f"http://translate.google.com/translate_tts?ie=UTF-8&q="
                f"{chunk_encoded}&tl={tts_lang}&client=tw-ob"
            )
            tts_url_https = (
                f"https://translate.google.com/translate_tts?ie=UTF-8&q="
                f"{chunk_encoded}&tl={tts_lang}&client=tw-ob"
            )
            fetched = False
            for tts_url in [tts_url_http, tts_url_https]:
                try:
                    req = urllib.request.Request(tts_url, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    })
                    with urllib.request.urlopen(req, timeout=7) as resp:
                        audio_stream.extend(resp.read())
                    fetched = True
                    break
                except Exception as fetch_e:
                    logger.warning(f"TTS fetch failed for {tts_url[:60]}: {fetch_e}")
            if not fetched:
                logger.error(f"All TTS fetch attempts failed for chunk: {chunk[:40]}")

        audio_bytes = bytes(audio_stream)
        if not audio_bytes:
            logger.error(f"No audio bytes received from Google TTS for text: {cleaned[:60]}")
            return JsonResponse({"error": "TTS service unavailable. Browser will use built-in voice."}, status=503)

        if audio_bytes:
            # Store in cache (limit to 250 items)
            if len(_TTS_AUDIO_CACHE) > 250:
                old_keys = list(_TTS_AUDIO_CACHE.keys())[:50]
                for k in old_keys:
                    _TTS_AUDIO_CACHE.pop(k, None)
            _TTS_AUDIO_CACHE[cache_key] = audio_bytes

        response = HttpResponse(audio_bytes, content_type="audio/mpeg")
        response["Cache-Control"] = "public, max-age=86400"
        response["X-TTS-Cached"] = "MISS"
        return response

    except Exception as e:
        logger.error(f"Server-side TTS fetch failed: {e}")
        return JsonResponse({"error": str(e)}, status=503)


