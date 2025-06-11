from django.contrib import admin
from .models import PlaidItem

@admin.register(PlaidItem)
class PlaidItemAdmin(admin.ModelAdmin):
    list_display = ("user", "institution_name", "item_id", "created_at")
