import json
import urllib.parse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ai_assistant.rag_engine import ask_karran_ai
from .speech import clean_for_voice


def home(request):
    return render(request, "core/home.html")


@csrf_exempt
@require_http_methods(["GET", "POST"])
def karran_chat(request):
    """
    Karran AI Agricultural Chatbot API endpoint with RAG (Retrieval-Augmented Generation),
    LLM integration, and multilingual voice routing (Hindi, English, Bengali, Marathi, Telugu, Tamil).
    """
    if request.method == "POST":
        # Supports JSON or Form-data
        if request.content_type and "application/json" in request.content_type:
            try:
                data = json.loads(request.body.decode("utf-8"))
            except Exception:
                data = {}
            question = data.get("q") or data.get("message") or data.get("question") or data.get("query", "")
            user_lang = data.get("lang")
        else:
            question = request.POST.get("q") or request.POST.get("message") or request.POST.get("question") or request.POST.get("query", "")
            user_lang = request.POST.get("lang")
    else:
        question = request.GET.get("q") or request.GET.get("message") or request.GET.get("question") or request.GET.get("query", "")
        user_lang = request.GET.get("lang")

    question = (question or "").strip()

    if not question:
        return JsonResponse({
            "success": False,
            "reply": "कृपया अपना सवाल पूछें / Please ask your question.",
            "answer": "कृपया अपना सवाल पूछें / Please ask your question.",
            "lang": "hi",
            "voice_code": "hi-IN"
        })

    # Pass through RAG + LLM Engine
    result = ask_karran_ai(question, user_lang=user_lang)

    reply_text = result.get("reply", "")
    lang = result.get("lang", "hi")
    voice_code = result.get("voice_code", "hi-IN")
    spoken_text = clean_for_voice(reply_text, max_chars=240)
    tts_url = f"/karran/tts/?text={urllib.parse.quote(spoken_text)}&lang={lang}"

    return JsonResponse({
        "success": result.get("success", True),
        "reply": reply_text,
        "answer": reply_text,  # Backwards compatibility
        "spoken_reply": spoken_text,
        "tts_url": tts_url,
        "lang": lang,
        "voice_code": voice_code,
        "has_context": result.get("has_context", False)
    })