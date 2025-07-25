from datetime import datetime
from django.utils import timezone
from decimal import Decimal
from plaid_link.models import Account, Transaction
from core.models import Budget
from core.models import AccountBalanceSnapshot
from django.utils.timezone import now
from collections import defaultdict

def get_net_worth_data(user):
    accounts = Account.objects.filter(plaid_item__user=user)

    asset_accounts = [a for a in accounts if a.type == "depository"]
    credit_card_accounts = [a for a in accounts if a.type == "credit"]

    total_assets = sum(Decimal(a.current_balance or 0) for a in asset_accounts)
    total_liabilities = sum(Decimal(a.current_balance or 0) for a in credit_card_accounts)

    return {
        "asset_accounts": asset_accounts,
        "credit_accounts": credit_card_accounts,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "net_worth": total_assets - total_liabilities
    }


def get_budget_widget_data(user, max_items=3):
    now = timezone.now()
    month_start = datetime(now.year, now.month, 1)

    transactions = Transaction.objects.filter(
        account__plaid_item__user=user,
        date__gte=month_start
    )

    data = []
    for budget in Budget.objects.filter(user=user):
        tags = budget.tags.all()
        tag_ids = {t.id for t in tags}
        total_spent = sum(t.amount for t in transactions if t.tag and t.tag.id in tag_ids)
        percent = float(total_spent) / float(budget.amount) if budget.amount else 0

        if percent >= 1.0:
            color = "#ef4444"  # red
        elif percent >= 0.75:
            color = "#facc15"  # yellow
        else:
            color = "#4ade80"  # green

        data.append({
            "name": budget.name,
            "spent": total_spent,
            "limit": budget.amount,
            "percent": percent * 100,
            "color": color,
            "tags": [t.name for t in tags],  # 👈 add this
        })

    return sorted(data, key=lambda b: b["percent"], reverse=True)[:max_items]

def get_account_balance_deltas(user):
    today = now().date()
    last_month = today.replace(day=1).replace(month=today.month - 1 or 12)

    deltas = []
    for acct in Account.objects.filter(plaid_item__user=user):
        try:
            prev = AccountBalanceSnapshot.objects.get(user=user, account=acct, date=last_month)
            delta = acct.balance - prev.balance
            pct_change = (delta / prev.balance * 100) if prev.balance != 0 else None
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

def get_top_categories_data(user, limit=3):
    """Summarizes total spending per tag for the current month."""
    now = timezone.now()
    month_start = datetime(now.year, now.month, 1)

    # Filter current month and only include tagged transactions
    transactions = Transaction.objects.filter(
        account__plaid_item__user=user,
        date__gte=month_start,
        tag__isnull=False
    )

    # Aggregate totals by tag
    category_totals = defaultdict(float)
    for txn in transactions:
        category_totals[txn.tag.name] += float(txn.amount)

    # Sort highest spending first and return top N
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:limit]

    return [{"name": name, "amount": total} for name, total in sorted_categories]