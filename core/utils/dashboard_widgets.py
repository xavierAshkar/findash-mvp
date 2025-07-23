# core/utils/dashboard_widgets.py
from django.template.loader import render_to_string
from plaid_link.models import Transaction as PlaidTransaction, Account as PlaidAccount
from core.utils.dashboard_data import get_net_worth_data, get_budget_widget_data, get_account_balance_deltas
from core.models import DashboardBalancePreference
from core.constants import (
    WIDGET_TRANSACTIONS,
    WIDGET_NET_WORTH,
    WIDGET_BALANCES,
    WIDGET_BUDGETS,
    WIDGET_BALANCE_CHANGE,
)


def get_widget_map(user, request):
    recent_txns = PlaidTransaction.objects.filter(
        account__plaid_item__user=user
    ).order_by("-date")[:5]

    if pref := DashboardBalancePreference.objects.filter(user=user).first():
        selected_accounts = list(pref.accounts.select_related("plaid_item").all())[:3]
    else:
        selected_accounts = []

    return {
        WIDGET_TRANSACTIONS: {
            "title": "Recent Transactions",
            "content": render_to_string(
                "core/dashboard/widgets/transactions_widget.html", 
                {"transactions": recent_txns}, request=request
            )
        },
        WIDGET_NET_WORTH: {
            "title": "Net Worth",
            "content": render_to_string(
                "core/dashboard/widgets/net_worth_widget.html",
                {"net_worth_data": get_net_worth_data(user)}, request=request
            )
        },
        WIDGET_BALANCES: {
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
        WIDGET_BUDGETS: {
            "title": "Budget Overview",
            "content": render_to_string(
                "core/dashboard/widgets/budgets_widget.html",
                {"data": get_budget_widget_data(user)}, request=request
            )
        },
        WIDGET_BALANCE_CHANGE: {
            "title": "Account Balance Changes",
            "content": render_to_string(
                "core/dashboard/widgets/balance_change_widget.html",
                {"deltas": get_account_balance_deltas(user)},
                request=request
            )
        },
    }
