import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ai_assistant.rag_engine import ask_karran_ai


@csrf_exempt
def chatbot(request):
    """
    RAG-enabled Chatbot endpoint for backwards-compatibility with /chatbot/?question=...
    """
    question = request.GET.get("question") or request.GET.get("q") or request.GET.get("message", "")
    lang = request.GET.get("lang")

    if request.method == "POST":
        question = request.POST.get("question") or request.POST.get("message") or question
        lang = request.POST.get("lang") or lang

    question = (question or "").strip()
    image_b64 = None
    if request.FILES.get("image"):
        image_file = request.FILES["image"]
        try:
            image_b64 = base64.b64encode(image_file.read()).decode("utf-8")
        except Exception:
            pass

    result = ask_karran_ai(question, user_lang=lang, image_b64=image_b64)

    return JsonResponse({
        "success": result.get("success", True),
        "answer": result.get("reply", ""),
        "reply": result.get("reply", ""),
        "lang": result.get("lang", "hi"),
        "voice_code": result.get("voice_code", "hi-IN")
    })
import urllib.request
import urllib.parse
from django.http import HttpResponse

def karran_tts(request):
    text = request.GET.get('text', '')
    lang = request.GET.get('lang', 'hi')
    if not text:
        return HttpResponse(status=400)
    
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl={lang}&q={urllib.parse.quote(text)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            audio = response.read()
            return HttpResponse(audio, content_type="audio/mpeg")
    except Exception as e:
        return HttpResponse(status=500)
