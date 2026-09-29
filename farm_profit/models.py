from django.db import models
from django.contrib.auth.models import User


class FarmProfitCalculation(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    crop = models.CharField(
        max_length=100
    )

    area = models.FloatField(
        help_text="Area in acres"
    )

    seed_cost = models.FloatField(
        default=0
    )

    fertilizer_cost = models.FloatField(
        default=0
    )

    pesticide_cost = models.FloatField(
        default=0
    )

    labour_cost = models.FloatField(
        default=0
    )

    irrigation_cost = models.FloatField(
        default=0
    )

    machinery_cost = models.FloatField(
        default=0
    )

    other_cost = models.FloatField(
        default=0
    )

    expected_yield = models.FloatField(
        help_text="Expected yield in quintals"
    )

    selling_price = models.FloatField(
        help_text="Expected selling price per quintal"
    )

    total_cost = models.FloatField(
        default=0
    )

    expected_revenue = models.FloatField(
        default=0
    )

    expected_profit = models.FloatField(
        default=0
    )

    roi = models.FloatField(
        default=0
    )

    break_even_price = models.FloatField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.crop} - {self.expected_profit}"