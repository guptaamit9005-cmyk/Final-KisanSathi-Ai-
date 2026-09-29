
from django.urls import path
from . import views

app_name = "government_schemes"

urlpatterns = [
    path("", views.scheme_list, name="scheme_list"),
    path("api/", views.scheme_api, name="scheme_api"),
]