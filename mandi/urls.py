from django.urls import path

from . import views


app_name = "mandi"


urlpatterns = [

    path(
        "",
        views.mandi_home,
        name="home"
    ),

    path(
        "api/<str:crop_id>/",
        views.mandi_crop_api,
        name="api_detail"
    ),

]