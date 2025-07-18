from decimal import Decimal
from plaid_link.models import Account

def get_net_worth_data(user):
    accounts = Account.objects.filter(plaid_item__user=user)

    asset_accounts = [a for a in accounts if a.type == "depository"]
    credit_card_accounts = [a for a in accounts if a.type == "credit"]

    total_assets = sum(Decimal(a.current_balance or 0) for a in asset_accounts)
    total_liabilities = sum(Decimal(a.current_balance or 0) for a in credit_card_accounts)

    return {
        "asset_accounts": asset_accounts,
        "credit_accounts": credit_card_accounts,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "net_worth": total_assets + total_liabilities
    }
