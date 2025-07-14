"""
plaid_link/views/accounts.py

Handles:
- Fetching and saving Plaid account data
"""

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid_link.models import PlaidItem, Account
from plaid_link.utils import get_plaid_client
import traceback

@require_POST
@login_required
def fetch_accounts(request):
    """
    Fetches and saves Plaid account data for the authenticated user.
    - Retrieves all linked Plaid items for the user
    - For each item, fetches account details from Plaid
    - Saves or updates account information in the database
    """
    try:
        # Get all Plaid items linked to the user
        plaid_items = PlaidItem.objects.filter(user=request.user)

        # If no Plaid items are linked, return an error
        if not plaid_items.exists():
            return JsonResponse({"error": "No linked Plaid items"}, status=404)

        # Setup Plaid client
        client = get_plaid_client()

        # Init list to hold all accounts fetched
        all_accounts = []

        # Loop through each Plaid item and fetch accounts
        for plaid_item in plaid_items:
            access_token = plaid_item.get_access_token()
            response = client.accounts_get(AccountsGetRequest(access_token=access_token))
            accounts = response.to_dict()["accounts"]
            all_accounts.extend(accounts)

            # Save or update each account in the database
            for acct in accounts:
                Account.objects.update_or_create(
                    plaid_item=plaid_item,
                    account_id=acct["account_id"],
                    defaults={
                        "name": acct["name"],
                        "official_name": acct.get("official_name"),
                        "type": acct["type"],
                        "subtype": acct["subtype"],
                        "available_balance": acct["balances"].get("available"),
                        "current_balance": acct["balances"].get("current"),
                    }
                )

        # Return success response with count of accounts fetched
        response = JsonResponse({"status": "success", "count": len(all_accounts)})
        # Trigger a frontend update to refresh account data
        response["HX-Trigger"] = "refreshComplete"
        return response

    except Exception as e:
        # Log the error and return an error response
        print("🔴 ERROR in fetch_accounts")
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
