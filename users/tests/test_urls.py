from django.test import TestCase
from django.urls import reverse, resolve

from users.views import (
    GameAPIListView,
    LoginView, 
    RegisterView 
)

# Create your tests here.

class UrlsTest(TestCase):
    # Test user register
    def test_register_resolves(self):
        url = reverse('api_register')
        self.assertEqual(resolve(url).func.view_class, RegisterView)

    # Test user log in
    def test_log_in_resolves(self):
        url = reverse('api_login')
        self.assertEqual(resolve(url).func.view_class, LoginView)

    # Test get game list
    def test_api_games_resolves(self):
        url = reverse('api_games')
        self.assertEqual(resolve(url).func.view_class, GameAPIListView)