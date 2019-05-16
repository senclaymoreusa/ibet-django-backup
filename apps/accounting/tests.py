from django.test import TestCase, Client
from .models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from rest_framework.test import APIRequestFactory
from django.core.urlresolvers import reverse


# class ViewTest(TestCase):
#     def test_deposit_method_url(self):
#         c = Client()
#         response = c.get('/accounting/api/deposit_method')
#         self.assertEqual(response.status_code, 200)


    
