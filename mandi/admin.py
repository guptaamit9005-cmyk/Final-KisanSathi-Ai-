from django.contrib import admin
from .models import MandiPrice


@admin.register(MandiPrice)
class MandiPriceAdmin(admin.ModelAdmin):

    list_display = (
        "commodity",
        "market",
        "district",
        "state",
        "min_price",
        "modal_price",
        "max_price",
        "arrival_date",
    )

    list_filter = (
        "commodity",
        "state",
        "district",
        "arrival_date",
    )

    search_fields = (
        "commodity",
        "market",
        "district",
        "state",
    )