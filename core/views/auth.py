"""
core/views/auth.py

Handles:
- User authentication and logout functionality
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

@require_POST
@login_required
def logout_view(request):
    logout(request)
    return redirect("users:login")

