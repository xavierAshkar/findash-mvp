"""
users/forms.py

Contains form(s) for user creation and authentication.
"""

import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

CustomUser = get_user_model()

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name']

    def clean_password1(self):
        password = self.cleaned_data.get("password1")

        # Length
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        # Uppercase
        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        # Number
        if not re.search(r"\d", password):
            raise forms.ValidationError("Password must contain at least one number.")
        # Special character
        if not re.search(r"[^A-Za-z0-9]", password):
            raise forms.ValidationError("Password must contain at least one special character.")

        return password

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class CustomLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_verified:
            raise forms.ValidationError("Please verify your email before logging in.")