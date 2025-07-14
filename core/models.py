"""
core/models.py

Defines core application models such as Tag and Budget.
These models are used to categorize and manage user budgets and financial tags.
"""

from django.db import models
from django.conf import settings

class Tag(models.Model):
    """
    Represents a tag that can be associated with budgets or transactions.
    Tags can be used to categorize expenses or income for better financial tracking.
    """
    class Meta:
        unique_together = ("user", "name")
        indexes = [models.Index(fields=["user"])]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Budget(models.Model):
    """
    Represents a budget set by the user.
    Each budget can have multiple tags associated with it, and it tracks the total amount.
    Budgets can be used to manage financial goals and spending limits.
    """
    class Meta:
        indexes = [models.Index(fields=["user"])]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets")
    name = models.CharField(max_length=100)  # e.g. "Groceries"
    tags = models.ManyToManyField(Tag, related_name="budgets")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ${self.amount}"