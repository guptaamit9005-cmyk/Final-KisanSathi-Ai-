from django.db import models


class FarmingTechnique(models.Model):

    CATEGORY_CHOICES = [
        ("irrigation", "Smart Irrigation"),
        ("fertilizer", "Smart Fertilization"),
        ("pest", "Pest Management"),
        ("monitoring", "Crop Monitoring"),
        ("precision", "Precision Farming"),
        ("drone", "Drone Technology"),
        ("soil", "Soil Management"),
        ("harvesting", "Smart Harvesting"),
        ("other", "Other"),
    ]

    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    crop_name = models.CharField(
        max_length=100
    )

    title = models.CharField(
        max_length=200
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    short_description = models.TextField()

    technology_used = models.CharField(
        max_length=255,
        blank=True
    )

    benefits = models.TextField(
        help_text="Write each benefit on a new line."
    )

    implementation = models.TextField(
        help_text="Explain how farmers can implement this technique."
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default="beginner"
    )

    estimated_cost = models.CharField(
        max_length=100,
        blank=True
    )

    suitable_season = models.CharField(
        max_length=150,
        blank=True
    )

    video_title = models.CharField(
        max_length=200,
        blank=True
    )

    video_url = models.URLField(
        blank=True
    )

    thumbnail_url = models.URLField(
        blank=True
    )

    is_featured = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    def __str__(self):
        return f"{self.crop_name} - {self.title}"