"""
core/views/profile.py

Handles:
- User profile view and account deletion functionality
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import logout

@require_POST
@login_required
def delete_account_view(request):
    user = request.user
    logout(request)
    user.delete()
    return redirect("users:register")

@login_required
def profile_view(request):
    return render(request, "core/profile/index.html")