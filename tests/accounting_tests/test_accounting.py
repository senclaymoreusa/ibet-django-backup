import datetime

from django.test import TestCase

from accounting.models import (
    Transaction,
    ThirdParty,
    DepositChannel,
    WithdrawChannel,
    DepositAccessManagement,
    WithdrawAccessManagement
)

from users.models import (
    CustomerUser,
)

# Test Accounting Model
class AccountingModelTest(TestCase):
    @classmethod
    def setUpTestData(self):
        deposit_transaction = Transaction.objects.create(
            user = CustomUser.objects.create_superuser(
                username='wluuuu_test',
                email = 'wluuuutest@gmail.com', 
                phone='2028903727', 
                password="wluuuutest"
            ),
            transaction_type = 0,
            amount = 10.22,
            status = 0,
        )
        deposit_transaction.save()