from django.contrib import admin
from .models import FarmProfitCalculation


@admin.register(FarmProfitCalculation)
class FarmProfitCalculationAdmin(admin.ModelAdmin):

    list_display = (
        "crop",
        "area",
        "total_cost",
        "expected_revenue",
        "expected_profit",
        "roi",
        "created_at",
    )

    list_filter = (
        "crop",
        "created_at",
    )

    search_fields = (
        "crop",
        "user__username",
    )