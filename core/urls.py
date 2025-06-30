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

    # Accounts view
    path("accounts/", views.accounts_view, name="accounts"),


    # Transactions view
    path("transactions/", views.transactions_view, name="transactions"),

    # Adding a transaction
    path("transactions/new/", views.add_transaction_view, name="add_transaction"),

    # Tagging a transaction
    path("transactions/tag/<int:transaction_id>/", views.tag_transaction, name="tag_transaction"),

    # Budgets view
    path('budgets/', views.budgets, name='budgets'),
]
