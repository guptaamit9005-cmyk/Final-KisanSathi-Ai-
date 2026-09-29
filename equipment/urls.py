from django.urls import path

from . import views


app_name = "equipment"


urlpatterns = [

    path(
        "",
        views.equipment_home,
        name="home"
    ),

    path(
        "add/",
        views.add_equipment,
        name="add"
    ),

    path(
        "<int:equipment_id>/",
        views.equipment_detail,
        name="detail"
    ),

    path(
        "<int:equipment_id>/book/",
        views.book_equipment,
        name="book"
    ),

    path(
        "my-bookings/",
        views.my_bookings,
        name="my_bookings"
    ),

    path(
        "my-equipment/",
        views.my_equipment,
        name="my_equipment"
    ),

    path(
        "owner-bookings/",
        views.owner_bookings,
        name="owner_bookings"
    ),

    path(
        "booking/<int:booking_id>/approve/",
        views.approve_booking,
        name="approve_booking"
    ),

    path(
        "booking/<int:booking_id>/reject/",
        views.reject_booking,
        name="reject_booking"
    ),
]