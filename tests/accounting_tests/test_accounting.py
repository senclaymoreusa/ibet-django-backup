from django.test import TestCase
from django.urls import reverse

from accounting.models import (
    Transaction,
    DepositChannel,
    WithdrawChannel,
    DepositAccessManagement,
    WithdrawAccessManagement
)

from users.models import (
    CustomUser,
)

import json

# Test Accounting Model
class AccountingModelTest(TestCase):
    @classmethod
    def setUpTestData(self):
        user = CustomUser.objects.create_superuser(
            username='wluuuu_test',
            email = 'wluuuuakjdh@gmail.com', 
            phone='2028903727', 
            password="wluuuu"
        )
        user.balance += 100
        user.save()
    
    # create transaction from frontend
    def test_transaction_create_success_when_deposit_money(self):
        response = self.client.post(reverse('add_withdraw_balance'), {
            'username': 'wluuuu_test',
            'type': 'add',
            'balance': '20',
        }, format='json')
        assert response.status_code == 200
        user = CustomUser.objects.get(id=1)
        self.assertTrue(Transaction.objects.filter(transaction_type=0).exists())
        self.assertFalse(Transaction.objects.filter(transaction_type=1).exists())
        self.assertEqual(user.balance, 120)
    
    def test_transaction_create_success_when_withdraw_money_than_balance(self):
        response = self.client.post(reverse('add_withdraw_balance'), {
            'username': 'wluuuu_test',
            'type': 'withdraw',
            'balance': '20',
        }, format='json')
        assert response.status_code == 200
        user = CustomUser.objects.get(id=1)
        self.assertEqual(response.content.decode("utf-8") , 'Withdraw Success')
        self.assertFalse(Transaction.objects.filter(transaction_type=0).exists()) 
        self.assertTrue(Transaction.objects.filter(transaction_type=1).exists())
        self.assertEqual(user.balance, 80)
    
    def test_transaction_create_failed_when_withdraw_money_than_balance(self):
        response = self.client.post(reverse('add_withdraw_balance'), {
            'username': 'wluuuu_test',
            'type': 'withdraw',
            'balance': '2000',
        }, format='json')
        assert response.status_code == 200
        user = CustomUser.objects.get(id=1)
        self.assertEqual(response.content.decode("utf-8") , 'The balance is not enough')
        self.assertFalse(Transaction.objects.filter(transaction_type=0).exists()) 
        self.assertFalse(Transaction.objects.filter(transaction_type=1).exists())
        self.assertEqual(user.balance, 100)

    # create transaction from backend model
    def test_create_deposit_transaction_from_admin(self):
        deposit_transaction = Transaction.objects.create(
            user_id=CustomUser.objects.get(id=1), 
            amount=100, 
            transaction_type=0,
        )
        self.assertEqual(Transaction.objects.filter(transaction_type=0).count(), 1) 
    
    def test_create_withdraw_transaction_from_admin(self):
        deposit_transaction = Transaction.objects.create(
            user_id=CustomUser.objects.get(id=1), 
            amount=100, 
            transaction_type=1,
        )
        self.assertEqual(Transaction.objects.filter(transaction_type=1).count(), 1)
    
    # create deposit channel from backend model
    def test_create_deposit_channel(self):
        deposit_channel = DepositChannel.objects.create(
            thridParty_name = 0,
        )
        self.assertEqual(DepositChannel.objects.count(), 1)
    
    # create withdraw channel from backend model
    def test_create_withdraw_channel(self):
        withdraw_channel = WithdrawChannel.objects.create(
            thridParty_name = 0,
        )
        self.assertEqual(WithdrawChannel.objects.count(), 1)

    def test_deposit_access_management(self):
        user = CustomUser.objects.get(id=1)
        deposit_channel = DepositChannel.objects.create(
            thridParty_name = 0,
        )
        deposit_access = DepositAccessManagement.objects.create(
            user_id = user,
            deposit_channel = deposit_channel,
        )
        self.assertTrue(DepositAccessManagement.objects.exists())
    
    def test_withdraw_access_management(self):
        user = CustomUser.objects.get(id=1)
        withdraw_channel = WithdrawChannel.objects.create(
            thridParty_name = 1,
        )
        withdraw_access = WithdrawAccessManagement.objects.create(
            user_id = user,
            withdraw_channel = withdraw_channel,
        )
        self.assertTrue(WithdrawAccessManagement.objects.exists())






