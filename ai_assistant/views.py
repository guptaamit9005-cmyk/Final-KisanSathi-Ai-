from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .services import get_ai_response


@login_required(login_url="accounts:login")
def assistant_home(request):
    return render(
        request,
        "ai_assistant/assistant.html"
    )


@login_required(login_url="accounts:login")
def assistant_api(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST request required."
        }, status=405)

    question = request.POST.get("question", "").strip()

    if not question:
        return JsonResponse({
            "success": False,
            "message": "Please enter your question."
        })

    answer = get_ai_response(question)

    return JsonResponse({
        "success": True,
        "answer": answer
    })