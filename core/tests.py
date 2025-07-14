from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from plaid_link.models import PlaidItem, Account, Transaction
from core.models import Budget, Tag

User = get_user_model()

class CoreViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="dash@example.com", password="pw")
        self.client.login(email="dash@example.com", password="pw")

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

    # Test: Tagging a transaction sets the user_tag field
    def test_tag_transaction_applies_tag(self):
        tag = Tag.objects.create(user=self.user, name="custom-tag")
        
        item = PlaidItem.objects.create(user=self.user, item_id='mock')
        account = Account.objects.create(
            plaid_item=item,
            account_id='acct1',
            name='Test Account',
            type='depository',
            subtype='checking',
            current_balance=100.0,
        )
        txn = Transaction.objects.create(
            account=account,
            transaction_id='txn1',
            name='Test Transaction',
            amount=12.34,
            date='2025-07-01',
        )

        response = self.client.post(reverse('core:tag_transaction', args=[txn.id]), {
            'tag': str(tag.id)
        })

        self.assertEqual(response.status_code, 302)
        txn.refresh_from_db()
        self.assertEqual(txn.tag, tag)
