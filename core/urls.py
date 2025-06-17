"""
core/urls.py

Routes for the authenticated app experience.
Includes dashboard, accounts, transactions, budgets, etc.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard view (main post-login homepage)
    path('dashboard/', views.dashboard, name='dashboard'),

    # Cash accounts view
    path("cash/", views.cash_accounts, name="cash_accounts"),

    # Credit accounts view
    path("credit/", views.credit_accounts, name="credit_accounts"),

    # Transactions view
    path("transactions/", views.transactions, name="transactions"),

    # Tagging a transaction
    path("transactions/tag/<int:transaction_id>/", views.tag_transaction, name="tag_transaction"),


    # Budgets view
    path('budgets/', views.budgets, name='budgets'),
]
