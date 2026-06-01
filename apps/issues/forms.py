from django import forms

from .models import Issue, IssueComment


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        exclude = ("reference_no", "status", "assigned_officer", "internal_notes", "escalated_to_district", "closed_at", "created_at", "updated_at")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Issue title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "category": forms.Select(attrs={"class": "form-select form-select-lg"}),
            "priority": forms.Select(attrs={"class": "form-select form-select-lg"}),
            "citizen": forms.Select(attrs={"class": "form-select form-select-lg"}),
            "ward": forms.Select(attrs={"class": "form-select form-select-lg"}),
        }


class IssueStatusForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ("status", "assigned_officer", "internal_notes", "escalated_to_district")
        widgets = {
            "status": forms.Select(attrs={"class": "form-select form-select-lg"}),
            "assigned_officer": forms.Select(attrs={"class": "form-select form-select-lg"}),
            "internal_notes": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }


class IssueCommentForm(forms.ModelForm):
    class Meta:
        model = IssueComment
        fields = ("body", "is_internal")
        widgets = {
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
