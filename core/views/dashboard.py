"""
core/views/dashboard.py

Handles:
- Main dashboard view shown after login
- Widget rendering and edit mode toggling
- Widget removal functionality
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import DashboardWidget

# For the toggle edit mode and delete widget functionality
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect

# For dynamic reloading withour full page reload of widgets
from django.template.loader import render_to_string
from django.http import HttpResponse

from plaid_link.models import Transaction as PlaidTransaction

@login_required
def dashboard(request):
    user = request.user

    widgets = DashboardWidget.objects.filter(user=user, enabled=True).order_by("position")

    recent_txns = PlaidTransaction.objects.filter(
        account__plaid_item__user=user
    ).order_by("-date")[:5]

    WIDGET_MAP = {
        "transactions": {
            "title": "Recent Transactions",
            "content": render_to_string("core/components/widgets/transactions_widget.html", {
                "transactions": recent_txns
            }, request=request)
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
            "type": w.widget_type,
            "title": WIDGET_MAP[w.widget_type]["title"],
            "content": WIDGET_MAP[w.widget_type]["content"]
        }
        for w in widgets
        if w.widget_type in WIDGET_MAP
    ]

    available_widgets = [
        key for key in WIDGET_MAP
        if not DashboardWidget.objects.filter(user=user, widget_type=key, enabled=True).exists()
    ]

    edit_mode = request.session.get("dashboard_edit_mode", False)

    if request.GET.get("partial") == "chooser":
        available_widgets = [
            key for key in WIDGET_MAP
            if not DashboardWidget.objects.filter(user=user, widget_type=key, enabled=True).exists()
        ]

        return render(request, "core/components/widget_chooser.html", {
            "available_widgets": available_widgets,
            "edit_mode": edit_mode,
        })

    return render(request, "core/dashboard.html", {
        "rendered_widgets": rendered_widgets,
        "edit_mode": edit_mode,
        "available_widgets": available_widgets,
    })

@require_POST
@login_required
def toggle_edit_mode(request):
    edit_mode = request.session.get("dashboard_edit_mode", False)
    request.session["dashboard_edit_mode"] = not edit_mode
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/dashboard/"))


@require_POST
@login_required
def remove_widget(request):
    widget_type = request.POST.get("widget_type")
    DashboardWidget.objects.filter(user=request.user, widget_type=widget_type).update(enabled=False)

    if request.headers.get("Hx-Request") == "true":
        return HttpResponse("")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/dashboard/"))

@require_POST
@login_required
def add_widget(request):
    widget_type = request.POST.get("widget_type")
    user = request.user

    if widget_type:
        DashboardWidget.objects.update_or_create(
            user=user,
            widget_type=widget_type,
            defaults={"enabled": True}
        )

        if request.headers.get("Hx-Request") == "true":
            recent_txns = PlaidTransaction.objects.filter(
                account__plaid_item__user=user
            ).order_by("-date")[:5]

            WIDGET_MAP = {
                "transactions": {
                    "title": "Recent Transactions",
                    "content": render_to_string("core/components/widgets/transactions_widget.html", {
                        "transactions": recent_txns
                    }, request=request)
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

            data = {
                "widget_type": widget_type,
                "title": WIDGET_MAP[widget_type]["title"],
                "content": WIDGET_MAP[widget_type]["content"],
                "edit_mode": request.session.get("dashboard_edit_mode", False),
            }

            html = render_to_string("core/components/dashboard_widget.html", data, request=request)
            return HttpResponse(html)

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/dashboard/"))