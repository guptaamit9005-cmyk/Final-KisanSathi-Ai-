from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .rag_engine import ask_karran_ai


def assistant_home(request):
    """
    Dedicated Karran AI Agricultural Assistant page.
    Open to all farmers with optional personalization if logged in.
    """
    return render(
        request,
        "ai_assistant/assistant.html",
        {
            "user_name": request.user.first_name if request.user.is_authenticated else ""
        }
    )


@csrf_exempt
@require_http_methods(["GET", "POST"])
def assistant_api(request):
    """
    Unified JSON API for Karran AI Assistant.
    Accepts question via POST (Form or JSON) or GET query parameters.
    Returns structured reply with language code and voice synthesis metadata.
    """
    if request.method == "POST":
        if request.content_type and "application/json" in request.content_type:
            import json
            try:
                data = json.loads(request.body.decode("utf-8"))
            except Exception:
                data = {}
            question = data.get("q") or data.get("question") or data.get("message") or data.get("query", "")
            lang = data.get("lang")
        else:
            question = request.POST.get("q") or request.POST.get("question") or request.POST.get("message") or request.POST.get("query", "")
            lang = request.POST.get("lang")
    else:
        question = request.GET.get("q") or request.GET.get("question") or request.GET.get("message") or request.GET.get("query", "")
        lang = request.GET.get("lang")

    question = (question or "").strip()
    lang = (lang or "").strip().lower() or None

    if not question:
        return JsonResponse({
            "success": False,
            "message": "कृपया अपना सवाल पूछें / Please enter or speak your question.",
            "answer": "कृपया अपना सवाल पूछें / Please enter or speak your question.",
            "reply": "कृपया अपना सवाल पूछें / Please enter or speak your question.",
            "lang": "hi",
            "voice_code": "hi-IN",
            "has_context": False
        })

    result = ask_karran_ai(question, user_lang=lang)

    return JsonResponse({
        "success": result.get("success", True),
        "answer": result.get("reply", ""),
        "reply": result.get("reply", ""),
        "lang": result.get("lang", "hi"),
        "voice_code": result.get("voice_code", "hi-IN"),
        "has_context": result.get("has_context", False)
    })