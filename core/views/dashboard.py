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
from plaid_link.models import Account as PlaidAccount

from core.models import DashboardBalancePreference
from core.utils.dashboard_data import get_net_worth_data, get_budget_widget_data


@login_required
def dashboard(request):
    user = request.user

    if "dashboard_edit_mode" not in request.session:
        request.session["dashboard_edit_mode"] = False
    
    widgets = DashboardWidget.objects.filter(user=user, enabled=True).order_by("position")

    recent_txns = PlaidTransaction.objects.filter(
        account__plaid_item__user=user
    ).order_by("-date")[:5]

    if pref := DashboardBalancePreference.objects.filter(user=user).first():
        all_selected = pref.accounts.select_related("plaid_item").all()
        selected_accounts = all_selected[:3]
        selected_ids = [a.id for a in selected_accounts]
    else:
        selected_accounts = []
        selected_ids = []



    WIDGET_MAP = {
        "transactions": {
            "title": "Recent Transactions",
            "content": render_to_string(
                "core/dashboard/widgets/transactions_widget.html", 
                {
                    "transactions": recent_txns
                }, 
                request=request
            )
        },
        "net_worth": {
            "title": "Net Worth",
            "content": render_to_string(
                "core/dashboard/widgets/net_worth_widget.html",
                {
                    "net_worth_data": get_net_worth_data(user)
                },
                request=request
            )
        },
        "balances": {
            "title": "Account Balances",
            "content": render_to_string(
                "core/dashboard/widgets/balances_widget.html",
                {
                    "selected_accounts": selected_accounts,
                    "all_accounts": PlaidAccount.objects.filter(plaid_item__user=user),
                    "selected_ids": [a.id for a in selected_accounts],
                    "edit_mode": request.session.get("dashboard_edit_mode", False),
                },
                request=request
            )
        },
        "budgets": {
            "title": "Budget Overview",
            "content": render_to_string(
                "core/dashboard/widgets/budgets_widget.html",
                {
                    "data": get_budget_widget_data(user)
                },
                request=request
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

    return render(request, "core/dashboard/index.html", {
        "rendered_widgets": rendered_widgets,
        "edit_mode": edit_mode,
        "available_widgets": available_widgets,
    })

@require_POST
@login_required
def toggle_edit_mode(request):
    edit_mode = request.session.get("dashboard_edit_mode", False)
    request.session["dashboard_edit_mode"] = not edit_mode

    if request.headers.get("Hx-Request") == "true":
        return render(request, "core/dashboard/partials/_header.html", {
            "edit_mode": request.session["dashboard_edit_mode"],
        })

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

            selected_accounts_qs = PlaidAccount.objects.filter(
                dashboard_balance_preferences__user=user
            ).select_related("plaid_item")

            selected_accounts = list(selected_accounts_qs[:3])
            selected_ids = [a.id for a in selected_accounts]


            WIDGET_MAP = {
                "transactions": {
                    "title": "Recent Transactions",
                    "content": render_to_string(
                        "core/dashboard/widgets/transactions_widget.html", 
                        {
                            "transactions": recent_txns
                        }, 
                        request=request
                    )
                },
                "net_worth": {
                    "title": "Net Worth",
                    "content": render_to_string(
                        "core/dashboard/widgets/net_worth_widget.html",
                        {
                            "net_worth_data": get_net_worth_data(user)
                        },
                        request=request
                    )
                },
                "balances": {
                    "title": "Account Balances",
                    "content": render_to_string(
                        "core/dashboard/widgets/balances_widget.html",
                        {
                            "selected_accounts": selected_accounts,
                            "all_accounts": PlaidAccount.objects.filter(plaid_item__user=user),
                            "selected_ids": [a.id for a in selected_accounts],
                            "edit_mode": request.session.get("dashboard_edit_mode", False),
                        },
                        request=request
                    )
                },
                "budgets": {
                    "title": "Budget Overview",
                    "content": render_to_string(
                        "core/dashboard/widgets/budgets_widget.html",
                        {
                            "data": get_budget_widget_data(user)
                        },
                        request=request
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

@require_POST
@login_required
def update_balance_widget(request):
    account_ids = request.POST.getlist("account_ids")[:3]  # limit to 3
    accounts = PlaidAccount.objects.filter(id__in=account_ids, plaid_item__user=request.user)

    setting, _ = DashboardBalancePreference.objects.get_or_create(user=request.user)
    setting.accounts.set(accounts)

    # Re-render widget
    rendered = render_to_string("core/components/dashboard_widget.html", {
        "title": "Account Balances",
        "widget_type": "balances",
        "content": render_to_string("core/dashboard/widgets/balances_widget.html", {
            "selected_accounts": accounts,
            "all_accounts": PlaidAccount.objects.filter(plaid_item__user=request.user),
            "selected_ids": [a.id for a in accounts],
            "edit_mode": request.session.get("dashboard_edit_mode", False)
        }, request=request),
        "edit_mode": request.session.get("dashboard_edit_mode", False),
    }, request=request)

    return HttpResponse(rendered)
