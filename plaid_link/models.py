"""
plaid_link/models.py

This module defines the database models for Plaid integration, including PlaidItem, Account, and Transaction.
These models are used to store user financial data securely and efficiently.
"""

from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings
from .utils import encrypt_token, decrypt_token
from core.models import Tag

class PlaidItem(models.Model):
    """
    Represents a Plaid Item, which is a connection to a financial institution.
    Each PlaidItem is associated with a user and contains an encrypted access token,
    institution name, and an optional item ID.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="plaid_items")
    _access_token = models.CharField(max_length=500)  # stored encrypted
    institution_name = models.CharField(max_length=100)
    item_id = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_access_token(self, raw_token: str):
        self._access_token = encrypt_token(raw_token)

    def get_access_token(self) -> str:
        return decrypt_token(self._access_token)

    def __str__(self):
        return f"{self.user.email} – {self.institution_name}"


class Account(models.Model):
    """
    Represents a financial account linked to a PlaidItem.
    Each Account is associated with a PlaidItem and contains details such as account ID,
    name, type, subtype, and balances.
    """
    class Meta:
        indexes = [
            models.Index(fields=["plaid_item"]),
        ]
    plaid_item = models.ForeignKey(PlaidItem, on_delete=models.CASCADE, related_name="accounts")
    account_id = models.CharField(max_length=100)  # from Plaid
    name = models.CharField(max_length=100)
    official_name = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=50)
    subtype = models.CharField(max_length=50)
    available_balance = models.FloatField(null=True, blank=True)
    current_balance = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.subtype})"
    
class Transaction(models.Model):
    """
    Represents a financial transaction linked to an Account.
    Each Transaction is associated with an Account and contains details such as transaction ID,
    name, amount, date, category, user tag, merchant name, and payment channel.
    """
    class Meta:
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["account"]),
            models.Index(fields=["tag"]),
        ]
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # from Plaid
    name = models.CharField(max_length=200)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    date = models.DateField()
    category_main = models.CharField(max_length=100, null=True, blank=True)
    category_detailed = models.CharField(max_length=200, null=True, blank=True)
    tag = models.ForeignKey(Tag, null=True, blank=True, on_delete=models.SET_NULL, related_name="transactions")
    merchant_name = models.CharField(max_length=200, null=True, blank=True)
    payment_channel = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} – {self.name} – ${self.amount}"
