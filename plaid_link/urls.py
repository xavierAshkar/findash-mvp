from django.urls import path
from .views import create_link_token, exchange_public_token, fetch_accounts, fetch_transactions, sync_all, link_account

app_name = 'plaid'

urlpatterns = [
    # Create Plaid Link Token (to start the Plaid Link flow)
    path('create-link-token/', create_link_token, name='create_link_token'),

    # Exchange Public Token for Access Token (after user completes Plaid Link flow)
    path('exchange-token/', exchange_public_token, name='exchange_public_token'),

    # Link an account to the user's profile
    path('link-account/', link_account, name='link_account'),

    # Fetch accounts and transactions
    path('fetch-accounts/', fetch_accounts, name='fetch_accounts'),
    path('fetch-transactions/', fetch_transactions, name="fetch_transactions"),

    # Sync all accounts and transactions
    path("sync_all/", sync_all, name="sync_all"),
]