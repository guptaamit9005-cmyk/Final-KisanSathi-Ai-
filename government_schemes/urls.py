from django.urls import path
from . import views

app_name = "government_schemes"

urlpatterns = [
    path("", views.scheme_list, name="home"),
    path("list/", views.scheme_list, name="scheme_list"),
    path("api/schemes/", views.scheme_api, name="scheme_api"),
    path("api/check-eligibility/", views.check_eligibility_api, name="check_eligibility_api"),
    path("<slug:slug>/", views.scheme_detail, name="scheme_detail"),
]