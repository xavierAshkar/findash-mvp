"""
plaid_link/views/link.py

Handles:
- Creating link token
- Rendering Plaid Link page
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from ..utils import get_plaid_client

@login_required
def create_link_token(request):
    """
    Generates a link_token for initializing the Plaid Link flow.
    """
    # Setup Plaid client
    client = get_plaid_client()

    # Build request payload with current user ID
    user = LinkTokenCreateRequestUser(client_user_id=str(request.user.id))
    request_data = LinkTokenCreateRequest(
        user=user,
        client_name="Findash MVP",
        products=[Products("transactions")],
        country_codes=[CountryCode("US")],
        language='en',
    )
    # Request Plaid to create a new link token
    response = client.link_token_create(request_data)
    # Return the link token as JSON response
    return JsonResponse(response.to_dict())

@login_required
def link_account(request):
    """
    Render the Plaid Link account linking page.
    This page will use the link token to initialize the Plaid Link flow.
    """
    return render(request, 'plaid_link/link_account.html')
