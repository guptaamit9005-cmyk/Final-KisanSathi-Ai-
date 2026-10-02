
import json
from collections import Counter, defaultdict
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from prediction.models import CropAnalysis


# ============================================================
# HELPER: Build display name
# ============================================================

def _display_name(user):
    name = (user.first_name or "").strip()
    return name if name else user.username


# ============================================================
# 1. MAIN DASHBOARD HOME
# ============================================================

@login_required(login_url="accounts:login")
def dashboard_home(request):

    user = request.user
    farm = getattr(user, "farmer_farm", None)

    analyses = (
        CropAnalysis.objects
        .filter(farmer=user)
        .order_by("-created_at")
    )

    total_analyses    = analyses.count()
    pending_analyses  = analyses.filter(status=CropAnalysis.STATUS_SENT_TO_EXPERT).count()
    verified_analyses = analyses.filter(status=CropAnalysis.STATUS_VERIFIED).count()
    rejected_analyses = analyses.filter(status=CropAnalysis.STATUS_REJECTED).count()

    # Last 6 months monthly breakdown (for inline CSS chart)
    now = timezone.now()
    monthly_stats = []
    for i in range(5, -1, -1):
        month_start = (now - timedelta(days=30 * i)).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        month_end = now if i == 0 else (now - timedelta(days=30 * (i - 1))).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        count = analyses.filter(created_at__gte=month_start, created_at__lt=month_end).count()
        monthly_stats.append({"month": month_start.strftime("%b"), "count": count})

    # Top 5 diseases
    disease_counts = Counter(
        a.final_disease for a in analyses
        if a.final_disease and a.final_disease.lower() not in ("", "not available", "unknown")
    )
    top_diseases = [{"name": d, "count": c} for d, c in disease_counts.most_common(5)]

    accuracy_rate = round((verified_analyses / total_analyses) * 100, 1) if total_analyses > 0 else 0
    history_analyses = analyses[:10]
    recent_analyses  = analyses[:5]
    display_name = _display_name(user)

    context = {
        "username":          display_name,
        "user_initial":      display_name[0].upper() if display_name else "F",
        "user_email":        user.email,
        "farm":              farm,
        "total_analyses":    total_analyses,
        "pending_analyses":  pending_analyses,
        "verified_analyses": verified_analyses,
        "rejected_analyses": rejected_analyses,
        "monthly_stats":     monthly_stats,
        "top_diseases":      top_diseases,
        "accuracy_rate":     accuracy_rate,
        "history_analyses":  history_analyses,
        "recent_analyses":   recent_analyses,
        "total_predictions": total_analyses,
        "recent_predictions": recent_analyses,
    }
    return render(request, "dashboard/dashboard.html", context)


# ============================================================
# 2. DEDICATED ANALYTICS DASHBOARD
# URL: /dashboard/analytics/
# ============================================================

@login_required(login_url="accounts:login")
def analytics_dashboard(request):

    user     = request.user
    analyses = (
        CropAnalysis.objects
        .filter(farmer=user)
        .order_by("-created_at")
    )

    all_list = list(analyses)          # single DB fetch for all computations
    total    = len(all_list)

    # ----------------------------------------------------------
    # KPI COUNTS
    # ----------------------------------------------------------
    verified  = sum(1 for a in all_list if a.status == CropAnalysis.STATUS_VERIFIED)
    pending   = sum(1 for a in all_list if a.status == CropAnalysis.STATUS_SENT_TO_EXPERT)
    rejected  = sum(1 for a in all_list if a.status == CropAnalysis.STATUS_REJECTED)
    accuracy  = round(verified / total * 100, 1) if total else 0

    # ----------------------------------------------------------
    # CHART 1 – Monthly Activity (last 12 months, bar chart)
    # ----------------------------------------------------------
    now = timezone.now()
    monthly_labels = []
    monthly_data   = []
    for i in range(11, -1, -1):
        month_dt = now - timedelta(days=30 * i)
        label = month_dt.strftime("%b %Y")
        monthly_labels.append(label)
        count = sum(
            1 for a in all_list
            if a.created_at.year == month_dt.year and a.created_at.month == month_dt.month
        )
        monthly_data.append(count)

    # ----------------------------------------------------------
    # CHART 2 – Disease Distribution (pie / doughnut)
    # ----------------------------------------------------------
    disease_counter = Counter(
        a.final_disease for a in all_list
        if a.final_disease and a.final_disease.lower() not in ("", "not available", "unknown", "none")
    )
    disease_labels = [d for d, _ in disease_counter.most_common(8)]
    disease_data   = [c for _, c in disease_counter.most_common(8)]

    # ----------------------------------------------------------
    # CHART 3 – Status Breakdown (donut)
    # ----------------------------------------------------------
    status_labels = ["Verified", "Pending Review", "Rejected"]
    status_data   = [verified, pending, rejected]

    # ----------------------------------------------------------
    # CHART 4 – Crop Distribution (horizontal bar)
    # ----------------------------------------------------------
    crop_counter = Counter(
        a.ai_crop for a in all_list
        if a.ai_crop and a.ai_crop.lower() not in ("", "unknown", "none", "not available")
    )
    crop_labels = [c for c, _ in crop_counter.most_common(6)]
    crop_data   = [n for _, n in crop_counter.most_common(6)]

    # ----------------------------------------------------------
    # CHART 5 – Weekly submissions (last 8 weeks, line chart)
    # ----------------------------------------------------------
    week_labels = []
    week_data   = []
    for i in range(7, -1, -1):
        week_start = (now - timedelta(weeks=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        week_end   = week_start + timedelta(days=7)
        label      = f"W{(now - timedelta(weeks=i)).isocalendar()[1]}"
        week_labels.append(label)
        week_data.append(sum(1 for a in all_list if week_start <= a.created_at < week_end))

    # ----------------------------------------------------------
    # CHART 6 – Verified vs Rejected trend (stacked bar, 6 months)
    # ----------------------------------------------------------
    trend_labels    = []
    trend_verified  = []
    trend_rejected  = []
    for i in range(5, -1, -1):
        month_dt   = now - timedelta(days=30 * i)
        trend_labels.append(month_dt.strftime("%b"))
        trend_verified.append(sum(
            1 for a in all_list
            if a.created_at.year == month_dt.year
            and a.created_at.month == month_dt.month
            and a.status == CropAnalysis.STATUS_VERIFIED
        ))
        trend_rejected.append(sum(
            1 for a in all_list
            if a.created_at.year == month_dt.year
            and a.created_at.month == month_dt.month
            and a.status == CropAnalysis.STATUS_REJECTED
        ))

    # ----------------------------------------------------------
    # CHART 7 – Day-of-week heatmap (submissions per weekday)
    # ----------------------------------------------------------
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekday_counter = Counter(a.created_at.weekday() for a in all_list)
    weekday_data = [weekday_counter.get(i, 0) for i in range(7)]

    # ----------------------------------------------------------
    # TOP 5 DISEASES with details
    # ----------------------------------------------------------
    top_diseases = [
        {"name": d, "count": c, "pct": round(c / total * 100, 1) if total else 0}
        for d, c in disease_counter.most_common(5)
    ]

    # ----------------------------------------------------------
    # FULL HISTORY (all analyses for the table)
    # ----------------------------------------------------------
    history = all_list   # full list

    # ----------------------------------------------------------
    # USER DISPLAY
    # ----------------------------------------------------------
    display_name = _display_name(user)

    context = {
        "username":     display_name,
        "user_initial": display_name[0].upper() if display_name else "F",
        "user_email":   user.email,

        # KPIs
        "total":     total,
        "verified":  verified,
        "pending":   pending,
        "rejected":  rejected,
        "accuracy":  accuracy,

        # Chart data – serialised as JSON for Chart.js
        "monthly_labels_json":   json.dumps(monthly_labels),
        "monthly_data_json":     json.dumps(monthly_data),

        "disease_labels_json":   json.dumps(disease_labels),
        "disease_data_json":     json.dumps(disease_data),

        "status_labels_json":    json.dumps(status_labels),
        "status_data_json":      json.dumps(status_data),

        "crop_labels_json":      json.dumps(crop_labels),
        "crop_data_json":        json.dumps(crop_data),

        "week_labels_json":      json.dumps(week_labels),
        "week_data_json":        json.dumps(week_data),

        "trend_labels_json":     json.dumps(trend_labels),
        "trend_verified_json":   json.dumps(trend_verified),
        "trend_rejected_json":   json.dumps(trend_rejected),

        "weekday_names_json":    json.dumps(weekday_names),
        "weekday_data_json":     json.dumps(weekday_data),

        # Table / list data
        "top_diseases": top_diseases,
        "history":      history,
    }
    return render(request, "dashboard/analytics.html", context)