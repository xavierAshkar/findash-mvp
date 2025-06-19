from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from plaid_link.models import PlaidItem, Account, Transaction
from core.models import Budget

User = get_user_model()

class CoreViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="dash@example.com", password="pw")
        self.client.login(email="dash@example.com", password="pw")

    # Test: Redirect to link flow if no accounts are linked
    def test_dashboard_redirects_if_no_accounts(self):
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('plaid:link_account'), response.url)

    # Test: POST to budgets creates a new Budget object
    def test_budget_post_creates_budget(self):
        response = self.client.post(reverse('core:budgets'), {
            'name': 'Food',
            'categories': ['groceries', 'restaurants'],
            'amount': '250.00',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Budget.objects.filter(user=self.user, name='Food').exists())

    # Test: Accounts view shows all cash accounts linked to the user
    def test_accounts_view_shows_cash_accounts(self):
        item = PlaidItem.objects.create(user=self.user, item_id='mock')
        Account.objects.create(
            plaid_item=item,
            account_id='x',
            name='Checking',
            type='depository',
            subtype='checking',
            current_balance=100
        )
        response = self.client.get(reverse('core:accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Checking')

    # Test: Accounts view shows all credit accounts linked to the user
    def test_accounts_view_shows_credit_accounts(self):
        item = PlaidItem.objects.create(user=self.user, item_id='mock')
        Account.objects.create(
            plaid_item=item,
            account_id='c',
            name='Credit Card',
            type='credit',
            subtype='credit card',
            current_balance=250
        )
        response = self.client.get(reverse('core:accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Credit Card')

    # Test: Only credit accounts are shown
    def test_credit_accounts_filter(self):
        item = PlaidItem.objects.create(user=self.user, item_id='mock')
        Account.objects.create(plaid_item=item, account_id='c', name='Credit Card', type='credit', subtype='credit card')
        response = self.client.get(reverse('core:credit_accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Credit Card')

    # Test: Tagging a transaction sets the user_tag field
    def test_tag_transaction_applies_tag(self):
        item = PlaidItem.objects.create(user=self.user, item_id='mock')
        account = Account.objects.create(plaid_item=item, account_id='a', name='A', type='depository', subtype='checking')
        txn = Transaction.objects.create(account=account, transaction_id='t', name='Txn', amount=12, date='2024-06-01')

        response = self.client.post(reverse('core:tag_transaction', args=[txn.id]), {
            'tag': 'custom-tag'
        })
        self.assertEqual(response.status_code, 302)
        txn.refresh_from_db()
        self.assertEqual(txn.user_tag, 'custom-tag')
