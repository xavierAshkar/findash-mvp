"""
plaid_link/views/sync.py

Handles:
- Combined sync of accounts + transactions
"""

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from plaid_link.views.accounts import fetch_accounts
from plaid_link.views.transactions import fetch_transactions
import traceback

@require_POST
@login_required
def sync_all(request):
    """
    Syncs both accounts and transactions for the authenticated user.
    This endpoint is called after the Plaid Link flow completes.
    - Fetches accounts and transactions for all linked Plaid items
    - Returns a success response with a trigger for frontend updates
    """
    try:
        # Fetch accounts and transactions
        fetch_accounts(request)
        fetch_transactions(request)

        # Return success response with a trigger for frontend updates
        response = JsonResponse({"status": "success"})
        response["HX-Trigger"] = "refreshComplete"
        return response
    
    except Exception as e:
        # Log the error and return an error response
        print("🔴 ERROR in sync_all")
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
