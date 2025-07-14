"""
plaid_link/views/exchange.py

Handles:
- Exchanging public_token for access_token
"""

import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

from plaid_link.models import PlaidItem
from plaid_link.utils import get_plaid_client
from plaid_link.views.accounts import fetch_accounts
from plaid_link.views.transactions import fetch_transactions

@require_POST
@login_required
def exchange_public_token(request):
    """
    Exchanges the public token for an access token after the user completes the Plaid Link flow.
    """
    try:
        # Parse the request body to get the public token
        body = json.loads(request.body)
        public_token = body.get("public_token")

        # Validate that the public token is provided
        if not public_token:
            return HttpResponseBadRequest("Missing public_token")

        # Setup Plaid client
        client = get_plaid_client()

        # Exchange the public token for an access token
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)

        # Extract the access token and item ID from the response
        access_token = exchange_response["access_token"]
        item_id = exchange_response["item_id"]

        # Encrypt the access token and save it in the database
        plaid_item = PlaidItem(user=request.user, item_id=item_id, institution_name="Unknown")
        plaid_item.set_access_token(access_token)
        plaid_item.save()

        # Automatically fetch accounts and transactions after linking
        fetch_accounts(request)
        fetch_transactions(request)

        # Return a success response
        return JsonResponse({"status": "success"})

    except Exception as e:
        # Handle any exceptions and return an error response
        return JsonResponse({"error": str(e)}, status=400)
