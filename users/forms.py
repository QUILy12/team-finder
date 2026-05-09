import re

from django import forms
from django.core.exceptions import ValidationError

from team_finder.services import validate_github_url
from users.constants import (
    PHONE_CLEAN_PATTERN,
    PHONE_EIGHT_PREFIX,
    PHONE_REGEX,
    PHONE_RUSSIAN_PREFIX,
)
from users.models import User


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if not phone:
            return phone

        phone = re.sub(PHONE_CLEAN_PATTERN, "", phone)

        if not re.match(PHONE_REGEX, phone):
            raise ValidationError("Неверный формат телефона")

        if phone.startswith(PHONE_EIGHT_PREFIX):
            phone = f"{PHONE_RUSSIAN_PREFIX}{phone[1:]}"

        if User.objects.exclude(pk=self.instance.pk).filter(phone=phone).exists():
            raise ValidationError("Телефон уже используется")

        return phone

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url"))
