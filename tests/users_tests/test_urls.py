from django.test import TestCase
from django.urls import reverse, resolve

from users.views import (
    AllSearchListView,
    SendEmail,
    LoginView,
    RegisterView
)

from games.views.views import GameDetailAPIListView

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
    # def test_api_games_resolves(self):
    #     url = reverse('api_games')
    #     self.assertEqual(resolve(url).func.view_class, GameAPIListView)

    # Test get game detail
    def test_api_games_detail_resolves(self):
        url = reverse('games_detail')
        self.assertEqual(resolve(url).func.view_class, GameDetailAPIListView)

    # Test get search list view
    def test_api_all_search_list_view_resolves(self):
        url = reverse('all_search_list_view')
        self.assertEqual(resolve(url).func.view_class, AllSearchListView)

    # Test send email
    def test_api_send_email_resolves(self):
        url = reverse('sendemail')
        self.assertEqual(resolve(url).func.view_class, SendEmail)
