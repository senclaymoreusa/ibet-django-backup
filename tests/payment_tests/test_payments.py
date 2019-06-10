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
    @classmethod
    def setUp(self):
        self.user = CustomUser.objects.create_superuser(username='angela', email = 'angela@test.com', phone='1239385544', password="testtest")
        user.main_wallet += 100
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

    def test_submit_deposit_url(self):
        
        response = self.client.post(reverse('submit_Deposit'), {
            'orderId' : 'ibet-9999',
            'amount' : '10.00',
            'currency' : 'IDR',
            'dateTime': '20181026T181035+03:00',
            'language': 'en-Us',
            'depositorUserId': 'angela',
            'depositorTier': '0',
            'depositMethod':  'LBT_ONLINE',
            'depositorEmail': 'angela@test.com',
            'depositorName': 'angela',
            'redirectUrl': 'https://www.google.com',
            'messageAuthenticationCode': '23e2d0bdc49e45070e5cc510c5371de024551b96bb9c751b2c6ad624e2c58558',
        }, format='json')
        assert response.status_code == 200
        
        self.assertTrue(Transaction.objects.filter(transaction_type=0).exists())
        self.assertFalse(Transaction.objects.filter(transaction_type=1).exists())
        

    def test_submit_payout_url(self):
        
        response = self.client.post(reverse('submit_Payout'), {
            'orderId' : 'ibet-99999',
            'amount' : '10.00',
            'currency' : 'CNY',
            'dateTime': '20181026T181035+03:00',
            'language': 'en-Us',
            'depositorUserId': 'angela',
            'depositorTier': '0',
            'depositMethod':  'LOCAL_BANK_TRANSFER',
            'depositorEmail': 'angela@test.com',
            'depositorName': 'angela',
            'redirectUrl': 'https://www.google.com',
            'messageAuthenticationCode': '70e774e4089fa2585441d57dac345681b0fb9941a4fa95e7107b399ac8786bb1',
        }, format='json')
        assert response.status_code == 200
        
        self.assertTrue(Transaction.objects.filter(transaction_type=0).exists())
        self.assertFalse(Transaction.objects.filter(transaction_type=1).exists())
    def test_get_payout_transaction(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user.auth_token.key)
        response = self.client.get(reverse('payout_Transaction'))
        self.assertEqual(response.status_code, 200)
    def test_transaction_update(self):
        response = self.client.post(reverse('transaction_status_update'), {
            'order_id': 'ibet-2019',
            'user_id': 'angela',
            'status': 'PENDING',
        }, format='json')
        assert response.status_code == 200
        user = CustomUser.objects.get(username='angela')
        self.assertTrue(Transaction.objects.filter(status=2).exists())
        self.assertFalse(Transaction.objects.filter(status=0).exists())
    def test_payout_method(self):
        response = self.client.post(reverse('payout_Method'), {
            'currency': 'CNY',
        }, format='json')
        self.assertEqual(response.status_code, 200)
    def test_payout_banklist(self):
        response = self.client.post(reverse('payout_Banklist'), {
            'currency': 'CNY',
            'method': 'LOCAL_BANK_TRANSFER',
        }, format='json')
        self.assertEqual(response.status_code, 200)
    def test_payout_banklimits(self):
        response = self.client.post(reverse('payout_Banklimits'), {
            'currency': 'CNY',
            'method': 'LOCAL_BANK_TRANSFER',
            'bank': 'BOSHCN',
        }, format='json')
        self.assertEqual(response.status_code, 200)
    def test_paypal_create_payment(self):
        response = self.client.post(reverse('paypal_Create_Payment'), {
            'orderId': 'ibet_1111',
            'currency': 'USD',
            'amount': '10',
            'user': 'angela',
        }, format='json')
        self.assertEqual(response.status_code, 200)
          

