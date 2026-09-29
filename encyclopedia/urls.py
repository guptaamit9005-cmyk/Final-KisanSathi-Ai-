from django.urls import path
from . import views

app_name = "encyclopedia"

urlpatterns = [
    path("", views.learning_home, name="home"),
]