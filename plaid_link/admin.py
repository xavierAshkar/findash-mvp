"""
plaid_link/admin.py

Handles the admin interface for Plaid Link integration.
- Custom admin configuration for PlaidItem model
"""

from django.contrib import admin
from .models import PlaidItem, Account, Transaction

@admin.register(PlaidItem)
class PlaidItemAdmin(admin.ModelAdmin):
    list_display = ("user", "institution_name", "item_id", "created_at")

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "current_balance", "plaid_item")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "name", "amount", "tag", "account")
    list_filter = ("date", "tag", "account__plaid_item")
