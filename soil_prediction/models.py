from django.db import models
from django.contrib.auth.models import User


class SoilAnalysis(models.Model):
    SOIL_TEXTURE_CHOICES = [
        ("", "Not specified"),
        ("sandy", "Sandy"),
        ("silty", "Silty"),
        ("clay", "Clay"),
        ("loamy", "Loamy"),
        ("other", "Other / Unknown"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="soil_analyses",
    )

    farm_name = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=150, blank=True)
    target_crop = models.CharField(max_length=100, blank=True)

    nitrogen = models.FloatField()
    phosphorus = models.FloatField()
    potassium = models.FloatField()

    temperature = models.FloatField()
    humidity = models.FloatField()
    ph = models.FloatField()
    rainfall = models.FloatField()

    organic_carbon = models.FloatField(null=True, blank=True)
    electrical_conductivity = models.FloatField(null=True, blank=True)
    soil_texture = models.CharField(
        max_length=20,
        choices=SOIL_TEXTURE_CHOICES,
        blank=True,
    )

    report = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Soil report - {self.farm_name or 'Farm'} ({self.created_at:%Y-%m-%d})"