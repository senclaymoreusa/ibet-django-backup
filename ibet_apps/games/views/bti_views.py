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
from games.helper import *
from utils.constants import *


logger = logging.getLogger('django')
PROVIDER = GameProvider.objects.get(provider_name='BTi')
CATEGORY = Category.objects.get(name='Sportsbook')

# check if token exists for logged in user
class ValidateToken(View):
    def get(self, request):
        token = request.GET.get("auth_token")
        try:
            userFromToken = (Token.objects.select_related('user').get(token=token)).user
            userFromToken.country
            res = "error_code=0\r\n" # 0 = success
            res += "error_message=success\r\n"
            res += f"cust_id={userFromToken.username}\r\n"
            res += f"balance={str('%.2f' % userFromToken.main_wallet)}\r\n"
            res += "cust_login=orion\r\n"
            res += "city=Sunnyvale\r\n"
            res += "country=CN\r\n"
            res += "currency_code=CNY\r\n"
            return HttpResponse(res, content_type='text/plain')
        except ObjectDoesNotExist as e:
            logger.error(repr(e))
            res = "error_code=-2\r\n"
            res += "error_message=Token not found\r\n"
            res += "cust_id=99999999\r\n"
            res += "balance=0.00\r\n"
            res += "cust_login=unknown_user\r\n"
            res += "city=nowhere\r\n"
            res += "country=CN\r\n"
            res += "currency_code=CNY\r\n"
            return HttpResponse(res, content_type='text/plain')

# set aside player balance to make bets with
class Reserve(View):
    def post(self, request):
        username = request.GET.get("cust_id")
        reserve_id = request.GET.get("reserve_id")
        amount = decimal.Decimal(request.GET.get("amount"))
        bet_xml = etree.fromstring(request.body)
        print(username,reserve_id,amount)
        txn_id = generateTxnId("BTi")
        user = findUser(username)
        # user found, record reserve
        try:
            with transaction.atomic():
                if amount < user.main_wallet:
                    ending_balance = user.main_wallet - amount
                    bet = GameBet(
                        provider=PROVIDER,
                        category=CATEGORY,
                        username=user,
                        ref_no=reserve_id,
                        amount_wagered=amount,
                        # transaction_id=txn_id,
                        market=0,
                        other_data={'is_reserve': True}
                    )
                    user.main_wallet = ending_balance
                    bet.save()
                    user.save()
                else:
                    res = "error_code=-4\r\n"
                    res += "error_message=InsufficientFunds\r\n"
                    res += f"balance={ending_balance}\r\n"
                    res += f"trx_id={txn_id}\r\n"
                    res += f"BonusUsed=0.00\r\n"
                    return HttpResponse(res, content_type='text/plain')
            print("success")
            res = "error_code=0\r\n"
            res += "error_message=success\r\n"
            res += f"balance={ending_balance}\r\n"
            res += f"trx_id={txn_id}\r\n"
            res += f"BonusUsed=0.00\rn"
            return HttpResponse(res, content_type='text/plain')

        except (DatabaseError, IntegrityError) as e:
            logger.error(repr(e))
            res = "error_code=-160\r\n"
            res += "error_message=SeamlessError160\r\n"
            res += f"balance={ending_balance}\r\n"
            res += f"trx_id={txn_id}\r\n"
            res += f"BonusUsed=0.00\r\n"
            return HttpResponse(res, content_type='text/plain')
                

# endpoint is called for every bet made in Reserve
class DebitReserve(View):
    def post(self, request):
        username = request.GET.get("cust_id")
        reserve_id = request.GET.get("reserve_id")  # the reserve id that this debit corresponds to
        amount = decimal.Decimal(request.GET.get("amount"))
        req_id = request.GET.get("req_id") # unique req id on the URL, different than bet ID

        xmlData = etree.fromstring(request.body)
        
        txn_id = generateTxnId("BTi")
        bet_id = xmlData[0].attrib['BetID']

        try:
            prev_bet = GameBet.objects.get(ref_no=reserve_id, other_data__is_reserve=True)
        except ObjectDoesNotExist as e:
            # if prev reserve not found (the initial Reserve call) then throw error
            res = "error_code=-20\r\n"
            res += "error_message=ReserveNotFound\r\n"
            res += f"balance=0.00\r\n"
            res += f"trx_id={txn_id}\r\n"
            res += f"BonusUsed=0.00\r\n"
            return HttpResponse(res, content_type='text/plain')

        try:
            user = findUser(username)
            bet = GameBet(
                provider=PROVIDER,
                category=CATEGORY,
                user=user,
                ref_no=reserve_id,
                amount_wagered=amount,
                # transaction_id=txn_id,
                market=0,
                other_data=dict({'bet_data': bet.attrib, 'line_data': [line.attrib for line in bet.getchildren()] })
            )
            bet.save()
            res = "error_code=0\r\n"
            res += "error_message=success\r\n"
            res += f"trx_id={txn_id}\r\n"
            res += f"balance={user.main_wallet}\r\n"
            return HttpResponse(res, content_type='text/plain')

        except (DatabaseError, IntegrityError, Exception) as e:
            logger.error(repr(e))
            res = "error_code=160\r\n"
            res += "error_message=SeamlessError160\r\n"
            res += f"trx_id={txn_id}\r\n"
            res += f"balance={user.main_wallet}\r\n"
            return HttpResponse(res, content_type='text/plain')

class CommitReserve(View):
    def get(self, request):
        username = request.GET.get("cust_id")
        reserve_id = request.GET.get("reserve_id")  # the reserve id that this debit corresponds to
        
        user = findUser(username)
        try:
            totalReserve = GameBet.objects.get(ref_no=reserve_id, other_data__is_reserve=True)

        except ObjectDoesNotExist as e:
            res = "error_code=-20\r\n"
            res += "error_message=ReserveNotFound\r\n"
            res += f"balance=0.00\r\n"
            res += f"trx_id={txn_id}\r\n"
            return HttpResponse(res, content_type='text/plain')

        # find debitReserves
        corresponding_reserves = GameBet.objects.filter(ref_no=reserve_id, other_data__has_key='bet_data').order_by('-created_time')
        # no debitReserves
        if not len(corresponding_reserves):
            res = "error_code=-20\r\n"
            res += "error_message=ReserveNotFound\r\n"
            res += f"balance=0.00\r\n"
            res += f"trx_id={txn_id}\r\n"
            return HttpResponse(res, content_type='text/plain')

        try:
            with transaction.atomic():
                bet = GameBet(
                        provider=PROVIDER,
                        category=CATEGORY,
                        username=user,
                        ref_no=reserve_id,
                        amount_wagered=amount,
                        market=0,
                        other_data={'commit_reserve': True}
                    )
                totalReserveAmount = totalReserve.amount_wagered
                actualTotal = 0
                for bet in corresponding_reserves:
                    actualTotal += bet.amount_wagered
                
                refundAmount = totalReserveAmount - actualTotal
                user.main_wallet += refundAmount
                bet.save()
                user.save()

            res = "error_code=0\r\n"
            res += "error_message=success\r\n"
            res += f"balance={user.main_wallet}\r\n"
            return HttpResponse(res, content_type='text/plain')

        except (DatabaseError, IntegrityError, Exception) as e:
            logger.error(repr(e))
            res = "error_code=160\r\n"
            res += "error_message=SeamlessError160\r\n"
            res += f"balance={user.main_wallet}\r\n"
            return HttpResponse(res, content_type='text/plain')


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
            res += f"balance={user.main_wallet}\r\n"
            # res += f"balance=100\r\n"
            return HttpResponse(res, content_type='text/plain')
            



def findUser(username): # should only throw error in the Reserve call, if it is called in any other reserve function, it should return the user
    try: # try to find user
        user = CustomUser.objects.get(username=username)
        return user
    except ObjectDoesNotExist as e:
        res = "error_code=-2\r\n"
        res += "error_message=CustomerNotFound\r\n"
        res += f"balance=0.00\r\n"
        res += f"trx_id={txn_id}\r\n"
        res += f"BonusUsed=0.00\r\n"
        return HttpResponse(res, content_type='text/plain')