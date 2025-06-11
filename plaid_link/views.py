from django.http import JsonResponse
from decouple import config

from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid.api import plaid_api

from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode


def create_link_token(request):
    # Configure Plaid client using sandbox credentials from .env
    configuration = Configuration(
        host="https://sandbox.plaid.com",
        api_key={
            "clientId": config("PLAID_CLIENT_ID"),
            "secret": config("PLAID_SECRET"),
        }
    )
    api_client = ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)

    # Build request payload with user ID and required Plaid products
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

    # Send request to Plaid and return the link_token
    response = client.link_token_create(request_data)
    return JsonResponse(response.to_dict())

# -------------------------
# Exchange Public Token View
# -------------------------

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
import json

from .models import PlaidItem
from .utils import encrypt_token

from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest


@csrf_exempt  # TEMP: replace with real CSRF protection later
@require_POST
@login_required
def exchange_public_token(request):
    """
    Receives a public_token, exchanges it for an access_token,
    encrypts it, and stores it linked to the current user.
    """
    try:
        body = json.loads(request.body)
        public_token = body.get("public_token")

        if not public_token:
            return HttpResponseBadRequest("Missing public_token")

        configuration = Configuration(
            host="https://sandbox.plaid.com",
            api_key={
                "clientId": config("PLAID_CLIENT_ID"),
                "secret": config("PLAID_SECRET"),
            }
        )
        client = plaid_api.PlaidApi(ApiClient(configuration))

        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)

        access_token = exchange_response["access_token"]
        item_id = exchange_response["item_id"]

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