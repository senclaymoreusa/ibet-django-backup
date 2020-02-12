# Django Rest Framework
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

# Django
from django.views import View
from django.db import transaction, DatabaseError
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

# Local
from users.views.helper import checkUserBlock
from users.models import CustomUser
from utils.constants import *
from games.models import *
from accounting.models import * 

# General
import datetime
import hashlib 
import json
import logging
import random
import requests
import urllib
import xmltodict
from decimal import Decimal
from datetime import date

# from background_task import background
import redis
from utils.redisClient import RedisClient
from utils.redisHelper import RedisHelper


logger = logging.getLogger('django')

def getGPIBalance(user):
    try:
        req_param = {}
        req_param["merch_id"] = GPI_MERCH_ID
        req_param["merch_pwd"] = GPI_MERCH_PWD
        req_param["cust_id"] = user.pk
        # req_param["cust_name"] = user.username
        req_param["currency"] = transCurrency(user)

        req = urllib.parse.urlencode(req_param)

        # url = GPI_URL + 'createuser' + '?' + req
        # res = requests.get(url)

        url = GPI_URL + 'getbalance' + '?' + req
        res = requests.get(url)
        
        res = xmltodict.parse(res.text)

        if res["resp"]["error_code"] == "0":
            logger.info("GPI get balance for user: {}, {}".format(user.username, res["resp"]["balance"]))
            return res["resp"]["balance"]
        else:
            logger.warning("GPI get balance failed: {}".format(res["resp"]["error_code"]))
            return 0
    except Exception as e:
        logger.error("Error: GPI GetBalanceAPI error -- {}".format(repr(e)))
        return 0


def gpiTransfer(user, amount, wallet, method):
    try:
        currency = transCurrency(user)

        trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

        req_param = {}
        req_param["merch_id"] = GPI_MERCH_ID
        req_param["merch_pwd"] = GPI_MERCH_PWD
        req_param["cust_id"] = user.pk
        req_param["currency"] = currency
        req_param["amount"] = amount
        req_param["trx_id"] = trans_id

        req = urllib.parse.urlencode(req_param)

        if method == 1:
            url = GPI_URL + 'debit' + '?' + req

            trans = Transaction.objects.create(
                transaction_id=trans_id,
                user_id=user,
                order_id=trans_id,
                amount=amount,
                currency=user.currency,
                transfer_from="gpi",
                transfer_to=wallet,
                product=GAME_TYPE_LIVE_CASINO,
                transaction_type=TRANSACTION_TRANSFER,
                status=TRAN_PENDING_TYPE
            )

        elif method == 0:
            url = GPI_URL + 'credit' + '?' + req

            trans = Transaction.objects.create(
                transaction_id=trans_id,
                user_id=user,
                order_id=trans_id,
                amount=amount,
                currency=user.currency,
                transfer_from=wallet,
                transfer_to="gpi",
                product=GAME_TYPE_LIVE_CASINO,
                transaction_type=TRANSACTION_TRANSFER,
                status=TRAN_PENDING_TYPE
            )

        res = requests.get(url)
            
        res = xmltodict.parse(res.text)

        if int(res["resp"]["error_code"]) == 0:
            trans = Transaction.objects.get(transaction_id=trans_id)

            trans.order_id = res["resp"]["trx_id"]
            trans.status = TRAN_COMPLETED_TYPE
            trans.save()

            # user.main_wallet = user.main_wallet + Decimal(amount)
            # user.save()

        return True
        
    except Exception as e:
        logger.error("Error: GPI Transfer API error -- {}".format(repr(e)))
        return False


def transCurrency(user):
    try:
        currency = user.currency

        if currency == CURRENCY_CNY:
            currency = "RMB"
        elif currency == CURRENCY_IDR:
            currency = "IDR"
        elif currency == CURRENCY_MYR:
            currency = "MYR"
        elif currency == CURRENCY_THB:
            currency = "THB"
        elif currency == CURRENCY_USD:
            currency = "USD"
        elif currency == CURRENCY_VND:
            currency = "VND"
        elif currency == CURRENCY_EUR:
            currency = "EUR"
        elif currency == CURRENCY_MMK:
            currency = "MMK"
        elif currency == CURRENCY_GBP:
            currency = "GBP"
        else:
            raise ValueError

        return currency
    except ValueError:
        logger.warning("Warning: GPI currency transform DOES NOT SUPPORT -- {}".format(currency))
    except Exception as e:
        logger.error("ERROR: GPI currency transform error -- {}".format(repr(e)))


def transLang(user):
    try:
        language = user.language

        if language == "English":
            language = "en-us"
        elif language == "Chinese":
            language = "zh-cn"
        elif language == "Thai":
            language = "th-th"
        elif language == "Vietnamese":
            language = "vi-vn"
        else:
            language = "en-us" # default
        
        return language
    except Exception as e:
        logger.warning("GPI transLang Function Error: {}".format(repr(e)))
        return "en-us" # default


# class LoginAPI(View):
#     def post(self, request, *kw, **args):
#         try:
#             data = json.loads(request.body)
#             username = data["username"]

#             user = CustomUser.objects.get(username=username)

#             req_param = {}
#             req_param["merch_id"] = MERCH_ID
#             req_param["merch_pwd"] = MERCH_PWD
#             req_param["cust_id"] = user.username
#             req_param["currency"] = transCurrency(user)

#             req = urllib.parse.urlencode(req_param)
    
#             url = GPI_URL + 'createuser' + '?' + req

#             res = requests.get(url)

#             res = xmltodict.parse(res.text)

#             return HttpResponse(json.dumps(res), content_type="json/application", status=200)
#         except ObjectDoesNotExist:
#             return HttpResponse("User Not found", content_type="plain/text", status=400)
#         except Exception as e:
#             logger.error("Error: GPI LoginAPI error -- {}".format(repr(e)))
#             return HttpResponse("Internal Error", content_type="plain/text", status=500)


class ValidateUserAPI(View):
    def get(self, request, *kw, **args):
        token = request.GET.get('ticket')
        res = {}

        try:
            user = Token.objects.get(key=token).user

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            resp = {}
            res["resp"] = resp

            resp["error_code"] = 0
            resp["cust_id"] = user.pk
            resp["cust_name"] = user.username
            resp["currency_code"] = transCurrency(user)
            resp["language"] = transLang(user)
            resp["country"] = user.country
            resp["ip"] = ip
            resp["date_of_birth"] = user.date_of_birth
            resp["test_cust"] = True

            logger.info("GPI ValidateUserAPI token: {}, user: {} successful".format(token, user.username))

        except ObjectDoesNotExist:
            resp = {}
            res["resp"] = resp

            resp["error_code"] = -2
            resp["err_message"] = "user does not exist"

            logger.warning("GPI ValidateUserAPI token: {} does not exist".format(token))

        except Exception as e:
            resp = {}
            res["resp"] = resp

            resp["error_code"] = -1
            resp["err_message"] = "Unknown Error"

            logger.critical("GPI ValidateUserAPI Error -- {}".format(repr(e)))

        res = xmltodict.unparse(res, pretty=True)
        return HttpResponse(res, content_type="application/xml", status=200)


# System will auto create user on the fly when “Authentication Success” & when “1st Debit request for user Success
class CreateUserAPI(View):
    def post(self, request, *kw, **args):
        try:
            data = json.loads(request.body)
            username = data['username']

            user = CustomUser.objects.get(username=username)

            req_param = {}
            req_param["merch_id"] = GPI_MERCH_ID
            req_param["merch_pwd"] = GPI_MERCH_PWD
            req_param["cust_id"] = user.username
            req_param["cust_name"] = user.username
            req_param["currency"] = transCurrency(user)

            req = urllib.parse.urlencode(req_param)
    
            url = GPI_URL + 'createuser' + '?' + req

            res = requests.get(url)

            res = xmltodict.parse(res.text)

            return HttpResponse(json.dumps(res), content_type="json/application", status=200)

        except ObjectDoesNotExist:
            logger.error("Error: can not find user -- {}".format(str(username)))
        except Exception as e:
            logger.error("Error: GPI CreateUserAPI error -- {}".format(repr(e)))
            return HttpResponse(status=400)


class GetBalanceAPI(View):
    def get(self, request, *kw, **args):
        username = request.GET.get("username")
        try:
            user = CustomUser.objects.get(username=username)

            req_param = {}
            req_param["merch_id"] = GPI_MERCH_ID
            req_param["merch_pwd"] = GPI_MERCH_PWD
            req_param["cust_id"] = user.username
            req_param["currency"] = transCurrency(user)

            req = urllib.parse.urlencode(req_param)
    
            url = GPI_URL + 'getbalance' + '?' + req

            res = requests.get(url)
            
            res = xmltodict.parse(res.text)

            return HttpResponse(json.dumps(res), content_type="json/application", status=200)

        except ObjectDoesNotExist:
            logger.warning("Error: can not find user -- {}".format(str(username)))
            return HttpResponse(status=404)
        
        except Exception as e:
            logger.error("Error: GPI GetBalanceAPI error -- {}".format(repr(e)))
            return HttpResponse(status=500)


# multiple requests with the same “trx_id” will only be executed once and no error message will be responded on the latter requests.
class DebitAPI(View):
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        username = request.GET.get("username")
        amount = request.GET.get("amount")
        to_wallet = request.GET.get("to_wallet")

        try:
            user = CustomUser.objects.get(username=username)

            currency = transCurrency(user)

            trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

            req_param = {}
            req_param["merch_id"] = GPI_MERCH_ID
            req_param["merch_pwd"] = GPI_MERCH_PWD
            req_param["cust_id"] = username
            req_param["currency"] = currency
            req_param["amount"] = amount
            req_param["trx_id"] = trans_id

            req = urllib.parse.urlencode(req_param)
    
            url = GPI_URL + 'debit' + '?' + req

            trans = Transaction.objects.create(
                transaction_id=trans_id,
                user_id=user,
                order_id=trans_id,
                amount=amount,
                currency=user.currency,
                transfer_from="GPI",
                transfer_to=to_wallet,
                product=GAME_TYPE_LIVE_CASINO,
                transaction_type=TRANSACTION_TRANSFER,
                status=TRAN_PENDING_TYPE
            )

            res = requests.get(url)
            
            res = xmltodict.parse(res.text)

            if int(res["resp"]["error_code"]) == 0:
                trans = Transaction.objects.get(transaction_id=trans_id)

                trans.order_id = res["resp"]["trx_id"]
                trans.status = TRAN_COMPLETED_TYPE
                trans.save()
                # trans = Transaction.objects.create(
                #     transaction_id=trans_id,
                #     user_id=user,
                #     order_id=res["resp"]["trx_id"],
                #     amount=amount,
                #     currency=user.currency,
                #     transfer_from="GPI",
                #     transfer_to="main_wallet",
                #     product=GAME_TYPE_LIVE_CASINO,
                #     transaction_type=TRANSACTION_TRANSFER,
                #     status=TRAN_COMPLETED_TYPE
                # )

                user.main_wallet = user.main_wallet + Decimal(amount)
                user.save()

            return HttpResponse(json.dumps(res), content_type="json/application", status=200)

        except ObjectDoesNotExist:
            logger.error("Error: can not find user -- {}".format(str(username)))
            return HttpResponse(status=400)
        
        except Exception as e:
            logger.error("Error: GPI DebitAPI error -- {}".format(repr(e)))
            return HttpResponse(repr(e))


# multiple requests with the same “trx_id” will only be executed once and no error message will be responded on the latter requests.
class CreditAPI(View):
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        username = request.GET.get("username")
        amount = request.GET.get("amount")
        from_wallet = request.GET.get("from_wallet")

        try:
            user = CustomUser.objects.get(username=username)

            currency = transCurrency(user)

            trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

            req_param = {}
            req_param["merch_id"] = GPI_MERCH_ID
            req_param["merch_pwd"] = GPI_MERCH_PWD
            req_param["cust_id"] = username
            req_param["currency"] = currency
            req_param["amount"] = amount
            req_param["trx_id"] = trans_id

            req = urllib.parse.urlencode(req_param)
    
            url = GPI_URL + 'credit' + '?' + req

            trans = Transaction.objects.create(
                transaction_id=trans_id,
                user_id=user,
                order_id=trans_id,
                amount=amount,
                currency=user.currency,
                transfer_from=from_wallet,
                transfer_to="GPI",
                product=GAME_TYPE_LIVE_CASINO,
                transaction_type=TRANSACTION_TRANSFER,
                status=TRAN_PENDING_TYPE
            )

            res = requests.get(url)
            
            res = xmltodict.parse(res.text)

            if int(res["resp"]["error_code"]) == 0:
                trans = Transaction.objects.get(transaction_id=trans_id)

                trans.order_id = res["resp"]["trx_id"]
                trans.status = TRAN_COMPLETED_TYPE
                trans.save()
                # trans = Transaction.objects.create(
                #     transaction_id=trans_id,
                #     user_id=user,
                #     order_id=res["resp"]["trx_id"],
                #     amount=amount,
                #     currency=user.currency,
                #     transfer_from="GPI",
                #     transfer_to="main_wallet",
                #     product=GAME_TYPE_LIVE_CASINO,
                #     transaction_type=TRANSACTION_TRANSFER,
                #     status=TRAN_COMPLETED_TYPE
                # )

                user.main_wallet = user.main_wallet - Decimal(amount)
                user.save()

            return HttpResponse(json.dumps(res), content_type="json/application", status=200)
        except ObjectDoesNotExist:
            logger.error("Error: can not find user -- {}".format(str(username)))
            return HttpResponse(status=404)
        
        except Exception as e:
            logger.error("Error: GPI CreditAPI error -- {}".format(repr(e)))
            return HttpResponse(status=500)


class CheckTransactionAPI(View):
    def get(self, request, *args, **kwargs):
        trx_id = request.GET.get("trx_id")
        try:
            req_param = {}
            req_param["merch_id"] = GPI_MERCH_ID
            req_param["merch_pwd"] = GPI_MERCH_PWD
            req_param["trx_id"] = trx_id

            req = urllib.parse.urlencode(req_param)
    
            url = GPI_URL + 'check' + '?' + req

            res = requests.get(url)
            
            res = xmltodict.parse(res.text)

            return HttpResponse(json.dumps(res), content_type="json/application", status=200)
        except Exception as e:
            logger.error("Error: GPI CheckTransactionAPI error -- {}".format(repr(e)))
            return HttpResponse(status=400)


class GetOnlineUserAPI(View):
    def get(self, request, *args, **kwargs):
        try:
            req_param = {}
            req_param["merch_id"] = GPI_MERCH_ID
            req_param["merch_pwd"] = GPI_MERCH_PWD

            req = urllib.parse.urlencode(req_param)

            url = GPI_LIVE_CASINO_URL + "onlineUser.html?" + req

            res = requests.get(url)

            return HttpResponse(res)
        except Exception as e:
            logger.warning("GPI GetOnlineUserAPI warning -- {}".format(repr(e)))
            return HttpResponse(status=400)

# cron job
class GetOpenBetsAPI(View):
    def get(self, request, *args, **kwargs):
        try:
            req_param = {}
            req_param["merch_id"] = GPI_MERCH_ID
            req_param["merch_pwd"] = GPI_MERCH_PWD

            req = urllib.parse.urlencode(req_param)

            url = GPI_LIVE_CASINO_URL + "openBets.html?" + req

            res = requests.get(url)

            return HttpResponse(res)
        except Exception as e:
            logger.warning("GPI GetOnlineUserAPI warning -- {}".format(repr(e)))
            return HttpResponse(status=400)


class LiveCasinoCreateUserAPI(View):
    def post(self, request, *kw, **args):
        try:
            data = json.loads(request.body)
            username = data['username']

            user = CustomUser.objects.get(username=username)

            req_param = {}
            req_param["merch_id"] = GPI_MERCH_ID
            req_param["merch_pwd"] = GPI_MERCH_PWD
            req_param["cust_id"] = user.username
            req_param["cust_name"] = user.username
            req_param["currency"] = transCurrency(user)

            req = urllib.parse.urlencode(req_param)
    
            url = GPI_LIVE_CASINO_URL + 'createUser.html' + '?' + req

            res = requests.get(url)

            res = xmltodict.parse(res.text)

            return HttpResponse(json.dumps(res), content_type="json/application", status=200)

        except ObjectDoesNotExist:
            logger.error("Error: can not find user -- {}".format(str(username)))
        except Exception as e:
            logger.error("Error: GPI CreateUserAPI error -- {}".format(repr(e)))
            return HttpResponse(repr(e))


class GetNewBetDetailAPI(View):
    def get(self, request, *kw, **args):
        try:
            # r = RedisClient().connect()
            # redis = RedisHelper()

            # start_time = redis.get_ky_bets_timestamp

            # timestamp = get_timestamp()
            # if start_time is None:
            #     start_time = timestamp - 300000 # five minutes before now

            # # Query Bet Order
            # if type(start_time) == bytes:
            #     start_time = start_time.decode("utf-8")

            # date_from = request.GET.get("date_from") # yyyy-MM-dd HH:mm:ss
            # date_to = request.GET.get("date_to")
            # date_from = datetime.datetime.now()
            # date_to = datetime.datetime.now()

            # req_param = {}
            # req_param["merch_id"] = GPI_MERCH_ID
            # req_param["merch_pwd"] = GPI_MERCH_PWD
            # req_param["date_from"] = date_from
            # req_param["date_to"] = date_to
            # req_param["cust_id"] = user.username
            # req_param["cust_name"] = user.username
            # req_param["currency"] = transCurrency(user)

            # req = urllib.parse.urlencode(req_param)
    
            # url = GPI_LIVE_CASINO_URL + 'newBetDetail.html' + '?' + req

            # res = requests.get(url)

            # res = xmltodict.parse(res.text)

            res = request.get(data)

            if res["resp"]["error_code"] == "0":
                res = res["resp"]["items"]

                provider = GameProvider.objects.get(provider_name=GPI_PROVIDER)
                category = Category.objects.filter(name='Table Games')

                for data in res["item"]:
                    gamebet = GameBet(provider=provider,
                            category=category[0],
                            user=user,
                            user_name=user.username,
                            amount_wagered=decimal.Decimal(cell_score[i]),
                            amount_won=decimal.Decimal(win_amount),
                            outcome=outcome,
                            transaction_id=trans_id,
                            market=ibetCN,
                            ref_no=game_id[i],
                            bet_time=bet_time,
                            resolved_time=resolved_time,
                            other_data={}
                        )
                return HttpResponse(json.dumps(res), content_type="json/application", status=200)

            return HttpResponse(json.dumps(res), content_type="json/application", status=200)

        except ObjectDoesNotExist:
            logger.error("Error: can not find user -- {}".format(str(username)))
        except Exception as e:
            logger.error("Error: GPI CreateUserAPI error -- {}".format(repr(e)))
            return HttpResponse(repr(e))
