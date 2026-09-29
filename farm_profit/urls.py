from django.urls import path
from . import views


app_name = "farm_profit"


urlpatterns = [

    path(
        "",
        views.farm_profit_calculator,
        name="calculator"
    ),

]