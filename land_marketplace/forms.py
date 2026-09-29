from decimal import Decimal
from django import forms


from .models import Land, LandRequest


class LandSearchForm(forms.Form):

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder":
                    "Search village, district, crop..."
            }
        )
    )

    district = forms.CharField(
        required=False
    )

    crop = forms.CharField(
        required=False
    )

    land_type = forms.ChoiceField(
        required=False,
        choices=[
            ("", "All Land Types"),
            *Land.LAND_TYPES,
        ]
    )

    listing_type = forms.ChoiceField(
        required=False,
        choices=[
            ("", "Rent / Share / Lease"),
            *Land.LISTING_TYPES,
        ]
    )

    min_area = forms.DecimalField(
        required=False,
        min_value=Decimal("0.01")
    )

    max_price = forms.DecimalField(
        required=False,
        min_value=Decimal("0")
    )


class LandListingForm(forms.ModelForm):

    class Meta:

        model = Land

        exclude = [
            "owner",
            "slug",
            "status",
            "is_verified",
            "created_at",
            "updated_at",
        ]

        widgets = {

            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder":
                        "Describe your land..."
                }
            ),

            "soil_description": forms.Textarea(
                attrs={
                    "rows": 3
                }
            ),

            "proposed_start_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),
        }


class LandRequestForm(forms.ModelForm):

    class Meta:

        model = LandRequest

        fields = [
            "requested_area",
            "duration_months",
            "proposed_start_date",
            "message",
        ]

        widgets = {

            "requested_area": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0.01"
                }
            ),

            "duration_months": forms.NumberInput(
                attrs={
                    "min": 1
                }
            ),

            "proposed_start_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder":
                        "Tell the land owner about your farming plan..."
                }
            ),
        }

    def __init__(self, *args, land=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.land = land

    def clean(self):

        cleaned = super().clean()

        area = cleaned.get(
            "requested_area"
        )

        duration = cleaned.get(
            "duration_months"
        )

        if self.land and area:

            if area > self.land.available_area:

                raise forms.ValidationError(
                    "Requested area is greater than "
                    "the currently available area."
                )

        if (
            self.land
            and duration
        ):

            if duration < self.land.minimum_duration_months:

                raise forms.ValidationError(
                    f"Minimum duration is "
                    f"{self.land.minimum_duration_months} months."
                )

            if duration > self.land.maximum_duration_months:

                raise forms.ValidationError(
                    f"Maximum duration is "
                    f"{self.land.maximum_duration_months} months."
                )

        return cleaned