
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
import simplejson as json
from django.db import transaction
from users.views.helper import checkUserBlock
from users.models import CustomUser
import logging
from games.views.eagameviews import requestEADeposit, requestEAWithdraw
from games.views.onebookviews import fundTransfer


logger = logging.getLogger('django')

class TransferDeposit():

    def __init__(self, user, amount, from_wallet):
        self.user = user
        self.amount = amount
        self.from_wallet = from_wallet
        # self.game_func_options = {'eaDeposit': self.eaDeposit,
        #                           'onebookWithdraw': self.onebookWithdraw,
        #                          }

    def eaDeposit(self):
        return requestEADeposit(self.user, self.amount, self.from_wallet)

    def onebookDeposit(self):
        return fundTransfer(self.user, self.amount, self.from_wallet, 1, 1)

    def kaiyuanDeposit(self):
        return kaiyuanDeposit()

    
class TransferWithdraw():

    def __init__(self, user, amount, to_wallet):
        self.user = user
        self.amount = amount
        self.to_wallet = to_wallet
        # self.game_func_options = {'eaWithdraw': self.eaWithdraw,
        #                           'onebookWithdraw': self.onebookWithdraw,

        #                          }

    def eaWithdraw(self):
        return requestEAWithdraw(self.user, self.amount, self.to_wallet)

    def onebookWithdraw(self):
        return fundTransfer(self.user, self.amount, self.to_wallet, 0, 1)

