from django.urls import path

from . import views
from . import speech


app_name = "core"


urlpatterns = [

    # Landing page
    path(
        "",
        views.home,
        name="home"
    ),

    # Karran chatbot
    path(
        "karran/chat/",
        views.karran_chat,
        name="karran_chat"
    ),

    # Server-side speech-to-text (bypasses browser Web Speech API network issues)
    path(
        "karran/speech/",
        speech.speech_to_text,
        name="speech_to_text"
    ),

    # High-quality server-side text-to-speech streaming (bypasses browser OS voice limitations)
    path(
        "karran/tts/",
        speech.text_to_speech,
        name="text_to_speech"
    ),

]