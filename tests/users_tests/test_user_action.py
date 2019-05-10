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
