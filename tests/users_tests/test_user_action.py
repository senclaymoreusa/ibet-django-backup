import datetime
from django.test import TestCase, Client
from rest_framework.test import APITestCase
from django.urls import reverse


from users.forms import (
    UserCreationForm
)

from users.models import (
    CustomUser,
    UserAction
)

import json

# Test User Action Model
class UserActionModelTest(APITestCase):

    def setUp(self):
        # user = CustomUser.objects.create(username = 'vicky_test', email = 'vicky@test.com', phone='1233355544', password="testtest")
        # use superuser instead customuser to bypass account activation
        user = CustomUser.objects.create_superuser(username='vicky_test', email = 'vicky@test.com', phone='1233355544', password="testtest")


        test_user_action = UserAction.objects.create(
            ip_addr = "127.0.0.1",
            event_type = 0,  #login
            user = user
        )
        test_user_action.save()
        user.main_wallet += 100
        user.save()

    def test_action_create_success(self):
        user = CustomUser.objects.filter(username="vicky_test")
        self.assertTrue(UserAction.objects.filter(user=user[0], event_type=0).exists())
        self.assertEqual(UserAction.objects.all().count(), 1)
        

    def test_action_create_success_when_login(self):
        response = self.client.post(reverse('api_login'), {
            'username': 'vicky_test',
            'password': 'testtest'
        }, format='json')
        assert response.status_code == 200
        user = CustomUser.objects.filter(username="vicky_test")
        self.assertTrue(UserAction.objects.filter(user=user[0], event_type=0).exists())
        self.assertEqual(UserAction.objects.all().count(), 2)


    def test_action_create_success_when_signup(self):
        response = self.client.post(reverse('api_register'), {
            'username': 'vickytestsignup',
            'email': 'vicky_signup@gamil.com',
            'password': 'testtest1231',
            'first_name': 'vicky',
            'last_name': 'yaya',
            'date_of_birth': "01/01/2011",
            'phone': '5849939393',
            'street_address_1': 'aaaaaaaaaa',
            'city': "SF",
            'country': 'USA',
            'state': 'CA',
            'over_eighteen': 'true',
            'zipcode': '92929',
            'language': 'english'

        }, format='json')
        print(response.status_code)
        assert response.status_code == 201
        user = CustomUser.objects.filter(username="vickytestsignup")
        self.assertTrue(UserAction.objects.filter(user=user[0], event_type=2).exists())
        self.assertEqual(UserAction.objects.filter(user=user[0], event_type=2).count(), 1)
        self.assertEqual(UserAction.objects.all().count(), 2)


    # This will handle by test_accounting file
    # def test_action_create_success_when_add_money(self):
    #     response = self.client.post(reverse('add_withdraw_balance'), {
    #         'username': 'vicky_test',
    #         'type': 'add',
    #         'balance': '100',
    #     }, format='json')
    #     assert response.status_code == 200
    #     user = CustomUser.objects.filter(username="vicky_test")
    #     self.assertTrue(UserAction.objects.filter(user=user[0], event_type=3, dollar_amount=100).exists())
    #     self.assertEqual(UserAction.objects.filter(user=user[0], event_type=3, dollar_amount=100).count(), 1)
    #     self.assertEqual(UserAction.objects.all().count(), 2)
    #     self.assertEqual(user[0].main_wallet, 200)

    
    # def test_action_create_success_when_withdraw_money(self):
    #     response = self.client.post(reverse('add_withdraw_balance'), {
    #         'username': 'vicky_test',
    #         'type': 'withdraw',
    #         'balance': '10',
    #     }, format='json')
    #     assert response.status_code == 200
    #     user = CustomUser.objects.filter(username="vicky_test")
    #     self.assertTrue(UserAction.objects.filter(user=user[0], event_type=4, dollar_amount=10).exists())
    #     self.assertEqual(UserAction.objects.filter(user=user[0], event_type=4, dollar_amount=10).count(), 1)
    #     self.assertEqual(UserAction.objects.all().count(), 2)
    #     self.assertEqual(user[0].main_wallet, 90)

    def test_action_fail_when_not_enough_money_to_withdraw(self):
        response = self.client.post(reverse('add_withdraw_balance'), {
            'username': 'vicky_test',
            'type': 'withdraw',
            'balance': '1000',
        }, format='json')
        assert response.status_code == 200
        self.assertEqual(response.content.decode("utf-8") , 'The balance is not enough')
        self.assertEqual(UserAction.objects.all().count(), 1)    # withdraw not success
        user = CustomUser.objects.filter(username="vicky_test")
        self.assertEqual(user[0].main_wallet, 100)
        