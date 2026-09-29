from django.urls import path
from . import views

app_name = "prediction"

urlpatterns = [
    # Crop analysis homepage
    path(
        "",
        views.crop_analysis_home,
        name="home",
    ),

    # Upload and analyze crop image
    path(
        "analyze/",
        views.crop_analysis_view,
        name="analyze",
    ),

    # Analysis result/status
    path(
        "analyze/status/<int:pk>/",
        views.analysis_status_view,
        name="analysis_status",
    ),

    # Download colorful PDF report
    path(
        "report/<int:pk>/pdf/",
        views.download_analysis_pdf,
        name="download_pdf",
    ),

    # Expert dashboard
    path(
        "experts/",
        views.expert_dashboard_view,
        name="expert_dashboard",
    ),

    # Expert review
    path(
        "experts/review/<int:pk>/",
        views.expert_review_view,
        name="expert_review",
    ),
]