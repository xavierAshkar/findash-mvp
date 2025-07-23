from django import template
from core.constants import (
    WIDGET_TRANSACTIONS,
    WIDGET_NET_WORTH,
    WIDGET_BALANCES,
    WIDGET_BUDGETS,
    WIDGET_BALANCE_CHANGE,
)

register = template.Library()

WIDGET_TITLES = {
    WIDGET_TRANSACTIONS: "Recent Transactions",
    WIDGET_NET_WORTH: "Net Worth",
    WIDGET_BALANCES: "Account Balances",
    WIDGET_BUDGETS: "Budget Overview",
    WIDGET_BALANCE_CHANGE: "Account Balance Changes",
}

@register.filter
def widget_title(widget_type):
    return WIDGET_TITLES.get(widget_type, widget_type.replace("_", " ").title())
