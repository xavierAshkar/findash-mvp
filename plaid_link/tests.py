import json
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from plaid_link.models import PlaidItem, Account, Transaction

User = get_user_model()

class PlaidViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="x@example.com", password="pw")
        self.client.login(email="x@example.com", password="pw")

    # Test: Link token creation works and returns a token (mocked)
    @patch("plaid_link.utils.get_plaid_client")
    def test_create_link_token_works(self, mock_get_client):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {"link_token": "mock-token"}
        mock_client.link_token_create.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = self.client.get(reverse('plaid:create_link_token'))
        self.assertEqual(response.status_code, 200)
        self.assertIn("link_token", response.json())



    # Test: Fetch accounts fails cleanly if no PlaidItem is linked
    def test_fetch_accounts_requires_plaiditem(self):
        response = self.client.post(reverse('plaid:fetch_accounts'))
        self.assertEqual(response.status_code, 404)  # no item linked yet

    # Test: Fetch transactions fails gracefully without a PlaidItem
    def test_fetch_transactions_requires_plaiditem(self):
        response = self.client.post(reverse('plaid:fetch_transactions'))
        self.assertEqual(response.status_code, 404)
        self.assertIn("No linked Plaid items", response.json().get("error", ""))

    # Test: Mock token exchange and assert PlaidItem is saved
    @patch("plaid_link.views.exchange.fetch_transactions")
    @patch("plaid_link.views.exchange.fetch_accounts")
    @patch("plaid_link.views.exchange.get_plaid_client")
    def test_exchange_token_creates_plaid_item(self, mock_get_client, mock_fetch_accounts, mock_fetch_transactions):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.__getitem__.side_effect = lambda key: {
            "access_token": "mock-access-token",
            "item_id": "mock-item-id"
        }[key]
        mock_client.item_public_token_exchange.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = self.client.post(
            reverse("plaid:exchange_public_token"),
            content_type="application/json",
            data=json.dumps({"public_token": "fake-public-token"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(PlaidItem.objects.filter(user=self.user).exists())



