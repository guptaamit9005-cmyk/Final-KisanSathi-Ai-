from django.shortcuts import render, get_object_or_404

from .models import FarmingTechnique


def farming_home(request):

    crop = request.GET.get(
        "crop",
        ""
    ).strip()

    category = request.GET.get(
        "category",
        ""
    ).strip()

    techniques = FarmingTechnique.objects.all()

    if crop:
        techniques = techniques.filter(
            crop_name__iexact=crop
        )

    if category:
        techniques = techniques.filter(
            category=category
        )

    crops = (
        FarmingTechnique.objects
        .values_list(
            "crop_name",
            flat=True
        )
        .distinct()
        .order_by("crop_name")
    )

    categories = FarmingTechnique.CATEGORY_CHOICES

    context = {
        "techniques": techniques,
        "crops": crops,
        "categories": categories,
        "selected_crop": crop,
        "selected_category": category,
    }

    return render(
        request,
        "smart_farming/home.html",
        context
    )


def technique_detail(request, pk):

    technique = get_object_or_404(
        FarmingTechnique,
        pk=pk
    )

    return render(
        request,
        "smart_farming/detail.html",
        {
            "technique": technique
        }
    )