
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
import simplejson as json
from django.db import transaction
from users.views.helper import checkUserBlock
from users.models import CustomUser, UserWallet
from games.models import GameProvider
import logging
from games.views.eagameviews import requestEADeposit, requestEAWithdraw, getEAWalletBalance
from games.views.onebookviews import fundTransfer, checkUserBalance
from games.views.kygameviews import kyTransfer, kyBalance
from games.views.aggamesviews import agFundTransfer, getBalance
from games.views.ptgameviews import ptTransfer
from games.views.gameplayintviews import getGPIBalance, gpiTransfer
import simplejson as json
import decimal


logger = logging.getLogger('django')

class TransferDeposit():

    def __init__(self, user, amount, from_wallet):
        self.user = user
        self.amount = amount
        self.from_wallet = from_wallet
        # self.game_func_options = {'eaDeposit': self.eaDeposit,
        #                           'onebookWithdraw': self.onebookWithdraw,
        #                          }

    def EADeposit(self):
        return requestEADeposit(self.user, self.amount, self.from_wallet)

    def OnebookDeposit(self):
        return fundTransfer(self.user, self.amount, self.from_wallet, "1", "1", "2")

    def KYDeposit(self):
        return kyTransfer(self.user, self.amount, self.from_wallet, 0)

    def AGDeposit(self):
        return agFundTransfer(self.user, self.from_wallet, self.amount, "IN")
    
    def PTDeposit(self):
        return ptTransfer(self.user, self.amount, self.from_wallet, 0)

    def GPIDeposit(self):
        return gpiTransfer(self.user, self.amount, self.from_wallet, 0)


    
class TransferWithdraw():

    def __init__(self, user, amount, to_wallet):
        self.user = user
        self.amount = amount
        self.to_wallet = to_wallet
        # self.game_func_options = {'eaWithdraw': self.eaWithdraw,
        #                           'onebookWithdraw': self.onebookWithdraw,

        #                          }

    def EAWithdraw(self):
        return requestEAWithdraw(self.user, self.amount, self.to_wallet)

    def OnebookWithdraw(self):
        return fundTransfer(self.user, self.amount, self.to_wallet, "0", "1", "2")

    def KYWithdraw(self):
        return kyTransfer(self.user, self.amount, self.to_wallet, 1)

    def AGWithdraw(self):
        return agFundTransfer(self.user, self.to_wallet, self.amount, "OUT")

    def PTWithdraw(self):
        return ptTransfer(self.user, self.amount, self.to_wallet, 1)

    def GPIWithdraw(self):
        return gpiTransfer(self.user, self.amount, self.to_wallet, 1)


class CheckTransferWallet():

    def __init__(self, user):
        self.user = user
    
    def EACheckAmount(self):
        obj = getEAWalletBalance(self.user)
        obj = json.loads(obj)
        balance = 0
        if obj and obj['balance']:
            balance = decimal.Decimal(obj['balance'])
        return balance
         
    def OnebookCheckAmount(self):
        obj = checkUserBalance(self.user)
        obj = json.loads(obj)
        balance = 0
        if obj and obj['balance']:
            balance = decimal.Decimal(obj['balance'])
        return balance
        
    def AGCheckAmount(self):
        obj = getBalance(self.user)
        obj = json.loads(obj)
        balance = 0
        if obj and obj['balance']:
            balance = decimal.Decimal(obj['balance'])
        return balance

    def BBINCheckAmount(self):
        return 0

    def OPUSCheckAmount(self):
        return 0

    def GPICheckAmount(self):
        balance = decimal.Decimal(getGPIBalance(self.user))
        print(balance)
        return balance

    def PTCheckAmount(self):
        return 0

    def KYCheckAmount(self):
        balance = kyBalance(self.user)
        return balance