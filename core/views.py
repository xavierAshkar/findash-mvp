"""
core/views.py

Handles views for the main app experience after login:
- Dashboard (summary of linked accounts, transactions, etc.)
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from plaid_link.models import PlaidItem, Account, Transaction

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
    transactions = Transaction.objects.filter(account__plaid_item__user=request.user).order_by("-date")[:50]
    return render(request, "core/transactions.html", {"transactions": transactions})

@login_required
def budgets(request):
    return render(request, 'core/budgets.html')