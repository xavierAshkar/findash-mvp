"""
users/tests.py

Test suite for the Users application.
- User registration
- User login/logout
- Home page access
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.logout_url = reverse('core:logout')
        self.home_url = reverse('home')
        self.link_account_url = reverse('plaid:link_account')

    # Home page still public
    def test_home_view_accessible(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

    # Registration GET shows form
    def test_register_get_displays_form(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign Up')

    # Registration POST creates user and redirects (auto-login)
    def test_register_post_creates_user_and_redirects(self):
        response = self.client.post(self.register_url, {
            'email': 'user@test.com',
            'full_name': 'Test User',
            'password1': 'Securepass123!',
            'password2': 'Securepass123!'
        })
        # Expect redirect after register
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.link_account_url)

        # User should exist and be logged in
        self.assertTrue(User.objects.filter(email='user@test.com').exists())
        self.assertIn('sessionid', self.client.cookies)

    # Login with valid credentials redirects
    def test_login_with_valid_credentials(self):
        User.objects.create_user(email='user@test.com', full_name='Test User', password='securepass123')
        response = self.client.post(self.login_url, {
            'username': 'user@test.com',
            'password': 'Securepass123!'
        })
        self.assertEqual(response.status_code, 302)

    # Logout redirects to login page
    def test_logout_redirects_to_login(self):
        user = User.objects.create_user(email='logout@test.com', full_name='Bye', password='bye12345')
        self.client.login(username='logout@test.com', password='bye12345')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
