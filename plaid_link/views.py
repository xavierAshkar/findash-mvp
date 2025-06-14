"""
plaid_link/views.py

Handles all Plaid-related API calls and views:
- Create link tokens
- Exchange public tokens for access tokens
- Fetch and store account data
- Render account linking page
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from decouple import config
import json

from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid.api import plaid_api

from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

from .models import PlaidItem, Account
from .utils import encrypt_token



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
    Fetches the user's financial accounts from Plaid
    and stores/updates them in the database.
    """
    try:
        # Get user's PlaidItem
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

        # Call /accounts/get endpoint
        request_data = AccountsGetRequest(access_token=access_token)
        response = client.accounts_get(request_data)
        accounts = response.to_dict()["accounts"]

        # Save or update accounts in DB
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

        return JsonResponse({"status": "success", "count": len(accounts)})

    except PlaidItem.DoesNotExist:
        return JsonResponse({"error": "Plaid item not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



# -----------------------------
# Render Link Page
# -----------------------------

@login_required
def link_account(request):
    """
    Renders the Plaid account linking page,
    or redirects to the dashboard if accounts are already linked.
    """
    has_plaid_item = PlaidItem.objects.filter(user=request.user).exists()

    if has_plaid_item:
        # User already linked an account — redirect to dashboard
        return redirect('core:dashboard')

    # Show account linking interface
    return render(request, 'plaid_link/link_account.html')