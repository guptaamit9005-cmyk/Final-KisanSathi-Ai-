from django.urls import path
from . import views

app_name = "weather"

urlpatterns = [
    path("", views.weather_home, name="home"),
    path("api/", views.weather_api, name="api"),
]