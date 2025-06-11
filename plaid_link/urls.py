from django.urls import path
from .views import create_link_token, exchange_public_token, fetch_accounts

urlpatterns = [
    path('create-link-token/', create_link_token, name='create_link_token'),
    path('exchange-token/', exchange_public_token, name='exchange_public_token'),
    path("fetch-accounts/", fetch_accounts, name="fetch_accounts"),
]
