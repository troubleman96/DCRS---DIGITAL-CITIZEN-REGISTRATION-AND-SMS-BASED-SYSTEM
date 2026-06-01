from django import forms

from .models import Citizen


class CitizenRegistrationForm(forms.ModelForm):
    class Meta:
        model = Citizen
        exclude = ("citizen_id", "user", "status", "created_at", "updated_at")
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Full name"}),
            "national_id": forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "National ID"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "+255..."}),
            "gender": forms.Select(attrs={"class": "form-select form-select-lg"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control form-control-lg", "type": "date"}),
            "region": forms.Select(attrs={"class": "form-select form-select-lg"}),
            "district": forms.Select(attrs={"class": "form-select form-select-lg"}),
            "ward": forms.Select(attrs={"class": "form-select form-select-lg"}),
            "mtaa": forms.Select(attrs={"class": "form-select form-select-lg"}),
            "profile_photo": forms.ClearableFileInput(attrs={"class": "form-control form-control-lg"}),
            "registration_notes": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

