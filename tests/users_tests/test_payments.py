from django.test import TestCase
from django.test.client import Client
from accounting.models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from django.urls import reverse



class ThirdPartyTestCases(TestCase):
    def setUp(self):
        self.client = Client()

    def test_deposit_method_url(self):
        response = self.client.get('/accounting/api/deposit_method')
        self.assertEqual(response.status_code, 200)

    def test_get_BankList_url(self):
        
        response = self.client.get('/accounting/api/get_BankList')
        self.assertEqual(response.status_code, 200)

    def test_get_BankLimits_url(self):
        
        response = self.client.get('/accounting/api/get_banklimits')
        self.assertEqual(response.status_code, 200)
        

