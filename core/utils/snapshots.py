from django.utils.timezone import now
from datetime import datetime
from ..models import AccountBalanceSnapshot
from plaid_link.models import Account

def create_monthly_snapshots(user):
    today = now().date()
    first_of_month = today.replace(day=1)

    accounts = Account.objects.filter(plaid_item__user=user)
    for acct in accounts:
        AccountBalanceSnapshot.objects.update_or_create(
            user=user,
            account=acct,
            date=first_of_month,
            defaults={"balance": acct.current_balance}
        )