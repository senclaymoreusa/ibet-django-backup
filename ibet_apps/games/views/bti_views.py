import datetime
import decimal
import hashlib 
import logging
import requests
import random
import simplejson as json
import uuid

from django.views import View
from django.db import DatabaseError, IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from rest_framework.authtoken.models import Token
from lxml import etree

from users.views.helper import checkUserBlock
from users.models import CustomUser
from games.models import *
from accounting.models import *

from utils.constants import *


logger = logging.getLogger('django')


class ValidateToken(View):
    def get(self, request):
        token = request.GET.get("auth_token")
        try:
            userFromToken = (Token.objects.select_related('user').get(token=token)).user
            res = "error_code=0\r\n" # 0 = success
            res += "error_message=success\r\n"
            res += f"cust_id={userFromToken.username}\r\n"
            res += f"balance={str('%.2f' % userFromToken.main_wallet)}\r\n"
            res += "cust_login=orion\r\n"
            res += "city=Sunnyvale\r\n"
            res += "country=USA\r\n"
            res += "currency_code=CNY\r\n"
            return HttpResponse(res, content_type='text/plain')
        except ObjectDoesNotExist as e:
            logger.error(repr(e))
            res = "error_code=-2\r\n"
            res += "error_message=Token not found\r\n"
            res += "cust_id=123456789\r\n"
            res += "balance=999999.99\r\n"
            res += "cust_login=orion\r\n"
            res += "city=Sunnyvale\r\n"
            res += "country=USA\r\n"
            res += "currency_code=CNY\r\n"
            return HttpResponse(res, content_type='text/plain')


class Reserve(View):
    def post(self, request):
        username = request.GET.get("cust_id")
        bet_id = request.GET.get("reserve_id")
        amount = decimal.Decimal(request.GET.get("amount"))
        # txn_id = generateTxnId()
        txn_id = "12345asdf"
        try:
            with transaction.atomic():
                user = CustomUser.objects.get(username=username)
                if amount < user.main_wallet:
                    new_balance = user.main_wallet - amount
                    user.main_wallet = new_balance

                    bet = GameBet(
                        user=user,
                        ref_no=bet_id,
                        amount_wagered=amount,
                        # transaction_id=generateUID,
                        # provider=PROVIDER,
                        # category=CATEGORY,
                    )
                    bet.save()
                    user.save()
                else:
                    raise Exception
            res = "error_code=0\r\n"
            res += "error_message=success\r\n"
            res += f"balance={new_balance}\r\n"
            res += f"trx_id={txn_id}\r\n"
            res += f"BonusUsed=0.00\rn"
            return HttpResponse(res, content_type='text/plain')
        except (ObjectDoesNotExist, DatabaseError, IntegrityError, Exception) as e:
            res = "error_code=-4\r\n"
            res += "error_message=InsufficientFunds\r\n"
            res += f"balance={new_balance}\r\n"
            res += f"trx_id={txn_id}\r\n"
            res += f"BonusUsed=0.00\r\n"
            return HttpResponse(res, content_type='text/plain')
                

class DebitReserve(View):
    def post(self, request):
        username = request.GET.get("cust_id")
        bet_id = request.GET.get("reserve_id")
        amount = decimal.Decimal(request.GET.get("amount"))
        req_id = request.GET.get("debit_reserve")
        xmlData = etree.fromstring(request.body)
        
        txn_id = "12345asdf" #TODO: change this to be variable
        try:
            with transaction.atomic():
                user = CustomUser.objects.get(username=username)

            res = "error_code=0\r\n"
            res += "error_message=success\r\n"
            res += f"trx_id={txn_id}\r\n"
            res += f"balance={user.main_wallet}\r\n" #TODO: remove hard coded balance

            return HttpResponse(res, content_type='text/plain')
        except (ObjectDoesNotExist, DatabaseError, IntegrityError, Exception) as e:
            res = "error_code=-4\r\n"
            res += "error_message=InsufficientFunds\r\n"
            res += f"trx_id={txn_id}\r\n"
            res += f"balance={user.main_wallet}\r\n"
            return HttpResponse(res, content_type='text/plain')

class CommitReserve(View):
    def get(self, request):
        return HttpResponse("Test test test")
    def post(self, request):
        return HttpResponse("Post Commit Reserve")

class CancelReserve(View):
    def get(self, request):
        username = request.GET.get("cust_id")
        bet_id = request.GET.get("reserve_id")
        try:
            with transaction.atomic():
                user = CustomUser.objects.get(username=username)

                try:
                    prev_bet = GameBet.objects.get(ref_no=bet_id)
                except ObjectDoesNotExist as e:
                    bet = GameBet(
                        ref_no=bet_id,
                        amount_won=decimal.Decimal(0),
                        outcome=3
                        # provider=PROVIDER,
                        # category=CATEGORY,
                    )
                    
                bet = GameBet(
                    ref_no=bet_id,
                    amount_won=prev_bet.amount_wagered,
                    # provider=PROVIDER,
                    # category=CATEGORY,
                )
                new_balance = user.main_wallet + prev_bet.amount_wagered
                user.main_wallet = new_balance
                user.save()
                bet.save()
                
            res = "error_code=-4\r\n"
            res += "error_message=success\r\n"
            # res += f"balance={user.main_wallet}\r\n"
            res += f"balance=100\r\n"
            return HttpResponse(res, content_type='text/plain')
        except (ObjectDoesNotExist, DatabaseError, IntegrityError, Exception) as e:
            logger.error(repr(e))
            res = "error_code=-4\r\n"
            res += "error_message=success\r\n"
            # res += f"balance={user.main_wallet}\r\n"
            res += f"balance=100\r\n"
            return HttpResponse(res, content_type='text/plain')
            
        return HttpResponse("Test test test")
