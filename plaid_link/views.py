from django.http import JsonResponse
from decouple import config

from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.configuration import Configuration
from plaid.api_client import ApiClient


def create_link_token(request):
    # Create API client configuration
    configuration = Configuration(
        host="https://sandbox.plaid.com",
        api_key={
            "clientId": config("PLAID_CLIENT_ID"),
            "secret": config("PLAID_SECRET"),
        }
    )
    api_client = ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)

    # Build the request data
    user = LinkTokenCreateRequestUser(client_user_id=str(request.user.id))
    request_data = LinkTokenCreateRequest(
        user=user,
        client_name="Findash MVP",
        products=[Products("auth"), Products("transactions")],
        country_codes=[CountryCode("US")],
        language='en',
    )

    # Send to Plaid
    response = client.link_token_create(request_data)

    # Return result
    return JsonResponse(response.to_dict())