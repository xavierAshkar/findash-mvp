"""
core/admin.py

Handles the admin interface for core integration.
- Custom admin configuration for Budget and Tag models
"""

from django.contrib import admin
from .models import Budget, Tag

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("name", "amount", "user", "created_at")
    list_filter = ("user",)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    list_filter = ("user",)