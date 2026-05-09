from django import forms

from projects.models import Project
from team_finder.services import validate_github_url


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Название проекта",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Описание проекта",
                }
            ),
            "github_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://github.com/...",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url"))
