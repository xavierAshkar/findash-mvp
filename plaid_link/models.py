# Create your Django models here.
from django.db import models
from django.conf import settings
from .utils import encrypt_token, decrypt_token  # coming next

class PlaidItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
    plaid_item = models.ForeignKey(PlaidItem, on_delete=models.CASCADE)
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
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)  # from Plaid
    name = models.CharField(max_length=200)
    amount = models.FloatField()
    date = models.DateField()
    category = models.CharField(max_length=100, null=True, blank=True)
    merchant_name = models.CharField(max_length=200, null=True, blank=True)
    payment_channel = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} – {self.name} – ${self.amount}"
