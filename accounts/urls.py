from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Accounts home
    path("", views.home, name="home"),

    # User registration
    path("register/", views.register, name="register"),

    # User login
    path("login/", views.user_login, name="login"),

    # Account dashboard redirect
    path("dashboard/", views.dashboard, name="dashboard"),

    # User logout
    path("logout/", views.user_logout, name="logout"),
]