"""
core/views/budgets.py

Handles:
- Budgets view shown from left sidebar
"""

from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from plaid_link.models import Transaction
from ..models import Budget, Tag

@login_required
def budgets(request):
    user = request.user

    if request.method == "POST":
        name = request.POST.get("name")
        tag_ids = request.POST.getlist("tags")
        amount = request.POST.get("amount")

        budget = Budget.objects.create(
            user=user,
            name=name,
            amount=amount,
        )
        budget.tags.set(tag_ids)
        return redirect('core:budgets')

    budgets = Budget.objects.filter(user=user)
    now = timezone.now()
    month_start = datetime(now.year, now.month, 1)

    transactions = Transaction.objects.filter(
        account__plaid_item__user=user,
        date__gte=month_start
    )

    budget_data = []
    for budget in budgets:
        matching_tags = budget.tags.all()
        tag_ids = {tag.id for tag in matching_tags}

        total_spent = 0
        included_txns = []

        for t in transactions:
            if t.tag and t.tag.id in tag_ids:
                total_spent += t.amount
                included_txns.append(t)


        percent = float(total_spent) / float(budget.amount) if budget.amount else 0

        if percent >= 1.0:
            color = "#ef4444"  # red
        elif percent >= 0.75:
            color = "#facc15"  # yellow
        else:
            color = "#4ade80"  # green

        budget_data.append({
            "name": budget.name,
            "amount": budget.amount,
            "spent": total_spent,
            "tags": matching_tags,
            "transactions": included_txns,
            "percent": percent * 100,
            "color": color,
        })

    user_tags = Tag.objects.filter(user=user)

    return render(request, 'core/budgets.html', {
        "budget_data": budget_data,
        "user_tags": user_tags,
    })