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

    def test_action_create_success(self):
        action_querySet = UserAction.objects.all()
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
            'password1': 'testtest1231',
            'password2': 'testtest1231',
            'first_name': 'vicky',
            'last_name': 'yaya',
            'date_of_birth': "01/01/2011",
            'phone': '5849939393',
            'city': "SF",
            'country': 'USA',
            'state': 'CA',
            'over_eighteen': 'false',
            'zipcode': '92929'

        }, format='json')
        print("!!!!" + str(response.content))
        print("!!!!" + str(response.status_code))
        assert response.status_code == 201
        user = CustomUser.objects.filter(username="vickytestsignup")
        self.assertTrue(UserAction.objects.filter(user=user[0], event_type=2).exists())
        self.assertEqual(UserAction.objects.filter(event_type=2).count(), 1)
