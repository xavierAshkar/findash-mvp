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
def cash_accounts(request):
    accounts = Account.objects.filter(
        plaid_item__user=request.user, 
            type="depository",
            subtype__in=["checking", "savings"])
    return render(request, "core/cash_accounts.html", {"accounts": accounts})

@login_required
def credit_accounts(request):
    accounts = Account.objects.filter(
        plaid_item__user=request.user, 
        type="credit")
    return render(request, "core/credit_accounts.html", {"accounts": accounts})

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