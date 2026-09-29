# crops/models.py
#
# Add this model to your existing "crops" app (or merge these fields into
# your current image-analysis model if you already have one).
#
# After adding this, run:
#   python manage.py makemigrations
#   python manage.py migrate

from django.conf import settings
from django.db import models
from django.utils import timezone


class CropAnalysis(models.Model):
    """
    One farmer submission: the uploaded image, the AI's first-pass
    prediction, and (once reviewed) the expert's verified/corrected version.
    """

    STATUS_SENT_TO_EXPERT = "sent_to_expert"
    STATUS_VERIFIED = "verified"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_SENT_TO_EXPERT, "Sent to Expert for Review"),
        (STATUS_VERIFIED, "Verified by Expert"),
        (STATUS_REJECTED, "Rejected by Expert"),
    ]

    # --- Who submitted it ---
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="crop_analyses",
    )
    image = models.ImageField(upload_to="crop_images/%Y/%m/%d/")

    # --- AI prediction (filled immediately after upload, before any human sees it) ---
    ai_crop = models.CharField(max_length=120, blank=True)
    ai_disease = models.CharField(max_length=200, blank=True)
    ai_confidence = models.CharField(max_length=50, blank=True)
    ai_solution = models.TextField(blank=True)
    ai_pesticide = models.TextField(blank=True)
    ai_prevention = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SENT_TO_EXPERT,
    )

    # --- Expert's reviewed / corrected version ---
    expert = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_analyses",
    )
    expert_disease = models.CharField(max_length=200, blank=True)
    expert_solution = models.TextField(blank=True)
    expert_pesticide = models.TextField(blank=True)
    expert_prevention = models.TextField(blank=True)
    expert_notes = models.TextField(
        blank=True,
        help_text="Optional note shown to the farmer, e.g. why something was changed.",
    )
    expert_reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Analysis #{self.pk} — {self.ai_disease or 'pending'} ({self.get_status_display()})"

    # --- Helpers ---

    def mark_verified(self, expert_user):
        self.status = self.STATUS_VERIFIED
        self.expert = expert_user
        self.expert_reviewed_at = timezone.now()
        self.save()

    def mark_rejected(self, expert_user):
        self.status = self.STATUS_REJECTED
        self.expert = expert_user
        self.expert_reviewed_at = timezone.now()
        self.save()

    @property
    def is_verified(self):
        return self.status == self.STATUS_VERIFIED

    @property
    def is_pending(self):
        return self.status == self.STATUS_SENT_TO_EXPERT

    # These always return the best available answer: the expert's
    # corrected value once verified, otherwise the AI's own guess.
    @property
    def final_disease(self):
        return self.expert_disease or self.ai_disease

    @property
    def final_solution(self):
        return self.expert_solution or self.ai_solution

    @property
    def final_pesticide(self):
        return self.expert_pesticide or self.ai_pesticide

    @property
    def final_prevention(self):
        return self.expert_prevention or self.ai_prevention