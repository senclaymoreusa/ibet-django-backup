from django.test import TestCase
from django.test.client import Client

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient,APITestCase
from accounting.models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from django.urls import reverse
from users.models import (
    CustomUser
)

@classmethod
class ThirdPartyTestCases(TestCase):
    client_class = APIClient
    def setUp(self):
        self.user = CustomUser.objects.create_superuser(username='angela', email = 'angela@test.com', phone='1239385544', password="testtest")
        user.balance += 100
        user.save()
        Token.objects.create(user=self.user)
        super(ThirdPartyTestCases, self).setUp() 
 

    def test_deposit_method_url(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user.auth_token.key)
        response = self.client.get('/accounting/api/deposit_method')
        
        self.assertEqual(response.status_code, 200)
       

    def test_get_BankList_url(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user.auth_token.key)
        response = self.client.get('/accounting/api/get_BankList')
        self.assertEqual(response.status_code, 200)

    def test_get_BankLimits_url(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user.auth_token.key)
        response = self.client.get('/accounting/api/get_banklimits')
        self.assertEqual(response.status_code, 200)
        

