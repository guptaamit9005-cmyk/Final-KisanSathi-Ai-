from django.urls import path

from . import views


app_name = "land_marketplace"


urlpatterns = [

    path(
        "",
        views.land_list,
        name="list"
    ),

    path(
        "create/",
        views.create_land,
        name="create"
    ),

    path(
        "my-land/",
        views.my_land,
        name="my_land"
    ),

    path(
        "my-requests/",
        views.my_requests,
        name="my_requests"
    ),

    path(
        "owner-requests/",
        views.owner_requests,
        name="owner_requests"
    ),

    path(
        "request/<int:request_id>/approve/",
        views.approve_request,
        name="approve_request"
    ),

    path(
        "request/<int:request_id>/reject/",
        views.reject_request,
        name="reject_request"
    ),

    path(
        "<int:land_id>/cost/",
        views.calculate_cost_api,
        name="calculate_cost"
    ),

    path(
        "<int:land_id>/",
        views.land_detail,
        name="detail"
    ),

]