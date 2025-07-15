from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def sum_balances(account_list):
    return sum(Decimal(a.current_balance) for a in account_list)

@register.filter
def abs_val(value):
    return abs(value)