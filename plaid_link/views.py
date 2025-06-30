"""
plaid_link/views.py

Handles all Plaid-related API calls and views:
- Create link tokens
- Exchange public tokens for access tokens
- Fetch and store account data
- Render account linking page
"""

# Standard lib
import json
from datetime import date, timedelta

# Third-party
from decouple import config
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid.api import plaid_api

from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

# Django
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

# Local
from .models import PlaidItem, Account, Transaction
from .utils import encrypt_token, decrypt_token

import traceback



# --------------------------
# Create Plaid Link Token
# --------------------------

@login_required
def create_link_token(request):
    """
    Generates a link_token for initializing the Plaid Link flow.
    """
    # Setup Plaid client with sandbox credentials
    configuration = Configuration(
        host="https://sandbox.plaid.com",
        api_key={
            "clientId": config("PLAID_CLIENT_ID"),
            "secret": config("PLAID_SECRET"),
        }
    )
    client = plaid_api.PlaidApi(ApiClient(configuration))

    # Build request payload with current user ID
    user = LinkTokenCreateRequestUser(client_user_id=str(request.user.id))
    request_data = LinkTokenCreateRequest(
        user=user,
        client_name="Findash MVP",
        products=[
            Products("auth"),
            Products("transactions"),
            Products("investments"),
            Products("liabilities"),
        ],
        country_codes=[CountryCode("US")],
        language='en',
    )

    # Request Plaid to create a new link token
    response = client.link_token_create(request_data)
    return JsonResponse(response.to_dict())



# ----------------------------------
# Exchange Public Token for Access
# ----------------------------------

@require_POST
@login_required
def exchange_public_token(request):
    """
    Receives a public_token from the frontend,
    exchanges it for a secure access_token,
    encrypts it, and stores it in the database.
    """
    try:
        body = json.loads(request.body)
        public_token = body.get("public_token")

        if not public_token:
            return HttpResponseBadRequest("Missing public_token")

        # Setup Plaid client
        configuration = Configuration(
            host="https://sandbox.plaid.com",
            api_key={
                "clientId": config("PLAID_CLIENT_ID"),
                "secret": config("PLAID_SECRET"),
            }
        )
        client = plaid_api.PlaidApi(ApiClient(configuration))

        # Exchange public_token for access_token
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)

        access_token = exchange_response["access_token"]
        item_id = exchange_response["item_id"]

        # Store the encrypted access_token in the database
        plaid_item = PlaidItem(
            user=request.user,
            item_id=item_id,
            institution_name="Unknown"
        )
        plaid_item.set_access_token(access_token)
        plaid_item.save()

        # Automatically fetch accounts and transactions
        fetch_accounts(request)
        fetch_transactions(request)

        return JsonResponse({"status": "success"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)



# -----------------------------
# Fetch and Save Accounts
# -----------------------------

@require_POST
@login_required
def fetch_accounts(request):
    """
    Fetches the user's financial accounts from all PlaidItems
    and stores/updates them in the database.
    """
    from django.conf import settings
    import traceback
    print("🔍 DEBUG mode is:", settings.DEBUG)

    try:
        # Get all PlaidItems for the user
        plaid_items = PlaidItem.objects.filter(user=request.user)

        if not plaid_items.exists():
            return JsonResponse({"error": "No linked Plaid items"}, status=404)

        # Setup Plaid client
        configuration = Configuration(
            host="https://sandbox.plaid.com",
            api_key={
                "clientId": config("PLAID_CLIENT_ID"),
                "secret": config("PLAID_SECRET"),
            }
        )
        client = plaid_api.PlaidApi(ApiClient(configuration))

        all_accounts = []

        for plaid_item in plaid_items:
            access_token = plaid_item.get_access_token()

            # Call /accounts/get for this access token
            request_data = AccountsGetRequest(access_token=access_token)
            response = client.accounts_get(request_data)
            accounts = response.to_dict()["accounts"]
            all_accounts.extend(accounts)

            # Save or update each account
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

        response = JsonResponse({"status": "success", "count": len(all_accounts)})
        response["HX-Trigger"] = "refreshComplete"
        return response

    except Exception as e:
        print("🔴 ERROR in fetch_accounts")
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)



# -----------------------------
# Fetch and Save Transactions
# -----------------------------

@require_POST
@login_required
def fetch_transactions(request):
    """
    Fetches transactions from Plaid and stores them in the database.
    """
    try:
        from .models import Transaction  # If not imported at top

        # Get user's PlaidItem and access token
        plaid_item = PlaidItem.objects.get(user=request.user)
        access_token = plaid_item.get_access_token()

        # Setup Plaid client
        configuration = Configuration(
            host="https://sandbox.plaid.com",
            api_key={
                "clientId": config("PLAID_CLIENT_ID"),
                "secret": config("PLAID_SECRET"),
            }
        )
        client = plaid_api.PlaidApi(ApiClient(configuration))

        # Date range for the last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        # Fetch transactions
        request_data = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date
        )
        response = client.transactions_get(request_data)
        transactions = response.to_dict()["transactions"]

        # Build map of Plaid account IDs to Account objects
        account_map = {
            acct.account_id: acct
            for acct in Account.objects.filter(plaid_item=plaid_item)
        }

        # Store transactions in DB
        created_count = 0
        for txn in transactions:
            Transaction.objects.update_or_create(
                transaction_id=txn["transaction_id"],
                defaults={
                    "account": account_map[txn["account_id"]],
                    "name": txn["name"],
                    "amount": txn["amount"],
                    "date": txn["date"],
                    "category_main": txn["category"][0] if txn.get("category") else None,
                    "category_detailed": txn["category"][1] if txn.get("category") and len(txn["category"]) > 1 else None,
                    "merchant_name": txn.get("merchant_name"),
                    "payment_channel": txn.get("payment_channel"),
                }
            )
            created_count += 1

        return JsonResponse({"status": "success", "count": created_count})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# -----------------------------
# Render Link Page
# -----------------------------

@login_required
def link_account(request):
    """
    Renders the Plaid account linking page.
    Used after registration or when user manually clicks “Add Account.”
    """
    return render(request, 'plaid_link/link_account.html')
