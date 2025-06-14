"""
users/views.py

Handles public-facing views such as:
- Home page
- User registration
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

def home(request):
    """
    Render the homepage (accessible to all users).
    """
    return render(request, 'home.html')


def register(request):
    """
    Handle user registration.
    
    - On GET: display a blank registration form
    - On POST: validate and save the user, log them in,
      and redirect to the dashboard if successful
    """
    if request.method == "POST":
        # Create a form instance with submitted POST data
        form = CustomUserCreationForm(request.POST)

        # Validate the form (built-in Django validation + custom logic)
        if form.is_valid():
            # Save the new user to the database
            user = form.save()

            # Log the user in after successful registration
            login(request, user)

            # Redirect user to their dashboard
            return redirect('core:dashboard')
    else:
        # If GET request, instantiate a blank registration form
        form = CustomUserCreationForm()

    # Render the registration template with the form (either blank or with errors)
    return render(request, "registration/register.html", {"form": form})
