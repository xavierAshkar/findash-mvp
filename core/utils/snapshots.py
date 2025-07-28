from django.utils.timezone import now
from datetime import datetime
from ..models import AccountBalanceSnapshot
from plaid_link.models import Account
from dateutil.relativedelta import relativedelta

def create_monthly_snapshots(user):
    today = now().date()
    first_of_month = today.replace(day=1)

    accounts = Account.objects.filter(plaid_item__user=user)
    for acct in accounts:
        AccountBalanceSnapshot.objects.get_or_create(
            user=user,
            account=acct,
            date=first_of_month,
            defaults={"balance": acct.current_balance}
        )

def get_account_balance_deltas(user):
    """
    Compare current balances with last month's snapshot.
    """
    today = now().date()
    this_month_start = today.replace(day=1)
    last_month_start = this_month_start - relativedelta(months=1)

    deltas = []
    for acct in Account.objects.filter(plaid_item__user=user):
        try:
            prev_snapshot = AccountBalanceSnapshot.objects.get(
                user=user, account=acct, date=last_month_start
            )
            delta = acct.current_balance - prev_snapshot.balance
            pct_change = (delta / prev_snapshot.balance * 100) if prev_snapshot.balance != 0 else None
        except AccountBalanceSnapshot.DoesNotExist:
            delta = None
            pct_change = None

        deltas.append({
            "account": acct,
            "current": acct.current_balance,
            "delta": delta,
            "pct_change": pct_change,
        })

    return deltas

def pct_change(deltas, types=None, subtypes=None):
    """Calculate % change for a group of accounts (by type/subtype)"""
    filtered = [
        d for d in deltas
        if (types is None or d["account"].type in types)
        and (subtypes is None or d["account"].subtype in subtypes)
    ]
    prev_total = sum((d["current"] - (d["delta"] or 0)) for d in filtered)
    delta_total = sum(d["delta"] or 0 for d in filtered)

    return (delta_total / prev_total * 100) if prev_total else None
