from django.contrib import admin
from django.urls import path, include

urlpatterns = [
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
    path(
    "ai-sathi/",
    include("ai_assistant.urls")
),
path(
    "mandi/",
    include("mandi.urls")
),
path(
    "schemes/",
    include("government_schemes.urls")
),
path(
    "learning/",
    include("encyclopedia.urls")
),
path(
    "land/",
    include(
        ("land_marketplace.urls", "land_marketplace"),
        namespace="land_marketplace"
    )
),
path(
    "government-schemes/",
    include(
        (
            "government_schemes.urls",
            "government_schemes"
        ),
        namespace="government_schemes"
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
    include(
        ("government_schemes.urls", "government_schemes"),
        namespace="government_schemes",
    ),
),
 path(
        "soil-prediction/",
        include("soil_prediction.urls")
    ),

]