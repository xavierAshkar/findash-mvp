"""
core/views/accounts.py

Handles:
- Accounts view shown from left sidebar
"""

from core.utils.snapshots import create_monthly_snapshots, get_account_balance_deltas, pct_change
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from plaid_link.models import Account
from django.shortcuts import render

@login_required
def accounts_view(request):
    # Get all user accounts
    accounts = Account.objects.filter(plaid_item__user=request.user)

    # Ensure snapshots exist for this month
    create_monthly_snapshots(request.user)

    # Get deltas (compares to last month or fallback to this month)
    deltas = get_account_balance_deltas(request.user)

    # --- Account groupings ---
    common_subtypes = ["checking", "savings"]

    checking_accounts = [a for a in accounts if a.type == "depository" and a.subtype == "checking"]
    savings_accounts = [a for a in accounts if a.type == "depository" and a.subtype == "savings"]
    investment_accounts = [a for a in accounts if a.type == "investment"]
    other_assets = [a for a in accounts if a.type == "depository" and a.subtype not in common_subtypes]
    credit_accounts = [a for a in accounts if a.type == "credit"]
    loan_accounts = [a for a in accounts if a.type == "loan" or a.subtype == "loan"]

    # --- Totals ---
    total_checking = sum(Decimal(a.current_balance) for a in checking_accounts)
    total_savings = sum(Decimal(a.current_balance) for a in savings_accounts)
    total_investments = sum(Decimal(a.current_balance) for a in investment_accounts)
    total_other = sum(Decimal(a.current_balance) for a in other_assets)

    total_assets = total_checking + total_savings + total_investments + total_other
    total_credit = sum(Decimal(a.current_balance) for a in credit_accounts)
    total_loans = sum(Decimal(a.current_balance) for a in loan_accounts)
    total_liabilities = total_credit + total_loans
    net_worth = total_assets - total_liabilities

    # --- Percentage change calculations (assets/liabilities) ---
    # Separate deltas
    asset_deltas = [d for d in deltas if d["account"].type in ["depository", "investment"]]
    liability_deltas = [d for d in deltas if d["account"].type in ["credit", "loan"]]

    # Compute previous totals (snapshot balances) = current - delta
    prev_assets = sum((d["current"] - (d["delta"] or 0)) for d in asset_deltas)
    prev_liabilities = sum((d["current"] - (d["delta"] or 0)) for d in liability_deltas)

    total_asset_delta = sum(d["delta"] or 0 for d in asset_deltas)
    total_liability_delta = sum(d["delta"] or 0 for d in liability_deltas)

    # Percent changes
    assets_pct = (total_asset_delta / prev_assets * 100) if prev_assets else None
    liabilities_pct = (total_liability_delta / prev_liabilities * 100) if prev_liabilities else None
    checking_pct = pct_change(deltas, types=["depository"], subtypes=["checking"])
    savings_pct = pct_change(deltas, types=["depository"], subtypes=["savings"])
    investment_pct = pct_change(deltas, types=["investment"])
    credit_pct = pct_change(deltas, types=["credit"])
    loan_pct = pct_change(deltas, types=["loan"])


    return render(request, "core/accounts/index.html", {
        "checking_accounts": checking_accounts,
        "savings_accounts": savings_accounts,
        "investment_accounts": investment_accounts,
        "other_assets": other_assets,
        "credit_accounts": credit_accounts,
        "loan_accounts": loan_accounts,
        "total_checking": total_checking,
        "total_savings": total_savings,
        "total_investments": total_investments,
        "total_other": total_other,
        "total_assets": total_assets,
        "total_credit": total_credit,
        "total_loans": total_loans,
        "total_liabilities": total_liabilities,
        "net_worth": net_worth,
        "accounts": accounts,
        "deltas": deltas,
        "assets_pct": assets_pct,
        "liabilities_pct": liabilities_pct,
        "checking_pct": checking_pct,
        "savings_pct": savings_pct,
        "investment_pct": investment_pct,
        "credit_pct": credit_pct,
        "loan_pct": loan_pct,
    })