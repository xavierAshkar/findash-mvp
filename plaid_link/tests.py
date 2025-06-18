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

    # Test: Link token endpoint returns valid JSON
    def test_create_link_token_works(self):
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
        self.assertEqual(response.status_code, 500)  # error handled gracefully

    # Test: Mock token exchange and assert PlaidItem is saved
    @patch("plaid_link.views.plaid_api.PlaidApi.item_public_token_exchange")
    def test_exchange_token_creates_plaid_item(self, mock_exchange):
        # Setup mock Plaid response
        mock_response = MagicMock()
        mock_response.__getitem__.side_effect = lambda key: {
            "access_token": "mock-access-token",
            "item_id": "mock-item-id"
        }[key]
        mock_exchange.return_value = mock_response

        # Call exchange endpoint with fake token
        response = self.client.post(
            reverse("plaid:exchange_public_token"),
            content_type="application/json",
            data=json.dumps({"public_token": "fake-public-token"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(PlaidItem.objects.filter(user=self.user).exists())

        item = PlaidItem.objects.get(user=self.user)
        self.assertEqual(item.item_id, "mock-item-id")
