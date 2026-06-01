from django import forms

from .models import Citizen

_CTRL = {"class": "form-control"}
_SEL  = {"class": "form-select"}
_CTRL_LG = {"class": "form-control form-control-lg"}
_SEL_LG  = {"class": "form-select form-select-lg"}


class CitizenRegistrationForm(forms.ModelForm):
    class Meta:
        model = Citizen
        exclude = ("citizen_id", "user", "status", "created_at", "updated_at")
        widgets = {
            "full_name":           forms.TextInput(attrs={**_CTRL_LG, "placeholder": "Full name"}),
            "national_id":         forms.TextInput(attrs={**_CTRL_LG, "placeholder": "National ID"}),
            "phone_number":        forms.TextInput(attrs={**_CTRL_LG, "placeholder": "+255..."}),
            "gender":              forms.Select(attrs=_SEL_LG),
            "date_of_birth":       forms.DateInput(attrs={**_CTRL_LG, "type": "date"}),
            "region":              forms.Select(attrs=_SEL_LG),
            "district":            forms.Select(attrs=_SEL_LG),
            "ward":                forms.Select(attrs=_SEL_LG),
            "mtaa":                forms.Select(attrs=_SEL_LG),
            "profile_photo":       forms.ClearableFileInput(attrs=_CTRL_LG),
            "registration_notes":  forms.Textarea(attrs={**_CTRL, "rows": 4}),
        }


class CitizenEditForm(forms.ModelForm):
    class Meta:
        model = Citizen
        exclude = ("citizen_id", "user", "created_at", "updated_at")
        widgets = {
            "full_name":           forms.TextInput(attrs=_CTRL),
            "national_id":         forms.TextInput(attrs=_CTRL),
            "phone_number":        forms.TextInput(attrs=_CTRL),
            "gender":              forms.Select(attrs=_SEL),
            "date_of_birth":       forms.DateInput(attrs={**_CTRL, "type": "date"}),
            "status":              forms.Select(attrs=_SEL),
            "region":              forms.Select(attrs=_SEL),
            "district":            forms.Select(attrs=_SEL),
            "ward":                forms.Select(attrs=_SEL),
            "mtaa":                forms.Select(attrs=_SEL),
            "profile_photo":       forms.ClearableFileInput(attrs=_CTRL),
            "registration_notes":  forms.Textarea(attrs={**_CTRL, "rows": 3}),
        }

