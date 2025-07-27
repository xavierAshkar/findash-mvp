"""core/views/__init__.py"""

from .dashboard import dashboard, toggle_edit_mode, remove_widget, add_widget, update_balance_widget, save_widget_order
from .accounts import accounts_view
from .transactions import transactions_view, add_transaction_view, tag_transaction
from .budgets import budgets, budget_history
from .profile import profile_view, delete_account_view
from .auth import logout_view
