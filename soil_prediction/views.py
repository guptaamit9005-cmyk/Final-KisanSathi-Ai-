import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from .forms import SoilAnalysisForm
from .models import SoilAnalysis
from .services import generate_soil_report
from .pdf_utils import build_soil_pdf


# =========================================================
# 1. SOIL ANALYSIS HOME
# URL: /soil-prediction/
# =========================================================

@require_http_methods(["GET", "POST"])
def soil_prediction_home(request):

    if request.method == "POST":
        form = SoilAnalysisForm(request.POST)

        if form.is_valid():

            analysis = form.save(commit=False)

            # Attach logged-in user
            if request.user.is_authenticated:
                analysis.user = request.user

            # Generate screening report
            analysis.report = generate_soil_report(form.cleaned_data)

            # Save soil analysis
            analysis.save()

            messages.success(
                request,
                "Your soil analysis report has been generated successfully."
            )

            return redirect(
                "soil_prediction:report",
                analysis_id=analysis.id,
            )

        messages.error(
            request,
            "Please correct the highlighted form errors."
        )

    else:
        form = SoilAnalysisForm()

    return render(
        request,
        "soil_prediction/index.html",
        {
            "form": form,
        },
    )


# =========================================================
# 2. SOIL INTELLIGENCE DASHBOARD
# URL: /soil-prediction/dashboard/
# =========================================================

@login_required
def soil_dashboard(request):

    analyses = SoilAnalysis.objects.filter(
        user=request.user
    ).order_by("created_at")

    latest = analyses.last()
    total_reports = analyses.count()

    # Prepare chart data
    chart_data = list(
        analyses.values(
            "created_at",
            "farm_name",
            "nitrogen",
            "phosphorus",
            "potassium",
            "ph",
        )
    )

    for row in chart_data:
        row["created_at"] = row["created_at"].strftime("%d %b %Y")
        row["farm_name"] = row["farm_name"] or "Unnamed farm"

    # Soil monitoring alerts
    alerts = []

    if latest:

        # pH screening
        if latest.ph < 5.5:

            alerts.append({
                "level": "warning",
                "title": "Acidic pH screening",
                "message": (
                    "Confirm the pH with a soil laboratory "
                    "and seek crop-specific guidance."
                ),
            })

        elif latest.ph > 7.5:

            alerts.append({
                "level": "warning",
                "title": "Alkaline pH screening",
                "message": (
                    "Confirm the result and request local "
                    "crop-specific interpretation."
                ),
            })

        else:

            alerts.append({
                "level": "success",
                "title": "pH screening range",
                "message": (
                    "Entered pH is within the broad "
                    "near-neutral screening range."
                ),
            })

        # Organic carbon reminder
        if latest.organic_carbon is None:

            alerts.append({
                "level": "info",
                "title": "Organic carbon not recorded",
                "message": (
                    "Consider including organic carbon "
                    "in your next laboratory soil test."
                ),
            })

        # Electrical conductivity reminder
        if latest.electrical_conductivity is None:

            alerts.append({
                "level": "info",
                "title": "EC not recorded",
                "message": (
                    "Consider EC testing if salinity "
                    "is a concern."
                ),
            })

    return render(
        request,
        "soil_prediction/dashboard.html",
        {
            "analyses": analyses.order_by("-created_at")[:10],
            "latest": latest,
            "total_reports": total_reports,
            "chart_data": chart_data,
            "alerts": alerts,
        },
    )


# =========================================================
# 3. SOIL ANALYSIS HISTORY
# URL: /soil-prediction/history/
# =========================================================

@login_required
def soil_analysis_history(request):

    analyses = SoilAnalysis.objects.filter(
        user=request.user
    ).order_by("-created_at")

    # Optional farm search
    farm = request.GET.get("farm", "").strip()

    if farm:
        analyses = analyses.filter(
            farm_name__icontains=farm
        )

    return render(
        request,
        "soil_prediction/history.html",
        {
            "analyses": analyses,
            "farm_filter": farm,
        },
    )


# =========================================================
# 4. SINGLE SOIL REPORT
# URL: /soil-prediction/report/<id>/
# =========================================================

def soil_analysis_report(request, analysis_id):

    analysis = get_object_or_404(
        SoilAnalysis,
        id=analysis_id,
    )

    # Prevent access to another user's private report
    if analysis.user_id:

        if (
            not request.user.is_authenticated
            or analysis.user_id != request.user.id
        ):
            return render(
                request,
                "soil_prediction/forbidden.html",
                status=403,
            )

    return render(
        request,
        "soil_prediction/report.html",
        {
            "analysis": analysis,
        },
    )


# =========================================================
# 5. COMPARE TWO SOIL REPORTS
# URL: /soil-prediction/compare/<first_id>/<second_id>/
# =========================================================

@login_required
def compare_soil_reports(request, first_id, second_id):

    first = get_object_or_404(
        SoilAnalysis,
        id=first_id,
        user=request.user,
    )

    second = get_object_or_404(
        SoilAnalysis,
        id=second_id,
        user=request.user,
    )

    fields = [
        ("Nitrogen", "nitrogen"),
        ("Phosphorus", "phosphorus"),
        ("Potassium", "potassium"),
        ("pH", "ph"),
        ("Temperature", "temperature"),
        ("Humidity", "humidity"),
        ("Rainfall", "rainfall"),
    ]

    comparisons = []

    for label, field in fields:

        old_value = getattr(first, field)
        new_value = getattr(second, field)

        difference = round(
            new_value - old_value,
            2,
        )

        comparisons.append({
            "label": label,
            "old": old_value,
            "new": new_value,
            "difference": difference,
        })

    return render(
        request,
        "soil_prediction/compare.html",
        {
            "first": first,
            "second": second,
            "comparisons": comparisons,
        },
    )


# =========================================================
# 6. EXPORT SOIL REPORTS AS CSV
# URL: /soil-prediction/export/csv/
# =========================================================

@login_required
def export_soil_csv(request):

    analyses = SoilAnalysis.objects.filter(
        user=request.user
    ).order_by("-created_at")

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="kisansathi_soil_reports.csv"'
    )

    writer = csv.writer(response)

    # CSV headings
    writer.writerow([
        "Report ID",
        "Date",
        "Farm",
        "Location",
        "Target Crop",
        "Nitrogen",
        "Phosphorus",
        "Potassium",
        "pH",
        "Temperature",
        "Humidity",
        "Rainfall",
        "Organic Carbon",
        "Electrical Conductivity",
        "Soil Texture",
    ])

    # CSV data
    for item in analyses:

        writer.writerow([
            item.id,
            item.created_at.strftime("%Y-%m-%d %H:%M"),
            item.farm_name,
            item.location,
            item.target_crop,
            item.nitrogen,
            item.phosphorus,
            item.potassium,
            item.ph,
            item.temperature,
            item.humidity,
            item.rainfall,
            item.organic_carbon,
            item.electrical_conductivity,
            item.get_soil_texture_display(),
        ])

    return response


# =========================================================
# 7. DOWNLOAD SINGLE SOIL REPORT AS PDF
# URL: /soil-prediction/report/<id>/pdf/
# =========================================================

def download_soil_pdf(request, analysis_id):

    analysis = get_object_or_404(
        SoilAnalysis,
        id=analysis_id,
    )

    # Protect private reports
    if analysis.user_id:

        if (
            not request.user.is_authenticated
            or analysis.user_id != request.user.id
        ):
            return render(
                request,
                "soil_prediction/forbidden.html",
                status=403,
            )

    # Generate PDF bytes
    pdf_bytes = build_soil_pdf(analysis)

    # Prepare downloadable response
    response = HttpResponse(
        pdf_bytes,
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        f'attachment; filename="KisanSathi_Soil_Report_{analysis.id}.pdf"'
    )

    response["Content-Length"] = str(len(pdf_bytes))

    return response