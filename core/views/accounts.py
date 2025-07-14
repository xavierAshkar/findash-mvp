"""
core/views/accounts.py

Handles:
- Accounts view shown from left sidebar
"""

from django.contrib.auth.decorators import login_required
from decimal import Decimal
from plaid_link.models import Account
from django.shortcuts import render

@login_required
def accounts_view(request):
    """
    Display the user's linked accounts and their balances.
    - Fetch all accounts linked via Plaid for this user
    - Separate accounts into asset and liability categories
    - Calculate totals for each category
    """

    # Fetch all accounts linked via Plaid for this user
    accounts = Account.objects.filter(plaid_item__user=request.user)

    # Separate out depository (asset) accounts
    asset_accounts = [a for a in accounts if a.type == "depository"]

    # Common subtypes shown separately
    common_subtypes = ["checking", "savings"]

    # Group common assets
    common_assets = {
        subtype: [a for a in asset_accounts if a.subtype == subtype]
        for subtype in common_subtypes
    }

    # Remaining assets go in "Other Assets"
    other_assets = [a for a in asset_accounts if a.subtype not in common_subtypes]

    # Totals
    total_checking = sum(Decimal(a.current_balance) for a in common_assets.get("checking", []))
    total_savings = sum(Decimal(a.current_balance) for a in common_assets.get("savings", []))
    total_other = sum(Decimal(a.current_balance) for a in other_assets)
    total_assets = total_checking + total_savings + total_other

    # Liabilities
    credit_card_accounts = [a for a in accounts if a.type == "credit"]
    total_credit = sum(Decimal(a.current_balance) for a in credit_card_accounts)
    total_liabilities = total_credit
    net_worth = total_assets + total_liabilities

    return render(request, "core/accounts.html", {
        "accounts": accounts,
        "common_assets": common_assets,
        "other_assets": other_assets,
        "credit_accounts": credit_card_accounts,
        "total_checking": total_checking,
        "total_savings": total_savings,
        "total_other": total_other,
        "total_assets": total_assets,
        "total_credit": total_credit,
        "total_liabilities": total_liabilities,
        "net_worth": net_worth,
    })