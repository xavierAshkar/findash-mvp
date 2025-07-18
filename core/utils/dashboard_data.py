from datetime import datetime
from django.utils import timezone
from decimal import Decimal
from plaid_link.models import Account, Transaction
from core.models import Budget

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
        "net_worth": total_assets + total_liabilities
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
        tag_ids = set(t.id for t in budget.tags.all())
        total_spent = sum(t.amount for t in transactions if t.tag and t.tag.id in tag_ids)
        percent = float(total_spent) / float(budget.amount) if budget.amount else 0

        data.append({
            "name": budget.name,
            "spent": total_spent,
            "limit": budget.amount,
            "percent": percent * 100,
        })

    # Sort by % used descending and limit to `max_items`
    return sorted(data, key=lambda b: b["percent"], reverse=True)[:max_items]