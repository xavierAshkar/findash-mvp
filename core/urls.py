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

    # Toggle edit mode for dashboard widgets
    path("dashboard/toggle-edit-mode/", views.toggle_edit_mode, name="toggle_edit_mode"),

    # Remove a widget from the dashboard
    path("dashboard/remove-widget/", views.remove_widget, name="remove_widget"),

    # Add a widget to the dashboard
    path("dashboard/add-widget/", views.add_widget, name="add_widget"),

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

    # Django built-in logout view
    path("logout/", views.logout_view, name="logout"),
    
    # Profile + Account Management
    path("profile/", views.profile_view, name="profile"),
    path("delete-account/", views.delete_account_view, name="delete_account"),
]
