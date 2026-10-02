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


class SeedAnalysisForm(forms.Form):
    """
    Form for analyzing seed quality, germination suitability, and defects for agriculture.
    Supports seed photo upload + agronomic condition indicators.
    """

    CROP_CHOICES = [
        ("Wheat", "Wheat (गेहूं)"),
        ("Rice", "Rice / Paddy (धान)"),
        ("Maize", "Maize / Corn (मक्का)"),
        ("Soybean", "Soybean (सोयाबीन)"),
        ("Mustard", "Mustard / Rapeseed (सरसों)"),
        ("Gram", "Gram / Chickpea (चना)"),
        ("Cotton", "Cotton (कपास)"),
        ("Tomato", "Tomato (टमाटर)"),
        ("Chilli", "Chilli / Pepper (मिर्च)"),
        ("Onion", "Onion (प्याज)"),
        ("Groundnut", "Groundnut / Peanut (मूंगफली)"),
        ("General", "Other Agri Seeds (अन्य कृषि बीज)"),
    ]

    VISUAL_CHOICES = [
        ("good", "Plump, lustrous & clean (स्वस्थ, चमकदार व भरा हुआ दाना)"),
        ("dull", "Dull & faded luster (चमकहीन / पुराना स्टॉक)"),
        ("spotted", "Discolored / black or brown spots (काले-भूरे धब्बे)"),
        ("shriveled", "Shriveled & wrinkled (सिकुड़े व कमजोर बीज)"),
        ("damaged", "Broken, cracked or diseased (क्षतिग्रस्त व विकृत दाने)"),
    ]

    BROKEN_CHOICES = [
        ("none", "None / Intact (< 2% cracked)"),
        ("few", "Few broken seeds (2% - 10%)"),
        ("high", "High broken / split seeds (> 10%)"),
    ]

    MOISTURE_CHOICES = [
        ("normal", "Dry & crisp (सामान्य सूखा बीज, 8-12% moisture)"),
        ("damp", "Damp / soft to touch (हल्की नमी)"),
        ("musty_smell", "Musty / moldy odor (सीलन व फफूंद गंध)"),
        ("rotten", "Decayed / sour smell (सड़न व तीव्र दुर्गंध)"),
    ]

    FLOAT_CHOICES = [
        ("sink", "All seeds sink in water (सभी बीज डूबते हैं - भारी व स्वस्थ)"),
        ("few_float", "Few seeds float (कुछ बीज तैरते हैं - 5-10%)"),
        ("many_float", "Many seeds float (अनेक बीज तैरते हैं - > 15% खोखले)"),
    ]

    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            "class": "seed-file-input",
            "id": "seedImageInput",
            "accept": "image/*",
        }),
    )

    crop_type = forms.ChoiceField(
        choices=CROP_CHOICES,
        initial="Wheat",
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "seedCropType",
        }),
    )

    visual_condition = forms.ChoiceField(
        choices=VISUAL_CHOICES,
        initial="good",
        required=False,
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "seedVisualCondition",
        }),
    )

    has_insect_holes = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input",
            "id": "seedInsectHoles",
        }),
    )

    broken_coat_level = forms.ChoiceField(
        choices=BROKEN_CHOICES,
        initial="none",
        required=False,
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "seedBrokenLevel",
        }),
    )

    moisture_status = forms.ChoiceField(
        choices=MOISTURE_CHOICES,
        initial="normal",
        required=False,
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "seedMoistureStatus",
        }),
    )

    float_test_result = forms.ChoiceField(
        choices=FLOAT_CHOICES,
        initial="sink",
        required=False,
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "seedFloatTest",
        }),
    )