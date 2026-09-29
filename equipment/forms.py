from django import forms

from .models import Equipment, EquipmentBooking


class EquipmentSearchForm(forms.Form):

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search tractor, sprayer, harvester..."
            }
        )
    )

    equipment_type = forms.ChoiceField(
        required=False,
        choices=[
            ("", "All Equipment"),
            *Equipment.EQUIPMENT_TYPES,
        ]
    )

    district = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "District"
            }
        )
    )

    rent_type = forms.ChoiceField(
        required=False,
        choices=[
            ("", "Any Rent Type"),
            *Equipment.RENT_TYPES,
        ]
    )


class EquipmentForm(forms.ModelForm):

    class Meta:
        model = Equipment

        exclude = [
            "owner",
            "status",
            "is_verified",
            "created_at",
            "updated_at",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Describe the equipment..."
                }
            ),

            "image": forms.ClearableFileInput(),

            "rent_amount": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0"
                }
            ),

            "security_deposit": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0"
                }
            ),
        }


class EquipmentBookingForm(forms.ModelForm):

    class Meta:
        model = EquipmentBooking

        fields = [
            "start_date",
            "end_date",
            "quantity",
            "message",
        ]

        widgets = {
            "start_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "end_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "quantity": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "1"
                }
            ),

            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Tell the equipment owner about your requirement..."
                }
            ),
        }

    def clean(self):

        cleaned = super().clean()

        start = cleaned.get("start_date")
        end = cleaned.get("end_date")

        if start and end and end < start:

            raise forms.ValidationError(
                "End date cannot be before start date."
            )

        return cleaned