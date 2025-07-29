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

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

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
            # Auto-verify for MVP
            user.is_verified = True
            user.save()

            login(request, user)
            messages.success(request, "Account created! Welcome to Findash.")
            return redirect('core:dashboard')
        else:
            # Show clear duplicate email error
            if form.errors.get('email'):
                messages.error(request, "This email is already registered.")
            else:
                messages.error(request, "Please fix the errors below.")
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

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")

        # Check if email exists first
        if not CustomUser.objects.filter(email=email).exists():
            messages.error(request, "No account found with this email.")
            return render(
                request,
                "registration/login.html",
                {"form": AuthenticationForm(request, data=request.POST)},
            )

        # Authenticate credentials
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Welcome back!")
            return redirect("core:dashboard")
        else:
            messages.error(request, "Incorrect password.")
            return render(
                request,
                "registration/login.html",
                {"form": AuthenticationForm(request, data=request.POST)},
            )

    # GET request → empty form
    form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})
