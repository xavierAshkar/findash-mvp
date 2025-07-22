from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def sum_balances(account_list):
    return sum(Decimal(a.current_balance) for a in account_list)

@register.filter
def abs_val(value):
    return abs(value)

@register.filter
def pad_accounts(selected_accounts, max_slots=3):
    """
    Returns a list of length `max_slots` where real accounts are followed by None placeholders.
    """
    padded = list(selected_accounts)
    while len(padded) < max_slots:
        padded.append(None)
    return padded