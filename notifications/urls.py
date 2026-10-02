from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('settings/', views.alert_settings, name='settings'),
    path('test/', views.test_alert, name='test_alert'),
]
