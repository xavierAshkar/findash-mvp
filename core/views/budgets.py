"""
core/views/budgets.py
"""
from datetime import datetime
import calendar
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from plaid_link.models import Transaction
from ..models import Budget, Tag
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string

@login_required
def budgets(request):
    user = request.user

    # Handle new budget creation
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

    # Time calculations
    now = timezone.now()
    month_start = datetime(now.year, now.month, 1)
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    today = now.day

    # Pull budgets + transactions
    budgets = Budget.objects.filter(user=user)
    transactions = Transaction.objects.filter(
        account__plaid_item__user=user,
        date__gte=month_start
    )

    budget_data = []
    for budget in budgets:
        matching_tags = budget.tags.all()
        tag_ids = {tag.id for tag in matching_tags}

        # Calculate spending
        total_spent = 0
        included_txns = []
        for t in transactions:
            if t.tag and t.tag.id in tag_ids:
                total_spent += abs(t.amount)  # use absolute value
                included_txns.append(t)

        # Percent spent overall
        percent = (float(total_spent) / float(budget.amount)) if budget.amount else 0

        # Expected pace by today
        expected_spent_by_today = float(budget.amount) * (today / days_in_month)

        # Color logic: pacing-based
        if total_spent >= float(budget.amount):
            color = "#ef4444"  # red (over budget)
        elif total_spent > expected_spent_by_today:
            color = "#facc15"  # yellow (spending too fast)
        else:
            color = "#4ade80"  # green (on track)

        budget_data.append({
            "name": budget.name,
            "amount": budget.amount,
            "spent": total_spent,
            "tags": matching_tags,
            "transactions": included_txns,
            "percent": percent * 100,
            "color": color,
        })

    # Tags for modal form
    user_tags = Tag.objects.filter(user=user)

    return render(request, 'core/budgets/index.html', {
        "budget_data": budget_data,
        "user_tags": user_tags,
        "budgets": budgets,
    })

@login_required
def budget_history(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request")

    user = request.user
    budget_id = request.POST.get("past-budget-select") or request.POST.get("budget_id")
    month_str = request.POST.get("past-budget-month") or request.POST.get("month")

    if not budget_id or not month_str:
        return HttpResponseBadRequest("Missing data")

    # Parse month/year from YYYY-MM format
    year, month = map(int, month_str.split("-"))
    month_start = datetime(year, month, 1)
    next_month = month_start + relativedelta(months=1)

    # Get budget and transactions
    budget = Budget.objects.get(id=budget_id, user=user)
    transactions = Transaction.objects.filter(
        account__plaid_item__user=user,
        date__gte=month_start,
        date__lt=next_month
    )

    # Calculate spending
    tag_ids = {tag.id for tag in budget.tags.all()}
    total_spent = sum(abs(t.amount) for t in transactions if t.tag and t.tag.id in tag_ids)
    percent = (float(total_spent) / float(budget.amount)) * 100 if budget.amount else 0

    # Determine color (reuse pacing logic or simple thresholds)
    color = "#ef4444" if total_spent >= float(budget.amount) else "#4ade80"

    context = {
        "budget": budget,
        "spent": total_spent,
        "percent": percent,
        "color": color,
        "transactions": [t for t in transactions if t.tag and t.tag.id in tag_ids],
    }

    # Render partial card
    html = render_to_string("core/budgets/partials/_past_budget_card.html", context, request=request)
    return HttpResponse(html)