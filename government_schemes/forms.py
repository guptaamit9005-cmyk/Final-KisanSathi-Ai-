from django import forms


class SchemeFinderForm(forms.Form):

    STATE_CHOICES = [
        ("Uttar Pradesh", "Uttar Pradesh"),
        ("Bihar", "Bihar"),
        ("Madhya Pradesh", "Madhya Pradesh"),
        ("Rajasthan", "Rajasthan"),
        ("Maharashtra", "Maharashtra"),
        ("Punjab", "Punjab"),
        ("Haryana", "Haryana"),
        ("West Bengal", "West Bengal"),
        ("Other", "Other"),
    ]

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    CATEGORY_CHOICES = [
        ("general", "General"),
        ("obc", "OBC"),
        ("sc", "SC"),
        ("st", "ST"),
    ]

    FARMER_TYPE_CHOICES = [
        ("small", "Small Farmer"),
        ("marginal", "Marginal Farmer"),
        ("tenant", "Tenant Farmer"),
        ("landless", "Landless Farmer"),
    ]

    CROP_CHOICES = [
        ("rice", "Rice"),
        ("wheat", "Wheat"),
        ("tomato", "Tomato"),
        ("potato", "Potato"),
        ("maize", "Maize"),
        ("other", "Other"),
    ]

    state = forms.ChoiceField(
        choices=STATE_CHOICES
    )

    district = forms.CharField(
        max_length=100,
        required=False
    )

    age = forms.IntegerField(
        min_value=18,
        max_value=100
    )

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES
    )

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES
    )

    farmer_type = forms.ChoiceField(
        choices=FARMER_TYPE_CHOICES
    )

    land_area = forms.FloatField(
        min_value=0
    )

    annual_income = forms.DecimalField(
        min_value=0,
        required=False
    )

    crop = forms.ChoiceField(
        choices=CROP_CHOICES
    )

    season = forms.ChoiceField(
        choices=[
            ("kharif", "Kharif"),
            ("rabi", "Rabi"),
            ("zaid", "Zaid"),
        ]
    )