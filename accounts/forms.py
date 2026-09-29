from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import FarmerProfile


class FarmerRegistrationForm(UserCreationForm):

    email = forms.EmailField()

    phone = forms.CharField()

    village = forms.CharField()

    district = forms.CharField()

    state = forms.CharField()

    pincode = forms.CharField()

    class Meta:

        model = User

        fields = [

            "username",
            "email",
            "phone",
            "village",
            "district",
            "state",
            "pincode",
            "password1",
            "password2"

        ]

    def save(self, commit=True):

        user = super().save(commit=False)

        user.email = self.cleaned_data["email"]

        if commit:

            user.save()

            FarmerProfile.objects.create(

                user=user,

                phone=self.cleaned_data["phone"],

                village=self.cleaned_data["village"],

                district=self.cleaned_data["district"],

                state=self.cleaned_data["state"],

                pincode=self.cleaned_data["pincode"]

            )

        return user