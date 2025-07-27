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
    accounts = Account.objects.filter(plaid_item__user=request.user)

    # Common subtypes
    common_subtypes = ["checking", "savings"]

    # Assets
    checking_accounts = [a for a in accounts if a.type == "depository" and a.subtype == "checking"]
    savings_accounts = [a for a in accounts if a.type == "depository" and a.subtype == "savings"]

    # Investments (Roth IRA, 401k, brokerage)
    investment_accounts = [a for a in accounts if a.type == "investment"]

    # Other assets: Depository but not checking/savings
    other_assets = [
        a for a in accounts
        if a.type == "depository" and a.subtype not in common_subtypes
    ]

    # Liabilities (credit cards, loans)
    credit_accounts = [a for a in accounts if a.type == "credit"]

    # Totals
    total_checking = sum(Decimal(a.current_balance) for a in checking_accounts)
    total_savings = sum(Decimal(a.current_balance) for a in savings_accounts)
    total_investments = sum(Decimal(a.current_balance) for a in investment_accounts)
    total_other = sum(Decimal(a.current_balance) for a in other_assets)

    total_assets = total_checking + total_savings + total_investments + total_other
    total_credit = sum(Decimal(a.current_balance) for a in credit_accounts)
    total_liabilities = total_credit
    net_worth = total_assets + total_liabilities

    return render(request, "core/accounts/index.html", {
        "checking_accounts": checking_accounts,
        "savings_accounts": savings_accounts,
        "investment_accounts": investment_accounts,
        "other_assets": other_assets,
        "credit_accounts": credit_accounts,
        "total_checking": total_checking,
        "total_savings": total_savings,
        "total_investments": total_investments,
        "total_other": total_other,
        "total_assets": total_assets,
        "total_credit": total_credit,
        "total_liabilities": total_liabilities,
        "net_worth": net_worth,
        "accounts": accounts,  # if needed elsewhere
    })
