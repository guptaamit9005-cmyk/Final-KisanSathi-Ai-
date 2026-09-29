from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Expert


@login_required
def expert_list(request):

    experts = Expert.objects.filter(
        is_active=True
    )

    # ==========================================
    # SEARCH
    # ==========================================

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        experts = experts.filter(
            name__icontains=search
        ) | experts.filter(
            organization__icontains=search
        ) | experts.filter(
            specialization__icontains=search
        ) | experts.filter(
            crops__icontains=search
        ) | experts.filter(
            location__icontains=search
        )


    # ==========================================
    # EXPERT TYPE
    # ==========================================

    expert_type = request.GET.get(
        "type",
        ""
    )

    if expert_type:

        experts = experts.filter(
            expert_type=expert_type
        )


    # ==========================================
    # LOCATION
    # ==========================================

    location = request.GET.get(
        "location",
        ""
    ).strip()

    if location:

        experts = experts.filter(
            location__icontains=location
        )


    # ==========================================
    # CROP
    # ==========================================

    crop = request.GET.get(
        "crop",
        ""
    ).strip()

    if crop:

        experts = experts.filter(
            crops__icontains=crop
        )


    # ==========================================
    # VERIFIED ONLY
    # ==========================================

    verified = request.GET.get(
        "verified",
        ""
    )

    if verified == "true":

        experts = experts.filter(
            verification_status="verified"
        )


    context = {

        "experts": experts,

        "search": search,

        "expert_type": expert_type,

        "location": location,

        "crop": crop,

        "verified": verified,

        "expert_types":
            Expert.EXPERT_TYPES,

    }


    return render(
        request,
        "experts/expert_list.html",
        context
    )


# =====================================================
# EXPERT DETAIL
# =====================================================

@login_required
def expert_detail(
    request,
    expert_id
):

    expert = get_object_or_404(
        Expert,
        id=expert_id,
        is_active=True
    )


    return render(
        request,
        "experts/expert_detail.html",
        {
            "expert": expert
        }
    )