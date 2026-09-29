# crops/forms.py

from django import forms

from .models import CropAnalysis


class CropImageForm(forms.ModelForm):
    """Farmer-facing form: just the image. Everything else is filled by the AI."""

    class Meta:
        model = CropAnalysis
        fields = ["image"]


class ExpertReviewForm(forms.ModelForm):
    """
    Expert-facing form. Pre-filled with the AI's own prediction (see the
    view) so the expert only has to correct what's wrong instead of
    retyping everything from scratch.
    """

    class Meta:
        model = CropAnalysis
        fields = [
            "expert_disease",
            "expert_solution",
            "expert_pesticide",
            "expert_prevention",
            "expert_notes",
        ]
        widgets = {
            "expert_disease": forms.TextInput(attrs={
                "class": "review-input",
                "placeholder": "Confirmed / corrected disease name",
            }),
            "expert_solution": forms.Textarea(attrs={
                "class": "review-textarea", "rows": 3,
                "placeholder": "Treatment / solution steps for the farmer",
            }),
            "expert_pesticide": forms.Textarea(attrs={
                "class": "review-textarea", "rows": 3,
                "placeholder": "Fertilizer / pesticide recommendation",
            }),
            "expert_prevention": forms.Textarea(attrs={
                "class": "review-textarea", "rows": 3,
                "placeholder": "How to prevent this next season",
            }),
            "expert_notes": forms.Textarea(attrs={
                "class": "review-textarea", "rows": 2,
                "placeholder": "Optional note for the farmer (why something was changed, extra caution, etc.)",
            }),
        }