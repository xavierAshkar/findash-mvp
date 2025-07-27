"""
plaid_link/views/transactions.py

Handles:
- Fetching and storing Plaid transactions
"""

from datetime import date, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid_link.models import PlaidItem, Account, Transaction
from plaid_link.utils import get_plaid_client
import traceback
from core.utils.tags import auto_tag_transaction

@require_POST
@login_required
def fetch_transactions(request):
    """
    Fetches and saves Plaid transaction data for the authenticated user.
    - Retrieves all linked Plaid items for the user
    - For each item, fetches transaction details from Plaid
    - Saves or updates transaction information in the database
    """
    try:
        # Get all Plaid items linked to the user
        plaid_items = PlaidItem.objects.filter(user=request.user)

        # If no Plaid items are linked, return an error
        if not plaid_items.exists():
            return JsonResponse({"error": "No linked Plaid items"}, status=404)

        # Setup Plaid client
        client = get_plaid_client()

        # Define date range for transactions (last 30 days)
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        # Init count of created transactions
        created_count = 0

        # Loop through each Plaid item and fetch transactions within the date range
        for plaid_item in plaid_items:
            access_token = plaid_item.get_access_token()
            response = client.transactions_get(TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date
            ))

            # Extract transactions from the response
            transactions = response.to_dict()["transactions"]

            # Map account IDs to Account objects for easy lookup
            account_map = {
                acct.account_id: acct
                for acct in Account.objects.filter(plaid_item=plaid_item)
            }

            # Loop through each transaction and save or update in the database
            for txn in transactions:
                txn_obj, created = Transaction.objects.update_or_create(
                    transaction_id=txn["transaction_id"],
                    defaults={
                        "account": account_map.get(txn["account_id"]),
                        "name": txn["name"],
                        "amount": txn["amount"],
                        "date": txn["date"],
                        "category_main": txn["category"][0] if txn.get("category") else None,
                        "category_detailed": txn["category"][1] if txn.get("category") and len(txn["category"]) > 1 else None,
                        "merchant_name": txn.get("merchant_name"),
                        "payment_channel": txn.get("payment_channel"),
                    }
                )

                # Auto-tag if no manual tag was set
                if txn_obj.tag is None:
                    auto_tag_transaction(request.user, txn_obj)

                created_count += 1


        # Return success response with count of transactions fetched
        return JsonResponse({"status": "success", "count": created_count})

    except Exception as e:
        # Log the error and return an error response
        print("🔴 ERROR in fetch_transactions")
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
