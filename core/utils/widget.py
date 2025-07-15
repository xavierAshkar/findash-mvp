from ..models import DashboardWidget

DEFAULT_WIDGETS = [
    ("transactions", 0),
    ("notifications", 1),
    ("balances", 2),
    ("budgets", 3),
]

def create_default_widgets(user):
    for widget_type, position in DEFAULT_WIDGETS:
        DashboardWidget.objects.get_or_create(
            user=user,
            widget_type=widget_type,
            defaults={"position": position, "enabled": True}
        )
