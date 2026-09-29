from django.contrib import admin
from .models import GovernmentScheme


@admin.register(GovernmentScheme)
class GovernmentSchemeAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "is_active",
        "created_at",
    )

    list_filter = (
        "category",
        "is_active",
    )

    search_fields = (
        "title",
        "short_description",
        "description",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    list_editable = (
        "is_active",
    )

    ordering = (
        "title",
    )