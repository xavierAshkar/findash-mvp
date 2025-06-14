"""
core/urls.py

Routes for the authenticated app experience.
Includes dashboard, accounts, transactions, etc.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard view (main post-login homepage)
    path('dashboard/', views.dashboard, name='dashboard'),
]
