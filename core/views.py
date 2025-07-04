"""
core/views.py

Handles views for the main app experience after login:
- Dashboard (summary of linked accounts, transactions, etc.)
"""

# Standard Library
from collections import OrderedDict
from datetime import datetime

# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Q

# Third-Party (Plaid models)
from plaid_link.models import PlaidItem, Account, Transaction

# Local App
from .models import Budget

# Other
from decimal import Decimal
from itertools import groupby
from operator import attrgetter

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


@login_required
def transactions_view(request):
    print("💡 Total transactions before filters:", Transaction.objects.filter(account__plaid_item__user=request.user).count())
    user = request.user
    params = request.GET

    # All user accounts
    user_accounts = Account.objects.filter(plaid_item__user=user)

    # Base queryset
    transactions = Transaction.objects.filter(account__plaid_item__user=user)

    # Account filter
    selected_id = params.get("account_id")
    if selected_id:
        transactions = transactions.filter(account__id=selected_id)

    # Date range filter
    start_date = params.get("start_date")
    end_date = params.get("end_date")
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    # Amount filter
    min_amount = params.get("min_amount")
    max_amount = params.get("max_amount")
    if min_amount:
        transactions = transactions.filter(amount__gte=Decimal(min_amount))
    if max_amount:
        transactions = transactions.filter(amount__lte=Decimal(max_amount))

    # Tag or category filter
    tag = params.get("tag")
    if tag:
        transactions = transactions.filter(
            Q(user_tag__icontains=tag) | Q(category_main__icontains=tag)
        )

    # Sort and group
    transactions = transactions.order_by("-date", "-id")
    print("🧾 First 5 transactions:", list(transactions[:5]))
    grouped_transactions = OrderedDict()

    for txn in transactions:
        grouped_transactions.setdefault(txn.date, []).append(txn)

    return render(request, "core/transactions.html", {
        "grouped_transactions": grouped_transactions,
        "user_accounts": user_accounts,
        "selected_account_id": int(selected_id) if selected_id else None,
        "filters": {
            "tag": tag,
            "start_date": start_date,
            "end_date": end_date,
            "min_amount": min_amount,
            "max_amount": max_amount,
        }
    })

@login_required
def add_transaction_view(request):
    accounts = Account.objects.filter(plaid_item__user=request.user)

    if request.method == "POST":
        name = request.POST.get("name")
        amount = request.POST.get("amount")
        date = request.POST.get("date")
        category = request.POST.get("category")
        tag = request.POST.get("tag")
        account_id = request.POST.get("account")

        if all([name, amount, date, account_id]):
            account = get_object_or_404(Account, id=account_id, plaid_item__user=request.user)
            Transaction.objects.create(
                name=name,
                amount=Decimal(amount),
                date=date,
                category_main=category,
                user_tag=tag,
                account=account,
            )
            return redirect("core:transactions")

    return render(request, "core/add_transaction.html", {
        "accounts": accounts
    })

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