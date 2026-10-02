from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from ai_assistant import views as ai_assistant_views

urlpatterns = [
    path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/javascript')),
    path('manifest.json', TemplateView.as_view(template_name='manifest.json', content_type='application/json')),
    path("admin/", admin.site.urls),

    # Home
    path("", include("core.urls")),

    # Authentication
    path(
        "accounts/",
        include(("accounts.urls", "accounts"), namespace="accounts")
    ),

    # Dashboard
    path(
        "dashboard/",
        include(("dashboard.urls", "dashboard"), namespace="dashboard")
    ),

    # Crop Prediction
    path("prediction/", include("prediction.urls")),
    path("weather/", include("weather.urls")),
    path("ai-sathi/", include("ai_assistant.urls")),
    path("ai-assistant/", ai_assistant_views.assistant_home),
    path("ai-assistant/api/", ai_assistant_views.assistant_api),
    path("notifications/", include("notifications.urls")),
    path("mandi/", include("mandi.urls")),
    path("learning/", include("encyclopedia.urls")),
    path(
        "land/",
        include(
            ("land_marketplace.urls", "land_marketplace"),
            namespace="land_marketplace"
        )
    ),
    path(
        "equipment/",
        include(
            ("equipment.urls", "equipment"),
            namespace="equipment"
        )
    ),
    path(
        "government-schemes/",
        include("government_schemes.urls")
    ),
    path("chatbot/", include("chatbot.urls")),
    path("karran/tts/", __import__("chatbot.views").views.karran_tts),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)