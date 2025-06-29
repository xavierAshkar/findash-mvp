"""
core/views.py

Handles views for the main app experience after login:
- Dashboard (summary of linked accounts, transactions, etc.)
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from plaid_link.models import PlaidItem, Account, Transaction
from .models import Budget
from django.utils import timezone
from datetime import datetime
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from decimal import Decimal

@login_required
def dashboard(request):
    """
    Display the user's main dashboard view.

    - If no Plaid accounts are linked, redirect to the Plaid link page
    - Otherwise, fetch accounts and render them in the dashboard template
    """

    # Check if user has any Plaid items linked
    has_plaid_item = PlaidItem.objects.filter(user=request.user).exists()
    if not has_plaid_item:
        # Redirect user to the account link flow if nothing is connected
        return redirect('plaid:link_account')

    # Fetch all accounts linked via Plaid for this user
    accounts = Account.objects.filter(plaid_item__user=request.user)

    # Filter account types into general categories for display
    account_types = ["depository", "credit"]


    # Render the dashboard page with the user’s accounts
    return render(request, 'core/dashboard.html', {
        'accounts': accounts,
        'account_types': account_types,
    })

@login_required
def accounts_view(request):
    accounts = Account.objects.filter(plaid_item__user=request.user)

    # Filters
    checking_accounts = [a for a in accounts if a.subtype == "checking"]
    savings_accounts = [a for a in accounts if a.subtype == "savings"]
    credit_card_accounts = [a for a in accounts if a.type == "credit"]

    # Totals
    total_checking = sum(Decimal(a.current_balance) for a in checking_accounts)
    total_savings = sum(Decimal(a.current_balance) for a in savings_accounts)
    total_credit = sum(Decimal(a.current_balance) for a in credit_card_accounts)

    # Asset/Liability classification
    asset_accounts = [
        a for a in accounts if a.type == "depository" and Decimal(a.current_balance) >= 0
    ]
    liability_accounts = [
        a for a in accounts if a.type in ["credit", "loan"] or Decimal(a.current_balance) < 0
    ]

    total_assets = sum(Decimal(a.current_balance) for a in asset_accounts)
    total_liabilities = sum(Decimal(a.current_balance) for a in liability_accounts)
    net_worth = total_assets + total_liabilities

    return render(request, "core/accounts.html", {
        "accounts": accounts,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "net_worth": net_worth,
        "total_checking": total_checking,
        "total_savings": total_savings,
        "total_credit": total_credit,
    })


@login_required
def transactions(request):
    transactions = Transaction.objects.filter(
        account__plaid_item__user=request.user).order_by("-date")[:50]
    return render(request, "core/transactions.html", {"transactions": transactions})

@require_POST
@login_required
def tag_transaction(request, transaction_id):
    txn = get_object_or_404(Transaction, id=transaction_id, account__plaid_item__user=request.user)
    tag = request.POST.get("tag", "").strip()
    if tag:
        txn.user_tag = tag
        txn.save()
    return redirect("core:transactions")

@login_required
def budgets(request):
    if request.method == "POST":
        name = request.POST.get("name")
        categories = request.POST.getlist("categories")  # multiple categories
        amount = request.POST.get("amount")

        Budget.objects.create(
            user=request.user,
            name=name,
            categories=categories,
            amount=amount
        )
        return redirect('core:budgets')

    budgets = Budget.objects.filter(user=request.user)
    now = timezone.now()
    month_start = datetime(now.year, now.month, 1)

    # Gather transactions from this month
    transactions = Transaction.objects.filter(
        account__plaid_item__user=request.user,
        date__gte=month_start
    )

    # Match against budgets
    budget_data = []
    for budget in budgets:
        total_spent = sum(
            t.amount
            for t in transactions
            if (
                (t.user_tag and any(cat.lower() in t.user_tag.lower() for cat in budget.categories)) or
                (not t.user_tag and t.category_main and any(cat.lower() in t.category_main.lower() for cat in budget.categories))
            )
        )
        budget_data.append({
            "name": budget.name,
            "amount": budget.amount,
            "spent": total_spent,
            "categories": budget.categories,
        })

    return render(request, 'core/budgets.html', {
        "budget_data": budget_data
    })