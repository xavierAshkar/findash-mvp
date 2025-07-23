# core/utils/widget.py

from ..models import DashboardWidget
from core.constants import (
    WIDGET_TRANSACTIONS,
    WIDGET_NET_WORTH,
    WIDGET_BALANCES,
    WIDGET_BUDGETS,
    WIDGET_BALANCE_CHANGE,
)

DEFAULT_WIDGETS = [
    (WIDGET_TRANSACTIONS, 0),
    (WIDGET_NET_WORTH, 1),
    (WIDGET_BALANCES, 2),
    (WIDGET_BUDGETS, 3),
]

def create_default_widgets(user):
    for widget_type, position in DEFAULT_WIDGETS:
        DashboardWidget.objects.get_or_create(
            user=user,
            widget_type=widget_type,
            defaults={"position": position, "enabled": True}
        )
