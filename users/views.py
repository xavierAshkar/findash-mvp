"""
users/views.py

Handles public-facing views such as:
- Home page
- User registration
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages  
from .forms import CustomUserCreationForm

from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from .tokens import email_verification_token

from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from .models import CustomUser

def home(request):
    """
    Render the homepage (accessible to all users).
    """
    return render(request, 'home.html')


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # Auto-verify for v1.0.0
            user.is_verified = True
            user.save()

            
            login(request, user)
            messages.success(request, "Account created and verified! Welcome to Findash.")
            return redirect('plaid:link_account')
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", {"form": form})


def verify_email(request, uid, token):
    user = get_object_or_404(CustomUser, pk=uid)
    if email_verification_token.check_token(user, token):
        user.is_verified = True
        user.save()
        messages.success(request, "Your email is verified! You can log in now.")
        return redirect('users:login')
    return HttpResponseBadRequest("Invalid or expired verification link.")