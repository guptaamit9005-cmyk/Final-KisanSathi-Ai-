from django.urls import path

from . import views


app_name = "mandi"


urlpatterns = [

    path(
        "",
        views.mandi_home,
        name="home"
    ),

]