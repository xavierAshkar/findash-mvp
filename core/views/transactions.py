"""
core/views/transactions.py

Handles:
- Transactions view shown from left sidebar
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from plaid_link.models import Account, Transaction
from ..models import Tag
from collections import OrderedDict
from decimal import Decimal
from django.db.models import Q
from django.template.loader import render_to_string
from core.utils.tags import auto_tag_transaction

@login_required
def transactions_view(request):
    user = request.user
    params = request.GET

    transactions = Transaction.objects.filter(account__plaid_item__user=user)

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

    # Tag or category filter (comma-separated)
    tag_input = params.get("tag")
    tag = None
    if tag_input:
        tag_list = [t.strip() for t in tag_input.split(",") if t.strip()]
        if tag_list:
            tag_query = Q()
            for t in tag_list:
                tag_query |= Q(tag__name__icontains=t) | Q(category_main__icontains=t)
            transactions = transactions.filter(tag_query)
            tag = tag_input  # preserve raw input for UI

    # Sort and group
    transactions = transactions.order_by("-date", "-id")
    grouped_transactions = OrderedDict()
    for txn in transactions:
        grouped_transactions.setdefault(txn.date, []).append(txn)

    user_tags = Tag.objects.filter(user=request.user)

    # Shared context
    context = {
        "grouped_transactions": grouped_transactions,
        "user_accounts": user_accounts,
        "user_tags": user_tags,
        "selected_account_id": int(selected_id) if selected_id else None,
        "filters": {
            "tag": tag,
            "start_date": start_date,
            "end_date": end_date,
            "min_amount": min_amount,
            "max_amount": max_amount,
        }
    }

    # Return partial if HTMX request
    if request.headers.get("HX-Request"):
        return render(request, "core/transactions/partials/_transaction_list.html", context)

    # Otherwise return full page
    return render(request, "core/transactions/index.html", context)

@login_required
def add_transaction_view(request):
    user = request.user
    accounts = Account.objects.filter(plaid_item__user=request.user)
    user_tags = Tag.objects.filter(user=user)

    if request.method == "POST":
        name = request.POST.get("name")
        amount = request.POST.get("amount")
        date = request.POST.get("date")
        category = request.POST.get("category")
        tag_id = request.POST.get("tag")
        tag = Tag.objects.filter(id=tag_id, user=request.user).first()
        account_id = request.POST.get("account")

        if all([name, amount, date, account_id]):
            account = get_object_or_404(Account, id=account_id, plaid_item__user=request.user)
            txn = Transaction.objects.create(
                name=name,
                amount=Decimal(amount),
                date=date,
                category_main=category,
                tag=tag,
                account=account,
            )

            # Auto-tag if no manual tag was selected
            if txn.tag is None:
                auto_tag_transaction(user, txn)

            return redirect("core:transactions")


    return render(request, "core/transactions/add_transaction.html", {
        "accounts": accounts,
        "user_tags": user_tags,
    })

@require_POST
@login_required
def tag_transaction(request, transaction_id):
    txn = get_object_or_404(Transaction, id=transaction_id, account__plaid_item__user=request.user)
    tag_id = request.POST.get("tag", "").strip()

    if tag_id == "":
        print(f"🧹 Clearing tag for transaction: {txn.name}")
        txn.tag = None
        txn.save()
        return redirect(request.META.get("HTTP_REFERER", "core:transactions"))

    tag = Tag.objects.filter(id=tag_id, user=request.user).first()
    if tag:
        txn.tag = tag
        txn.save()
        print(f"✅ Tagged transaction: {txn.name} → {tag.name}")
    else:
        print(f"⚠️ Tag ID {tag_id} not found for user {request.user}")

    return redirect(request.META.get("HTTP_REFERER", "core:transactions"))