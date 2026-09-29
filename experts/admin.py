from django.contrib import admin

from .models import Expert


@admin.register(Expert)
class ExpertAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "expert_type",
        "organization",
        "specialization",
        "verification_status",
        "is_active",
        "created_at",
    )

    list_filter = (
        "expert_type",
        "verification_status",
        "is_active",
    )

    search_fields = (
        "name",
        "organization",
        "specialization",
        "crops",
        "location",
        "languages",
    )

    list_editable = (
        "verification_status",
        "is_active",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )