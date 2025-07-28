"""
users/urls.py

Handles URL routing for user-related views such as:
- Registration 
- Login
"""

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomLoginForm

app_name = 'users'

urlpatterns = [
    # Registration view (custom)
    path('register/', views.register, name='register'),

    path('verify/<int:uid>/<str:token>/', views.verify_email, name='verify_email'),

    # Login view
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=CustomLoginForm
    ), name='login'),
]