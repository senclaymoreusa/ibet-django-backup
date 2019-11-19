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
MARKET_CN = 2

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
        
        txn_id = generateTxnId("BTi")
        user = findUser(username)
        # user found -> record reserve
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
                        market=MARKET_CN,
                        other_data={'is_reserve': True, 'bets_info': bet_xml.attrib, 'all_bet_info': [bet.attrib for bet in bet_xml.getchildren()]}
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
        bet = xmlData[0]

        txn_id = generateTxnId("BTi")
        try:
            user = findUser(username)
            prev_bet = GameBet.objects.get(ref_no=reserve_id, other_data__is_reserve=True)
        except ObjectDoesNotExist as e:
            # if prev reserve not found (the initial Reserve call) then throw error
            res = "error_code=-20\r\n"
            res += "error_message=ReserveNotFound\r\n"
            res += f"balance={user.main_wallet}\r\n"
            res += f"trx_id={txn_id}\r\n"
            return HttpResponse(res, content_type='text/plain')

        try:
            if amount > prev_bet.amount_wagered:
                res = "error_code=-21\r\n"
                res += "error_message=TotalReserveAmountExceeded\r\n"
                res += f"balance={user.main_wallet}\r\n"
                res += f"trx_id={txn_id}\r\n"
                return HttpResponse(res, content_type='text/plain')

            bet = GameBet(
                provider=PROVIDER,
                category=CATEGORY,
                user=user,
                ref_no=reserve_id,
                amount_wagered=amount,
                # transaction_id=txn_id,
                market=MARKET_CN,
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
        
        txn_id = generateTxnId("BTi")
        try:
            user = findUser(username)
            totalReserve = GameBet.objects.get(ref_no=reserve_id, other_data__is_reserve=True)

        except ObjectDoesNotExist as e:
            res = "error_code=-20\r\n"
            res += "error_message=ReserveNotFound\r\n"
            res += f"balance={user.main_wallet}\r\n"
            res += f"trx_id={txn_id}\r\n"
            return HttpResponse(res, content_type='text/plain')

        # find debitReserves
        corresponding_reserves = GameBet.objects.filter(ref_no=reserve_id, other_data__has_key='bet_data').order_by('-created_time')
        # no debitReserves
        if not len(corresponding_reserves):
            res = "error_code=-20\r\n"
            res += "error_message=ReserveNotFound\r\n"
            res += f"balance={user.main_wallet}\r\n"
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
                        market=MARKET_CN,
                        # transaction_id=txn_id,
                        other_data={'is_committed': True}
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
            res += f"trx_id={txn_id}\r\n"
            return HttpResponse(res, content_type='text/plain')

        except (DatabaseError, IntegrityError, Exception) as e:
            logger.error(repr(e))
            res = "error_code=160\r\n"
            res += "error_message=SeamlessError160\r\n"
            res += f"balance={user.main_wallet}\r\n"
            res += f"trx_id={txn_id}\r\n"
            return HttpResponse(res, content_type='text/plain')


# should generate success even if reserve is not found
class CancelReserve(View):
    def get(self, request):
        VOID_OUTCOME=3
        username = request.GET.get("cust_id")
        bet_id = request.GET.get("reserve_id")
        try:
            with transaction.atomic():
                user = findUser(username)                
                prev_bet = GameBet.objects.filter(ref_no=bet_id)

                # bet has already been debited
                if prev_bet.count() > 1: 
                    res = "error_code=-190\r\n"
                    res += "error_message=SeamlessError190\r\n"
                    res += f"balance={user.main_wallet}\r\n"
                    return HttpResponse(res, content_type='text/plain')
                
                # no Reserve was made, but cancel called anyways
                if prev_bet.count() == 0:
                    credit_amount = decimal.Decimal(0)
                    bet = GameBet(
                        ref_no=bet_id,
                        amount_won=credit_amount,
                        outcome=VOID_OUTCOME,
                        provider=PROVIDER,
                        category=CATEGORY,
                        resolved_time=timezone.now(),
                        other_data={'is_cancel': True}
                    )

                    bet.save()
                    res = "error_code=0\r\n"
                    res += "error_message=ReserveNotFound\r\n"
                    res += f"balance={user.main_wallet}\r\n"
                    return HttpResponse(res, content_type='text/plain')
                
                # expected case, only Reserve was called -> okay to cancel
                if prev_bet.count() == 1:
                    credit_amount = prev_bet[0].amount_wagered
                    bet = GameBet(
                        ref_no=bet_id,
                        amount_won=credit_amount,
                        outcome=VOID_OUTCOME,
                        provider=PROVIDER,
                        category=CATEGORY,
                        resolved_time=timezone.now(),
                        other_data={'is_cancel': True}
                    )
                    
                    new_balance = user.main_wallet + credit_amount
                    user.main_wallet = new_balance
                    user.save()
                    bet.save()

                    res = "error_code=0\r\n"
                    res += "error_message=success\r\n"
                    res += f"balance={user.main_wallet}\r\n"
                    return HttpResponse(res, content_type='text/plain')
            
        except (DatabaseError, IntegrityError, Exception) as e:
            logger.error(repr(e))
            res = "error_code=-170\r\n"
            res += "error_message=SeamlessError170\r\n"
            res += f"balance={user.main_wallet}\r\n"
            return HttpResponse(res, content_type='text/plain')
            
class Add2Bet(View):
    def post(self, request):
        username = request.GET.get("cust_id")
        reserve_id = request.GET.get("reserve_id")
        amount = request.GET.get("amount")
        txn_id = generateTxnId("BTi")
        
        xmlData = etree.fromstring(request.body)
        bet = xmlData[0]
        try:
            with transaction.atomic():
                user = findUser(username)
                open_bet = GameBet.objects.get(ref_no=reserve_id, other_data__is_reserve=True)
                new_bet = Bet(
                    provider=PROVIDER,
                    category=CATEGORY,
                    user=user,
                    ref_no=reserve_id,
                    amount_wagered=amount,
                    # transaction_id=txn_id,
                    market=MARKET_CN,
                    other_data=dict({'is_add2bet': True, 'bet_data': bet.attrib, 'line_data': [line.attrib for line in bet.getchildren()] })
                )
                user.main_wallet = user.main_wallet - amount
                user.save()
                new_bet.save()

                res = "error_code=0\r\n"
                res += "error_message=success\r\n"
                res += f"balance={user.main_wallet}\r\n"
                res += f"trx_id={txn_id}\r\n"
                return HttpResponse(res, content_type='text/plain')

        except (DatabaseError, IntegrityError, Exception) as e:
            logger.error("Add2Bet::Error Occured::" + repr(e))
            res = "error_code=-1\r\n"
            res += "error_message=GeneralError\r\n"
            res += f"balance={user.main_wallet}\r\n"
            res += f"trx_id={txn_id}\r\n"
            return HttpResponse(res, content_type='text/plain')


class Add2BetConfirm(View):
    def post(self, request):
        username = request.GET.get("cust_id")
        reserve_id = request.GET.get("reserve_id")
        amount = request.GET.get("amount")
        txn_id = generateTxnId("BTi")
        xmlData = etree.fromstring(request.body)
        bet = xmlData[0]
        try:
            user = findUser(username)
            bet_to_confirm = GameBet.objects.get(ref_no=reserve_id, other_data__is_add2bet=True)
            confirm_bet = Bet(
                provider=PROVIDER,
                category=CATEGORY,
                user=user,
                ref_no=reserve_id,
                amount_wagered=bet_to_confirm.amount_wagered,
                # transaction_id=txn_id,
                market=MARKET_CN,
                other_data=dict({'add2bet_confirm': True, 'updated_bet_data': bet.attrib, 'line_data': [line.attrib for line in bet.getchildren()] })
            )
            confirm_bet.save()

            res = "error_code=0\r\n"
            res += "error_message=success\r\n"
            res += f"trx_id={txn_id}\r\n"
            res += f"balance={user.main_wallet}\r\n"
            return HttpResponse(res, content_type='text/plain')

        except (DatabaseError, IntegrityError, Exception) as e:
            logger.error("Add2BetConfirm::Error Occured::" + repr(e))
            res = "error_code=0\r\n"
            res += "error_message=success\r\n"
            res += f"trx_id={txn_id}\r\n"
            res += f"balance={user.main_wallet}\r\n"
            return HttpResponse(res, content_type='text/plain')

class DebitCustomer(View):
    def post(self, request):
        username = request.GET.get("cust_id")
        reserve_id = request.GET.get("reserve_id")
        amount = request.GET.get("amount")
        txn_id = generateTxnId("BTi")
        
        xmlData = etree.fromstring(request.body)
        purchases = xmlData[0]
        try:
            with transaction.atomic():
                user = findUser(username)    
                resolvedBet = Bet(
                    provider=PROVIDER,
                    category=CATEGORY,
                    user=user,
                    ref_no=reserve_id,
                    amount_wagered=bet_to_confirm.amount_wagered,
                    # transaction_id=txn_id,
                    market=MARKET_CN,
                    resolved_time=timezone.now(),
                    other_data=dict({
                        'debit_data': xmlData.attrib, 
                        'purchase_data': {
                            'purchase': purchases.getchildren()[0],
                        }, 
                        'raw_xml': str(request.body, 'utf-8')
                    })
                )

        except (DatabaseError, IntegrityError, Exception) as e:
            logger.error("DebitCustomer::Error Occured::" + repr(e))
            return

def findUser(username): # should only throw error in the Reserve call, if it is called in any other reserve function, it should return the user
    try: # try to find user
        user = CustomUser.objects.get(username=username)
        return user
    except ObjectDoesNotExist as e:
        res = "error_code=-2\r\n"
        res += "error_message=CustomerNotFound\r\n"
        res += f"balance={user.main_wallet}\r\n"
        res += f"trx_id={txn_id}\r\n"
        res += f"BonusUsed=0.00\r\n"
        return HttpResponse(res, content_type='text/plain')