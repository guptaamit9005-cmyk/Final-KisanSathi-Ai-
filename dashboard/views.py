
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from prediction.models import CropAnalysis


@login_required(login_url="accounts:login")
def dashboard_home(request):

    user = request.user

    # ==========================================
    # FARM PROFILE
    # ==========================================

    farm = getattr(user, "farmer_farm", None)

    # ==========================================
    # CROP ANALYSIS DATA
    # ==========================================

    # CropAnalysis uses the farmer relationship,
    # not a field named user.
    analyses = (
        CropAnalysis.objects
        .filter(farmer=user)
        .order_by("-created_at")
    )

    # ==========================================
    # CROP ANALYSIS STATISTICS
    # ==========================================

    total_analyses = analyses.count()

    pending_analyses = analyses.filter(
        status="pending"
    ).count()

    verified_analyses = analyses.filter(
        status="verified"
    ).count()

    # ==========================================
    # RECENT ANALYSIS ACTIVITY
    # ==========================================

    recent_analyses = analyses[:5]

    # ==========================================
    # USER DISPLAY DATA
    # ==========================================

    display_name = (
        user.first_name.strip()
        if user.first_name and user.first_name.strip()
        else user.username
    )

    user_initial = (
        display_name[0].upper()
        if display_name
        else "F"
    )

    # ==========================================
    # DASHBOARD CONTEXT
    # ==========================================

    context = {

        # User information
        "username": display_name,
        "user_initial": user_initial,
        "user_email": user.email,

        # Farm information
        "farm": farm,

        # Crop analysis statistics
        "total_analyses": total_analyses,
        "pending_analyses": pending_analyses,
        "verified_analyses": verified_analyses,

        # Recent activity
        "recent_analyses": recent_analyses,

        # Backward-compatible variables
        "total_predictions": total_analyses,
        "recent_predictions": recent_analyses,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )