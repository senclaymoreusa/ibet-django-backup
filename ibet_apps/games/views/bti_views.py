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
from django.db.models import Q, Sum

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

MARKET_CN = 2
logger = logging.getLogger('django')


# check if token exists for logged in user
class ValidateToken(View):
    def get(self, request):
        token = request.GET.get("auth_token")
        if not token:
            return wrongRequest()
        try:
            userFromToken = (Token.objects.select_related('user').get(key=token)).user
            res = "error_code=0\r\n" # 0 = success
            res += "error_message=success\r\n"
            res += f"cust_id={userFromToken.username}\r\n"
            res += f"balance={str('%.2f' % userFromToken.main_wallet)}\r\n"
            res += f"cust_login={userFromToken}\r\n"
            res += "city=Shenzhen\r\n"
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
        amount = request.GET.get("amount")
        # data validation
        if not (username and reserve_id and amount and request.body):
            return wrongRequest()
        
        amount = decimal.Decimal(amount)
        if amount < 0:
            return wrongRequest()

        user = findUser(username)
        if not (isinstance(user, CustomUser)):
            return user

        bet_xml = etree.fromstring(request.body)
        txn_id = generateTxnId()
        
        prev_bets = GameBet.objects.filter(ref_no=reserve_id, other_data__is_reserve=True)
        if prev_bets.count() == 0:
            try:
                with transaction.atomic():
                    if amount < user.main_wallet:  # user has enough funds
                        PROVIDER, CATEGORY = getProviderCategory()
                        ending_balance = user.main_wallet - amount
                        bet = GameBet(
                            provider=PROVIDER,
                            category=CATEGORY,
                            user=user,
                            ref_no=reserve_id,
                            amount_wagered=amount,
                            user_name=user.username,
                            transaction_id=txn_id,
                            market=MARKET_CN,
                            other_data={
                                'is_reserve': True, 
                                'bets_info': dict(bet_xml.attrib), 
                                'all_bet_info': [dict(bet.attrib) for bet in bet_xml.getchildren()],
                                'ending_balance': float(ending_balance),
                                'txn_no': txn_id
                            }
                        )
                        user.main_wallet = ending_balance
                        bet.save()
                        user.save()

                        res = "error_code=0\r\n"
                        res += "error_message=success\r\n"
                        res += f"balance={ending_balance}\r\n"
                        # res += f"balance={ending_balance.quantize(Decimal('1.00'))}\r\n"
                        res += f"trx_id={txn_id}\r\n"
                        res += f"BonusUsed=0.00\r\n"
                        return HttpResponse(res, content_type='text/plain')

                    res = "error_code=-4\r\n"
                    res += "error_message=InsufficientFunds\r\n"
                    res += f"balance={user.main_wallet}\r\n"
                    res += f"trx_id={txn_id}\r\n"
                    res += f"BonusUsed=0.00\r\n"
                    return HttpResponse(res, content_type='text/plain')
            except (DatabaseError, IntegrityError) as e:
                logger.error(repr(e))
                res = "error_code=-160\r\n"
                res += "error_message=SeamlessError160\r\n"
                res += f"balance={ending_balance}\r\n"
                res += f"trx_id={txn_id}\r\n"
                res += f"BonusUsed=0.00\r\n"
                return HttpResponse(res, content_type='text/plain')
        
        # call with same reserve_id was made
        res = "error_code=0\r\n"
        res += "error_message=success\r\n"
        res += f"balance={prev_bets[0].other_data['ending_balance']}\r\n"
        res += f"trx_id={prev_bets[0].other_data['txn_no']}\r\n"
        res += f"BonusUsed=0.00\r\n"
        return HttpResponse(res, content_type='text/plain')

# endpoint is called for every bet made in Reserve
class DebitReserve(View):
    def post(self, request):
        username = request.GET.get("cust_id")
        reserve_id = request.GET.get("reserve_id")  # the reserve id that this debit corresponds to
        amount = request.GET.get("amount")
        req_id = request.GET.get("req_id") # unique req id on the URL, different than bet ID

        if not (username and reserve_id and amount and req_id and request.body):
            return wrongRequest()

        amount = decimal.Decimal(amount)
        if amount < 0:
            return wrongRequest()

        user = findUser(username)
        if not (isinstance(user, CustomUser)):
            return user

        bet_xml = etree.fromstring(request.body)
        bet = bet_xml[0]

        txn_id = generateTxnId()
        
        try:
            initial_reserve = GameBet.objects.get(ref_no=reserve_id, other_data__is_reserve=True)
        except ObjectDoesNotExist as e:  # throw error if matching Reserve call not found
            res = "error_code=-20\r\n"
            res += "error_message=ReserveNotFound\r\n"
            res += f"balance={user.main_wallet}\r\n"
            res += f"trx_id={txn_id}\r\n"
            return HttpResponse(res, content_type='text/plain')

        # reserve was already canceled
        try:
            transaction_canceled = GameBet.objects.get(ref_no=reserve_id, other_data__is_cancel=True)
            res = "error_code=-22\r\n"
            res += "error_message=ReserveClosed\r\n"
            return HttpResponse(res, content_type='text/plain')
        except ObjectDoesNotExist as e:
            pass
        
        # reserve was already committed
        try:
            transaction_committed = GameBet.objects.get(ref_no=reserve_id, other_data__is_committed=True)
            res = "error_code=-22\r\n"
            res += "error_message=ReserveClosed\r\n"
            return HttpResponse(res, content_type='text/plain')
        except ObjectDoesNotExist as e:
            pass

        # handle repeat request
        try:
            repeat_transaction = GameBet.objects.get(ref_no=reserve_id, other_data__request_id=req_id)
            res = "error_code=0\r\n"
            res += "error_message=success\r\n"
            res += f"trx_id={repeat_transaction.transaction_id}\r\n"
            res += f"balance={repeat_transaction.other_data['ending_balance']}\r\n"
            return HttpResponse(res, content_type='text/plain')
        except ObjectDoesNotExist as e:
            pass
        
        # check if reserve amount is exceeded
        all_debits = GameBet.objects.filter(ref_no=reserve_id, other_data__is_debit=True)
        running_sum = all_debits.aggregate(Sum('amount_wagered'))['amount_wagered__sum'] or 0

        if amount + running_sum > initial_reserve.amount_wagered:
            res = "error_code=-21\r\n"
            res += "error_message=TotalReserveAmountExceeded\r\n"
            return HttpResponse(res, content_type='text/plain')
            
        game_name = ""
        odds = int(bet.attrib.get("Odds"))
        if not b.getchildren(): # no lines
            game_name = bet.attrib.get("EventName")
        else:
            game_name = ""
            lines = bet.getchildren()
            for line in lines:
                game_name += line.attrib.get("EventName") or line.attrib.get("LeagueName")
        try:
            PROVIDER, CATEGORY = getProviderCategory()
            bet = GameBet(
                provider=PROVIDER,
                category=CATEGORY,
                user=user,
                user_name=user.username,
                ref_no=reserve_id,
                amount_wagered=amount,
                transaction_id=txn_id,
                market=MARKET_CN,
                odds=odds,
                game_name=bet.attrib.get("EventName"),
                other_data={
                    'bet_data': dict(bet.attrib), 
                    'line_data': [dict(line.attrib) for line in bet.getchildren()],
                    'ending_balance': float(initial_reserve.other_data["ending_balance"]),
                    'request_id': req_id,
                    'is_debit': True
                }
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

        if not (username and reserve_id):
            return wrongRequest()

        user = findUser(username)
        if not (isinstance(user, CustomUser)):
            return user

        txn_id = generateTxnId()
        # find reserve
        try:
            totalReserve = GameBet.objects.get(ref_no=reserve_id, other_data__is_reserve=True)
        except ObjectDoesNotExist as e:
            res = "error_code=-20\r\n"
            res += "error_message=ReserveNotFound\r\n"
            res += f"balance={user.main_wallet}\r\n"
            res += f"trx_id={txn_id}\r\n"
            return HttpResponse(res, content_type='text/plain')

        # handle repeat request
        try:
            duplicate = GameBet.objects.get(ref_no=reserve_id, other_data__is_committed=True)
            res = "error_code=0\r\n"
            res += "error_message=success\r\n"
            res += f"balance={duplicate.other_data['ending_balance']}\r\n"
            res += f"trx_id={duplicate.transaction_id}\r\n"
            return HttpResponse(res, content_type='text/plain')
        except ObjectDoesNotExist:
            pass

        # find debitReserves
        corresponding_reserves = GameBet.objects.filter(ref_no=reserve_id, other_data__is_debit=True).order_by('-bet_time')

        # no debitReserves
        if not corresponding_reserves:
            res = "error_code=-20\r\n"
            res += "error_message=ReserveNotFound\r\n"
            res += f"balance={user.main_wallet}\r\n"
            res += f"trx_id={txn_id}\r\n"
            return HttpResponse(res, content_type='text/plain')
        
        try:
            with transaction.atomic():
                totalReserveAmount = totalReserve.amount_wagered
                actualTotal = sum([bet.amount_wagered for bet in corresponding_reserves])
                
                refundAmount = totalReserveAmount - actualTotal
                user.main_wallet += refundAmount
                PROVIDER, CATEGORY = getProviderCategory()
                bet = GameBet(
                        provider=PROVIDER,
                        category=CATEGORY,
                        user=user,
                        user_name=user.username,
                        ref_no=reserve_id,
                        amount_wagered=actualTotal,
                        market=MARKET_CN,
                        transaction_id=txn_id,
                        other_data={
                            'is_committed': True,
                            'ending_balance': float(user.main_wallet)
                        }
                    )

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
        reserve_id = request.GET.get("reserve_id")

        if not (username and reserve_id):
            return wrongRequest()

        user = findUser(username)
        if (not isinstance(user, CustomUser)):
            return user
        
        try:
            with transaction.atomic():
                # check for repeat call
                try:
                    already_canceled = GameBet.objects.get(ref_no=reserve_id, other_data__is_cancel=True)
                    res = "error_code=0\r\n"
                    res += "error_message=success\r\n"
                    res += f"balance={already_canceled.other_data['ending_balance']}\r\n"
                    return HttpResponse(res, content_type='text/plain')
                except ObjectDoesNotExist:
                    pass

                prev_bet = GameBet.objects.filter(ref_no=reserve_id)
                # bet has already been debited
                if prev_bet.count() > 1:
                    prev_debits = prev_bet.objects.filter(other_data__is_debit=True)
                    refund = prev_debits.aggregate(Sum('amount_wagered'))['amount_wagered__sum'] or 0
                    user.main_wallet = user.main_wallet + refund
                    PROVIDER, CATEGORY = getProviderCategory()

                    bet = GameBet(
                        provider=PROVIDER,
                        category=CATEGORY,
                        user=user,
                        user_name=user.username,
                        ref_no=reserve_id,
                        amount_won=refund,
                        market=MARKET_CN,
                        outcome=VOID_OUTCOME,
                        resolved_time=timezone.now(),
                        other_data={
                            'is_cancel': True,
                            'ending_balance': float(user.main_wallet)
                        }
                    )
                    bet.save()
                    user.save()
                    res = "error_code=0\r\n"
                    res += "error_message=RefundDebitedReserve\r\n"
                    res += f"balance={user.main_wallet}\r\n"
                    return HttpResponse(res, content_type='text/plain')
                
                # no Reserve was made, but cancel called anyways
                if prev_bet.count() == 0:
                    credit_amount = decimal.Decimal(0)
                    PROVIDER, CATEGORY = getProviderCategory()

                    bet = GameBet(
                        provider=PROVIDER,
                        category=CATEGORY,
                        user=user,
                        user_name=user.username,
                        ref_no=reserve_id,
                        amount_won=credit_amount,
                        market=MARKET_CN,
                        outcome=VOID_OUTCOME,
                        resolved_time=timezone.now(),
                        other_data={
                            'is_cancel': True,
                            'ending_balance': float(user.main_wallet)
                        }
                    )

                    bet.save()
                    res = "error_code=0\r\n"
                    res += "error_message=ReserveNotFound\r\n"
                    res += f"balance={user.main_wallet}\r\n"
                    return HttpResponse(res, content_type='text/plain')
                
                # expected case, only Reserve was called -> okay to cancel
                if prev_bet.count() == 1:
                    credit_amount = prev_bet[0].amount_wagered
                    new_balance = user.main_wallet + credit_amount
                    user.main_wallet = new_balance
                    PROVIDER, CATEGORY = getProviderCategory()

                    bet = GameBet(
                        provider=PROVIDER,
                        category=CATEGORY,
                        user=user,
                        user_name=user.username,
                        ref_no=reserve_id,
                        amount_won=credit_amount,
                        market=MARKET_CN,
                        outcome=VOID_OUTCOME,
                        resolved_time=timezone.now(),
                        other_data={
                            'is_cancel': True,
                            'ending_balance': float(user.main_wallet)
                        }
                    )
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
        txn_id = generateTxnId()


        if not (username and reserve_id and amount and request.body):
            return wrongRequest()

        amount = decimal.Decimal(amount)
        if amount < 0:
            return wrongRequest()

        bet_xml = etree.fromstring(request.body)
        bet = bet_xml[0]
        try:
            with transaction.atomic():
                user = findUser(username)
                if not (isinstance(user, CustomUser)):
                    return user
                open_bet = GameBet.objects.get(ref_no=reserve_id, other_data__is_reserve=True, other_data__is_committed__isnull=True, other_data__is_cancel__isnull=True)
                PROVIDER, CATEGORY = getProviderCategory()

                new_bet = GameBet(
                    provider=PROVIDER,
                    category=CATEGORY,
                    user=user,
                    user_name=user.username,
                    ref_no=reserve_id,
                    amount_wagered=amount,
                    transaction_id=txn_id,
                    market=MARKET_CN,
                    other_data=dict({'is_add2bet': True, 'bet_data': dict(bet.attrib), 'line_data': [dict(line.attrib) for line in bet.getchildren()] })
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

        if not (username and reserve_id and amount and request.body):
            return wrongRequest()

        amount = decimal.Decimal(amount)
        if amount < 0:
            return wrongRequest()

        user = findUser(username)
        if not (isinstance(user, CustomUser)):
            return user

        txn_id = generateTxnId()
        bet_xml = etree.fromstring(request.body)
        bet = bet_xml[0]
        
        try:
            bet_to_confirm = GameBet.objects.get(ref_no=reserve_id, other_data__is_add2bet=True)
            PROVIDER, CATEGORY = getProviderCategory()

            confirm_bet = GameBet(
                provider=PROVIDER,
                category=CATEGORY,
                user=user,
                user_name=user.username,
                ref_no=reserve_id,
                amount_wagered=bet_to_confirm.amount_wagered,
                transaction_id=txn_id,
                currency=user.get_currency_display(),
                market=MARKET_CN,
                other_data={
                    'is_add2bet_confirm': True, 
                    'updated_bet_data': dict(bet.attrib), 
                    'line_data': [dict(line.attrib) for line in bet.getchildren()] 
                }
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
        request_id = request.GET.get("req_id")
        amount = request.GET.get("amount")
        txn_id = generateTxnId()
        
        if not (username and request_id and amount and request.body):
            logger.error(f"Debit Customer sent incorrect request params;\ncust_id={username}, request_id={req_id}, amount={amount}")
            res = "error_code=0\r\n"
            res += "error_message=MissingParameters\r\n"
            return HttpResponse(res, content_type='text/plain')
        
        amount = decimal.Decimal(amount)
        if amount < 0:
            logger.error(f"Debit Customer sent a negative amount; amount={amount}")
            res = "error_code=0\r\n"
            res += "error_message=NegativeAmount\r\n"
            return HttpResponse(res, content_type='text/plain')

        user = findUser(username)
        if not (isinstance(user, CustomUser)):
            return user
        
        # check for repeat request
        try:
            repeat_debit = GameBet.objects.get(other_data__request_id=request_id, other_data__is_debitcustomer=True)
            res = "error_code=0\r\n"
            res += "error_message=success\r\n"
            res += f"balance={repeat_debit.other_data['ending_balance']}\r\n"
            res += f"trx_id={repeat_debit.other_data['txn_id']}\r\n"
            return HttpResponse(res, content_type='text/plain')
        except ObjectDoesNotExist:
            pass
        
        bet_xml = etree.fromstring(request.body)
        
        purchases = bet_xml[0]
        purchase = purchases[0]
        reserve_id = purchase.attrib.get('ReserveID')
        purchaseDict = dict()
        for purchase in purchases.getchildren():
            purchaseDict["purchase_id_" + str(purchase.attrib.get("PurchaseID"))] = dict(purchase.attrib)
            selections = purchase[0]
            purchaseDict["purchase_id_" + str(purchase.attrib.get("PurchaseID"))]["selections"] = [
                dict(selection.attrib) for selection in selections.getchildren()
            ]


        try:
            with transaction.atomic():
                PROVIDER, CATEGORY = getProviderCategory()

                user.main_wallet = user.main_wallet - amount
                xmlJson = {
                    'is_debitcustomer': True,
                    'is_outcome_correction': True,
                    'debit_data': dict(bet_xml.attrib), 
                    'bet_data': purchaseDict,
                    'raw_xml': str(request.body, 'utf-8'),
                    'request_id': request_id,
                    'ending_balance': float(user.main_wallet),
                    'txn_id': txn_id
                }
                resolvedBet = GameBet(
                    provider=PROVIDER,
                    category=CATEGORY,
                    user=user,
                    user_name=user.username,
                    ref_no=reserve_id,
                    amount_won=decimal.Decimal(amount) * -1,
                    transaction_id=txn_id,
                    currency=user.currency,
                    market=MARKET_CN,
                    resolved_time=timezone.now(),
                    other_data=xmlJson
                )

                resolvedBet.save()
                user.save()

            res = "error_code=0\r\n"
            res += "error_message=success\r\n"
            res += f"balance={user.main_wallet}\r\n"
            res += f"trx_id={txn_id}\r\n"
            return HttpResponse(res, content_type='text/plain')
        except (DatabaseError, IntegrityError, Exception) as e:
            logger.error("DebitCustomer::Error Occured::" + repr(e))
            return

class CreditCustomer(View):
    def post(self, request):
        username = request.GET.get("cust_id")
        request_id = request.GET.get("req_id")
        amount = request.GET.get("amount")

        if not (username and request_id and amount and request.body):
            logger.error(f"Credit Customer sent incorrect request params;\ncust_id={username}, request_id={req_id}, amount={amount}")
            res = "error_code=0\r\n"
            res += "error_message=MissingParameters\r\n"
            return HttpResponse(res, content_type='text/plain')
        
        amount = decimal.Decimal(amount)
        if amount < 0:
            logger.error(f"Credit Customer sent a negative amount; amount={amount}")
            res = "error_code=0\r\n"
            res += "error_message=NegativeAmount\r\n"
            return HttpResponse(res, content_type='text/plain')
        
        user = findUser(username)
        if not (isinstance(user, CustomUser)):
            return user

        try:
            repeat_credit = GameBet.objects.get(other_data__request_id=request_id, other_data__is_credit=True)
            res = "error_code=0\r\n"
            res += "error_message=success\r\n"
            res += f"balance={repeat_credit.other_data['ending_balance']}\r\n"
            res += f"trx_id={repeat_credit.other_data['txn_id']}\r\n"
            return HttpResponse(res, content_type='text/plain')
        except ObjectDoesNotExist:
            pass

        txn_id = generateTxnId()

        bet_xml = etree.fromstring(request.body)
        purchases = bet_xml[0]
        purchase = purchases[0]
        
        reserve_id = purchase.attrib.get('ReserveID')

        try:
            with transaction.atomic():
                if amount > 0:
                    user.main_wallet = user.main_wallet + amount

                purchaseDict = dict()
                isBetCorrection = False
                for purchase in purchases.getchildren():
                    purchaseDict["purchase_id_" + str(purchase.attrib.get("PurchaseID"))] = dict(purchase.attrib)
                    selections = purchase[0]
                    for selection in selections.getchildren():
                        purchaseDict["purchase_id_" + str(purchase.attrib.get("PurchaseID"))]["selections"] = [
                            dict(selection.attrib)
                        ]
                        changes = selections[0]
                        for change in changes:
                            if "open" not in change.attrib.get("OldStatus").lower():
                                isBetCorrection = True

                PROVIDER, CATEGORY = getProviderCategory()
                
                outcome = 0 if amount > 0 else 1
                
                xmlJson = {
                    'is_credit': True,
                    'is_outcome_correction': isBetCorrection,
                    'credit_data': dict(bet_xml.attrib), 
                    'bet_data': purchaseDict,
                    'raw_xml': str(request.body, 'utf-8'),
                    'request_id': request_id,
                    'ending_balance': float(user.main_wallet),
                    'txn_id': txn_id
                }

                resolvedBet = GameBet(
                    provider=PROVIDER,
                    category=CATEGORY,
                    user=user,
                    user_name=user.username,
                    ref_no=reserve_id,
                    amount_won=amount,
                    transaction_id=txn_id,
                    currency=user.currency,
                    market=MARKET_CN,
                    resolved_time=timezone.now(),
                    other_data=xmlJson
                )
                user.save()
                resolvedBet.save() 

            res = "error_code=0\r\n"
            res += "error_message=success\r\n"
            res += f"balance={user.main_wallet}\r\n"
            res += f"trx_id={txn_id}\r\n"
            return HttpResponse(res, content_type='text/plain')
        except (DatabaseError, IntegrityError, Exception) as e:
            logger.error("CreditCustomer::Error Occured::" + repr(e))


######
# helper functions
#####
def findUser(username): # should only throw error in the Reserve call, if it is called in any other reserve function, it should return the user
    try: # try to find user
        user = CustomUser.objects.get(username=username)
        return user
    except ObjectDoesNotExist as e:
        res = "error_code=-2\r\n"
        res += "error_message=CustomerNotFound\r\n"
        return HttpResponse(res, content_type='text/plain')

def wrongRequest():
    res = "error_code=-10\r\n"
    res += "error_message=WrongRequest\r\n"
    return HttpResponse(res, content_type='text/plain')

def getProviderCategory():
    PROVIDER = None
    CATEGORY = None
    try:
        PROVIDER = GameProvider.objects.get(provider_name=BTI_PROVIDER)
    except ObjectDoesNotExist:
        logger.error("missing bti provider")

    try:
        CATEGORY = Category.objects.get(name='Sports')
    except ObjectDoesNotExist:
        logger.error("missing sport category")
    if PROVIDER and CATEGORY:
        return (PROVIDER, CATEGORY)
    else:
        raise Exception("Provider or category is missing")

###########################################################################################
# begin FE calls
###########################################################################################
class Status(View):
    def post(self, request):
        token = request.POST.get("token")
        try:
            userFromToken = (Token.objects.select_related('user').get(key=token)).user
            return JsonResponse({
                'uid': datetime.datetime.now(),
                'token': token,
                'status': 'real',
                'message': '',
                'balance': str(float(userFromToken.main_wallet)) + " " + userFromToken.get_currency_display()
            })
        except ObjectDoesNotExist:
            return JsonResponse({
                'uid': datetime.datetime.now(),
                'token': token,
                'status': 'anon',
                'message': '',
                'balance': '$0.00'
            })

class Refresh(View):
    def post(self, request):
        token = request.POST.get("token")
        try:
            userFromToken = (Token.objects.select_related('user').get(key=token)).user
            return JsonResponse({
                'status': 'success',
                'message': '',
                'balance': str(float(userFromToken.main_wallet)) + " " + userFromToken.get_currency_display()
            })
        except ObjectDoesNotExist:
            return JsonResponse({
                'status': 'failure',
                'message': '',
                'balance': '$0.00'
            })

# class Login(View):
#     def post(self, request):
#         return JsonResponse({
#             'key': 'testing_key',
#             'balance': 1234.56
#         })
