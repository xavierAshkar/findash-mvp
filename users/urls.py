"""
users/urls.py

Handles URL routing for user-related views such as:
- Registration 
- Login
"""

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    # Registration view (custom)
    path('register/', views.register, name='register'),

    # Login view (Django built-in)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
]