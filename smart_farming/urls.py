from django.urls import path

from . import views


app_name = "smart_farming"


urlpatterns = [

    path(
        "",
        views.farming_home,
        name="home"
    ),

    path(
        "<int:pk>/",
        views.technique_detail,
        name="detail"
    ),

]