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

<<<<<<< HEAD
from utils.constants import TRANSACTION_DEPOSIT, TRANSACTION_WITHDRAWAL, CURRENCY_CNY
=======
from utils.constants import TRANSACTION_DEPOSIT, TRANSACTION_WITHDRAWAL, CURRENCY_CNY
>>>>>>> 5956b84c0091f266a336e910041d814717f5587d

import json
from utils.constants import *

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
        user.main_wallet += 100
        user.save()
    
    # create transaction from frontend
    # def test_transaction_create_success_when_deposit_money(self):
    #     response = self.client.post(reverse('add_withdraw_balance'), {
    #         'username': 'wluuuu_test',
    #         'type': 'add',
    #         'balance': '20',
    #     }, format='json')
    #     assert response.status_code == 200
    #     user = CustomUser.objects.get(id=1)
    #     self.assertTrue(Transaction.objects.filter(transaction_type=1).exists())
    #     self.assertFalse(Transaction.objects.filter(transaction_type=0).exists())
    #     self.assertEqual(user.main_wallet, 120)
    
    # def test_transaction_create_success_when_withdraw_money_than_balance(self):
    #     response = self.client.post(reverse('add_withdraw_balance'), {
    #         'username': 'wluuuu_test',
    #         'type': 'withdraw',
    #         'balance': '20',
    #     }, format='json')
    #     assert response.status_code == 200
    #     user = CustomUser.objects.get(id=1)
    #     self.assertEqual(response.content.decode("utf-8") , 'Withdraw Success')
    #     self.assertFalse(Transaction.objects.filter(transaction_type=0).exists()) 
    #     self.assertTrue(Transaction.objects.filter(transaction_type=1).exists())
    #     self.assertEqual(user.main_wallet, 80)
    
    # def test_transaction_create_failed_when_withdraw_money_than_balance(self):
    #     response = self.client.post(reverse('add_withdraw_balance'), {
    #         'username': 'wluuuu_test',
    #         'type': 'withdraw',
    #         'balance': '2000',
    #     }, format='json')
    #     assert response.status_code == 200
    #     user = CustomUser.objects.get(id=1)
    #     self.assertEqual(response.content.decode("utf-8") , 'The balance is not enough')
    #     self.assertFalse(Transaction.objects.filter(transaction_type=0).exists()) 
    #     self.assertFalse(Transaction.objects.filter(transaction_type=1).exists())
    #     self.assertEqual(user.main_wallet, 100)

    # create transaction from backend model
    def test_create_deposit_transaction_from_admin(self):
        deposit_transaction = Transaction.objects.create(
            user_id=CustomUser.objects.get(id=1), 
            amount=100, 
<<<<<<< HEAD
            transaction_type=TRANSACTION_DEPOSIT,
            currency=CURRENCY_CNY,
            method="test_method",
            remark="test_remark",
        )
        self.assertEqual(Transaction.objects.filter(transaction_type=TRANSACTION_DEPOSIT).count(), 1) 
=======
            transaction_type=TRANSACTION_DEPOSIT,
            currency=CURRENCY_CNY,
            method="test_method",
            remark="test_remark",
        )
        self.assertEqual(Transaction.objects.filter(transaction_type=TRANSACTION_DEPOSIT).count(), 1) 
>>>>>>> ae121f71dc19adc683835c34b47395db8f9d00d2
    
    def test_create_withdraw_transaction_from_admin(self):
        deposit_transaction = Transaction.objects.create(
            user_id=CustomUser.objects.get(id=1), 
            amount=100, 
<<<<<<< HEAD
<<<<<<< HEAD
            transaction_type=TRANSACTION_WITHDRAWAL,
            currency=CURRENCY_CNY,
            method="test_method",
            remark="test_remark",
        )
        self.assertEqual(Transaction.objects.filter(transaction_type=TRANSACTION_WITHDRAWAL).count(), 1)
=======
            transaction_type=TRANSACTION_WITHDRAWAL,
=======
            transaction_type=TRANSACTION_WITHDRAWAL,
>>>>>>> 5956b84c0091f266a336e910041d814717f5587d
            currency=CURRENCY_CNY,
            method="test_method",
            remark="test_remark",
        )
<<<<<<< HEAD
        self.assertEqual(Transaction.objects.filter(transaction_type=TRANSACTION_WITHDRAWAL).count(), 1)
>>>>>>> ae121f71dc19adc683835c34b47395db8f9d00d2
=======
        self.assertEqual(Transaction.objects.filter(transaction_type=TRANSACTION_WITHDRAWAL).count(), 1)
>>>>>>> 5956b84c0091f266a336e910041d814717f5587d
    
    # create deposit channel from backend model
    def test_create_deposit_channel(self):
        deposit_channel = DepositChannel.objects.create(
            method="test method",
            channel="test channel",
            market= ibetVN
        )
        self.assertEqual(DepositChannel.objects.count(), 1)
    
    # create withdraw channel from backend model
    def test_create_withdraw_channel(self):
        withdraw_channel = WithdrawChannel.objects.create(
            method="test method",
            channel="test channel",
            market= ibetVN
        )
        self.assertEqual(WithdrawChannel.objects.count(), 1)

    def test_deposit_access_management(self):
        user = CustomUser.objects.get(id=1)
        deposit_channel = DepositChannel.objects.create(
            method="test method",
            channel="test channel",
            market= ibetVN
        )
        deposit_access = DepositAccessManagement.objects.create(
            user_id = user,
            deposit_channel = deposit_channel,
        )
        self.assertTrue(DepositAccessManagement.objects.exists())
    
    def test_withdraw_access_management(self):
        user = CustomUser.objects.get(id=1)
        withdraw_channel = WithdrawChannel.objects.create(
            method="test method",
            channel="test channel",
            market= ibetVN
        )
        withdraw_access = WithdrawAccessManagement.objects.create(
            user_id = user,
            withdraw_channel = withdraw_channel,
        )
        self.assertTrue(WithdrawAccessManagement.objects.exists())