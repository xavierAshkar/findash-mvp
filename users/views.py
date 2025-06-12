# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from plaid_link.models import PlaidItem


def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after signup
            return redirect('dashboard')  # You can change this later
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def dashboard(request):
    has_plaid_item = PlaidItem.objects.filter(user=request.user).exists()
    if not has_plaid_item:
        # No accounts linked — redirect to link account page
        return redirect('plaid:link_account')  # make sure 'plaid' is your app namespace if you have one
    
    # If accounts exist, render dashboard page
    return render(request, 'users/dashboard.html')