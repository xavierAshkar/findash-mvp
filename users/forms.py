"""
users/forms.py

Contains form(s) for user creation and authentication.
"""

from django import forms
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomUserCreationForm(forms.ModelForm):
    """
    Form for registering a new user with email and full name.
    Includes password confirmation and hashing.
    """
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name']

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
