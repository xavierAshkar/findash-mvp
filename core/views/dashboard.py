"""
core/views/dashboard.py

Handles:
- Main dashboard view shown after login
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import DashboardWidget

@login_required
def dashboard(request):
    user = request.user

    widgets = DashboardWidget.objects.filter(user=user, enabled=True).order_by("position")

    WIDGET_MAP = {
        "transactions": {
            "title": "Recent Transactions",
            "content": "<ul class='text-sm text-white space-y-[4px]'><li>Starbucks - $5.25</li><li>Amazon - $43.12</li><li>Rent - $1200.00</li></ul>"
        },
        "notifications": {
            "title": "Notifications",
            "content": "<p class='text-sm text-white'>You have 2 unread alerts</p>"
        },
        "balances": {
            "title": "Account Balances",
            "content": "<p class='text-sm text-textSubtle'>Total Balance: $8,542.32</p>"
        },
        "budgets": {
            "title": "Budget Overview",
            "content": (
                "<p class='text-sm text-textSubtle'>Groceries: 68% used</p>"
                "<p class='text-sm text-textSubtle'>Dining: 92% used</p>"
            )
        },
    }

    rendered_widgets = [
        {
            "title": WIDGET_MAP[w.widget_type]["title"],
            "content": WIDGET_MAP[w.widget_type]["content"]
        }
        for w in widgets
        if w.widget_type in WIDGET_MAP
    ]

    return render(request, "core/dashboard.html", {
        "rendered_widgets": rendered_widgets,
    })
