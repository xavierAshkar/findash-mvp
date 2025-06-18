from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.logout_url = reverse('users:logout')
        self.home_url = reverse('home')

    # Test: Ensure homepage is publicly accessible
    def test_home_view_accessible(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

    # Test: Ensure GET request to register page loads the signup form
    def test_register_get_displays_form(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign Up')

    # Test: Ensure POST to register creates a user and logs them in
    def test_register_post_creates_user_and_logs_in(self):
        response = self.client.post(self.register_url, {
            'email': 'user@test.com',
            'full_name': 'Test User',
            'password1': 'securepass123',
            'password2': 'securepass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='user@test.com').exists())
        self.assertIn('sessionid', self.client.cookies)

    # Test: Ensure login page works with valid credentials
    def test_login_with_valid_credentials(self):
        User.objects.create_user(email='user@test.com', full_name='Test User', password='securepass123')
        response = self.client.post(self.login_url, {
            'username': 'user@test.com',
            'password': 'securepass123'
        })
        self.assertEqual(response.status_code, 302)

    # Test: Ensure logout works and redirects to login page
    def test_logout_redirects_to_login(self):
        user = User.objects.create_user(email='logout@test.com', full_name='Bye', password='bye12345')
        self.client.login(username='logout@test.com', password='bye12345')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
