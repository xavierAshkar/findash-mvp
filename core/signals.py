# core/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from core.utils.widget import create_default_widgets

User = get_user_model()

@receiver(post_save, sender=User)
def create_dashboard_widgets_on_user_creation(sender, instance, created, **kwargs):
    if created:
        create_default_widgets(instance)
