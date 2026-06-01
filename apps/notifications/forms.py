from django import forms


class ComposeSMSForm(forms.Form):
    recipient = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "+255..."}),
    )
    message_body = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": 5}))


class BroadcastSMSForm(forms.Form):
    ward = forms.CharField(
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Ward name (optional)"}),
    )
    message_body = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": 5}))
