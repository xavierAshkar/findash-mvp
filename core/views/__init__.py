"""core/views/__init__.py"""

from .dashboard import dashboard, toggle_edit_mode, remove_widget, add_widget
from .accounts import accounts_view
from .transactions import transactions_view, add_transaction_view, tag_transaction
from .budgets import budgets
from .profile import profile_view, delete_account_view
from .auth import logout_view
