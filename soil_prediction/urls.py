from django.urls import path
from . import views

app_name = "soil_prediction"

urlpatterns = [
    path(
        "",
        views.soil_prediction_home,
        name="home",
    ),

    path(
        "dashboard/",
        views.soil_dashboard,
        name="dashboard",
    ),

    path(
        "history/",
        views.soil_analysis_history,
        name="history",
    ),

    path(
        "report/<int:analysis_id>/",
        views.soil_analysis_report,
        name="report",
    ),

    path(
        "compare/<int:first_id>/<int:second_id>/",
        views.compare_soil_reports,
        name="compare",
    ),

    path(
        "export/csv/",
        views.export_soil_csv,
        name="export_csv",
    ),

    path(
        "report/<int:analysis_id>/pdf/",
        views.download_soil_pdf,
        name="download_pdf",
    ),
]