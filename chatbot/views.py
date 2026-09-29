from django.http import JsonResponse

from .services import ask_bot


def chatbot(request):

    question = request.GET.get("question")

    answer = ask_bot(question)

    return JsonResponse({

        "answer":answer

    })