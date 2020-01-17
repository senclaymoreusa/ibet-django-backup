# Django Rest Framework
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

# Django
from django.views import View
from django.db import DatabaseError
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


logger = logging.getLogger('django')

MERCH_ID = "IBETP"
MERCH_PWD = "2C19AA9A-E3C6-4202-B29D-051E756736DA"
GPI_URL = "http://club8api.bet8uat.com/op/"
GPI_LIVE_CASINO_URL = "http://casino.bet8uat.com/csnbo/api/"


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
            currency = ""

        return currency
    except Exception as e:
        logger.error("ERROR: GPI currency transform error -- {}".format(repr(e)))
        return ""


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
        return "en-us"


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

        except ObjectDoesNotExist:
            resp = {}
            res["resp"] = resp

            resp["error_code"] = -2
            resp["err_message"] = "user does not exist"

        except Exception as e:
            print(repr(e))
            resp = {}
            res["resp"] = resp

            resp["error_code"] = -1
            resp["err_message"] = "Unknown Error"

        res = xmltodict.unparse(res, pretty=True)
        return HttpResponse(res, content_type="application/xml", status=200)


# System will auto create user on the fly when “Authentication Success” & when “1st Debit request for user Success
class CreateUserAPI(View):
    def get(self, request, *kw, **args):
        username = request.GET.get("username")

        try:
            user = CustomUser.objects.get(username=username)

            req_param = {}
            req_param["merch_id"] = MERCH_ID
            req_param["merch_pwd"] = MERCH_PWD
            req_param["cust_id"] = user.username
            req_param["currency"] = transCurrency(user)

            req = urllib.parse.urlencode(req_param)
    
            url = GPI_URL + 'createuser' + '?' + req

            res = requests.get(url)

            res = xmltodict.parse(res.text)

            return HttpResponse(json.dumps(res), content_type="json/application", status=200)

        except ObjectDoesNotExist:
            logger.error("Error: can not find user -- {}".format(str(username)))
        except Exception as e:
            logger.error("Error: GPI GetBalanceAPI error -- {}".format(repr(e)))


class GetBalanceAPI(View):
    def get(self, request, *kw, **args):
        username = request.GET.get("username")
        try:
            user = CustomUser.objects.get(username=username)

            req_param = {}
            req_param["merch_id"] = MERCH_ID
            req_param["merch_pwd"] = MERCH_PWD
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


class DebitAPI(View):
    def get(self, request, *args, **kwargs):
        username = request.GET.get("username")
        amount = request.GET.get("amount")

        try:
            user = CustomUser.objects.get(username=username)

            currency = transCurrency(user)

            req_param = {}
            req_param["merch_id"] = MERCH_ID
            req_param["merch_pwd"] = MERCH_PWD
            req_param["cust_id"] = username
            req_param["currency"] = currency
            req_param["amount"] = amount
            req_param["trx_id"] = "Test01"

            req = urllib.parse.urlencode(req_param)
    
            url = GPI_URL + 'debit' + '?' + req

            res = requests.get(url)
            
            res = xmltodict.parse(res.text)

            return HttpResponse(json.dumps(res), content_type="json/application", status=200)

        except ObjectDoesNotExist:
            logger.error("Error: can not find user -- {}".format(str(username)))
        
        except Exception as e:
            logger.error("Error: GPI GetBalanceAPI error -- {}".format(repr(e)))
            return HttpResponse('GET request!')


class CreditAPI(View):
    def get(self, request, *args, **kwargs):
        username = request.GET.get("username")
        amount = request.GET.get("amount")

        try:
            user = CustomUser.objects.get(username=username)

            currency = transCurrency(user)

            req_param = {}
            req_param["merch_id"] = MERCH_ID
            req_param["merch_pwd"] = MERCH_PWD
            req_param["cust_id"] = username
            req_param["currency"] = currency
            req_param["amount"] = amount
            req_param["trx_id"] = "Test11"

            req = urllib.parse.urlencode(req_param)
    
            url = GPI_URL + 'credit' + '?' + req

            res = requests.get(url)
            
            res = xmltodict.parse(res.text)

            return HttpResponse(json.dumps(res), content_type="json/application", status=200)

        except ObjectDoesNotExist:
            logger.error("Error: can not find user -- {}".format(str(username)))
        
        except Exception as e:
            logger.error("Error: GPI GetBalanceAPI error -- {}".format(repr(e)))
            return HttpResponse('GET request!')


class CheckTransactionAPI(View):
    def get(self, request, *args, **kwargs):
        trx_id = request.GET.get("trx_id")
        try:
            req_param = {}
            req_param["merch_id"] = MERCH_ID
            req_param["merch_pwd"] = MERCH_PWD
            req_param["trx_id"] = "Test11"

            req = urllib.parse.urlencode(req_param)
    
            url = GPI_URL + 'check' + '?' + req

            res = requests.get(url)
            
            res = xmltodict.parse(res.text)

            return HttpResponse(json.dumps(res), content_type="json/application", status=200)
        except Exception as e:
            logger.error("Error: GPI GetBalanceAPI error -- {}".format(repr(e)))
            return HttpResponse(status=400)


class GetOnlineUserAPI(View):
    def get(self, request, *args, **kwargs):
        try:
            req_param = {}
            req_param["merch_id"] = MERCH_ID
            req_param["merch_pwd"] = MERCH_PWD

            req = urllib.parse.urlencode(req_param)

            url = GPI_LIVE_CASINO_URL + "onlineUser.html?" + req

            res = requests.get(url)

            return HttpResponse(res)
        except Exception as e:
            print(repr(e))
            return HttpResponse(status=400)


class GetOpenBetsAPI(View):
    def get(self, request, *args, **kwargs):
        try:
            req_param = {}
            req_param["merch_id"] = MERCH_ID
            req_param["merch_pwd"] = MERCH_PWD

            req = urllib.parse.urlencode(req_param)

            url = GPI_LIVE_CASINO_URL + "openBets.html?" + req

            res = requests.get(url)

            return HttpResponse(res)
        except Exception as e:
            print(repr(e))
            return HttpResponse(status=400)
        return HttpResponse(200)