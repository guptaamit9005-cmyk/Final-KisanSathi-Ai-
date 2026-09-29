from django.urls import path

from . import views


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

]