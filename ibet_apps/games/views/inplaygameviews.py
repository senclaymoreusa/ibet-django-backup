from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from users.models import CustomUser
from accounting.models import *
import simplejson as json
import decimal
import requests
from utils.constants import *
import random
import hashlib 
import logging
import datetime
from datetime import timedelta
from django.utils import timezone
import uuid
from  games.models import *
import json

from rest_framework.authtoken.models import Token
from Crypto.Cipher import DES3
import xmltodict
import base64
import pytz
import urllib

from utils.aws_helper import getThirdPartyKeys

logger = logging.getLogger('django')

def pad(m):
    return m+chr(16-len(m)%16)*(16-len(m)%16)


def des3Encryption(plain_text):
    try:
        key = hashlib.md5(IMES_KEY.encode()).digest()
        cipher = DES3.new(key, DES3.MODE_ECB)
        cipher_text = cipher.encrypt(pad(plain_text))

        return str(base64.b64encode(cipher_text), "utf-8")
    except Exception as e:
        logger.error("IMES Encrypt Error: {}".format(repr(e)))
        return ""


def des3Decryption(cipher_text):
    try:
        key = hashlib.md5(IMES_KEY.encode()).digest()
        cipher_text = base64.b64decode(cipher_text)
        cipher = DES3.new(key, DES3.MODE_ECB)
        plain_text = cipher.decrypt(cipher_text)
        return plain_text.decode()
    except Exception as e:
        logger.error("IMES Decrypt Error: {}".format(repr(e)))
        return ""


class InplayLoginAPI(View):
    def post(self, request, *arg, **kwargs):
        try:
            data = json.loads(request.body)

            username = data['username']
            user = CustomUser.objects.get(username=username)

            post_data = {}
            sessionToken = Token.objects.get(user_id=user)
            # post_data['Token'] = str(sessionToken)
            post_data['Token'] = "e789cd6b4cc84f9ff8de0bee5a0bf8f5485c6d9f"

            # time_stamp = (datetime.datetime.utcnow() - timedelta(hours=4)).strftime("%a, %d %b %Y %H:%M:%S GMT")
            time_stamp = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
            time_stamp = des3Encryption(time_stamp)
            post_data['TimeStamp'] = str(time_stamp)

            url = IMES_URL + "api/login"
            headers = {'Content-type': 'application/json'}
            res = requests.post(url, data=json.dumps(post_data), headers=headers)

            res = res.json()

            return HttpResponse(json.dumps(res), content_type='application/json')
        except ObjectDoesNotExist:
            logger.info("User: {} does not exist".format(username))

            res = {}
            res["statusCode"] = 101 # Invalid User
            res["statusDesc"] = "Invalid User"

            return HttpResponse(json.dumps(res), content_type="application/json", status=200)
        except Exception as e:
            logger.error("FATAL__ERROR: IMES Login Error -- {}".format(repr(e)))
            return HttpResponse("Login Error", content_type='text/plain', status=400)


class ValidateTokenAPI(View):
    def get(self, request, *arg, **kwargs):
        try:
            token = request.GET.get("token")
            res = {}

            user = Token.objects.get(key=token).user

            res["memberCode"] = user.username
            if user.currency == CURRENCY_CNY:
                res["CurrencyCode"] = "RMB"
            if user.currency == CURRENCY_USD:
                res["CurrencyCode"] = "USD"
            if user.currency == CURRENCY_THB:
                res["CurrencyCode"] = "THB"
            if user.currency == CURRENCY_IDR:
                res["CurrencyCode"] = "IDR"
            if user.currency == CURRENCY_HKD:
                res["CurrencyCode"] = "HKD"
            if user.currency == CURRENCY_AUD:
                res["CurrencyCode"] = "AUD"
            if user.currency == CURRENCY_MYR:
                res["CurrencyCode"] = "MYR"
            if user.currency == CURRENCY_MMK:
                res["CurrencyCode"] = "MMK"
            if user.currency == CURRENCY_EUR:
                res["CurrencyCode"] = "EUR"
            if user.currency == CURRENCY_GBP:
                res["CurrencyCode"] = "GBP"
            if user.currency == CURRENCY_NOK:
                res["CurrencyCode"] = "NOK"

            res["statusCode"] = 100
            res["statusDesc"] = "Success"

            return HttpResponse(json.dumps(res), content_type="application/json", status=200)
        except ObjectDoesNotExist as e:
            logger.info(str(token) + " : {}".format(repr(e)))

            res = {}
            res["statusCode"] = 101 # Invalid User
            res["statusDesc"] = "Invalid User"

            return HttpResponse(json.dumps(res), content_type="application/json", status=200)
        except Exception as e:
            logger.error("IMES Validation Error: {}".format(repr(e)))

            res = {}
            res["statusCode"] = 301 # Internal Error
            res["statusDesc"] = "Internal Error"
            
            return HttpResponse(json.dumps(res), content_type="application/json", status=400)


class InplayGetBalanceAPI(View):
    def get(self, request, *arg, **kwargs):
        balance_package = request.GET.get("balancePackage")
        date_sent = request.GET.get("dateSent")
        try:
            balance_package = balance_package.replace(' ', '+')
            data = des3Decryption(balance_package)
            data = "".join([data.rsplit("}" , 1)[0] , "}"])
            data = json.loads(data)

            response = {}
            if data["EventTypeId"] == '1000':
                member_code = data["MemberCode"]
                member_code = member_code.strip('\"')
                user = CustomUser.objects.get(username=member_code)

                response["StatusCode"] = 100
                response["StatusMessage"] = "Success"
                response["PackageId"] = str(uuid.uuid1())
                response["Balance"] = float(user.main_wallet)

                response = json.dumps(response)

                ciphertext = des3Encryption(response)
                return HttpResponse(ciphertext, content_type='text/plain', status=200)
            else:
                response["StatusCode"] = -100
                response["StatusMessage"] = "Wrong Event Type"

                response = json.dumps(response)
                cipher_text = des3Encryption(response)
        except Exception as e:
            logger.error("IMES GET Balance Error: {}".format(repr(e)))
            return HttpResponse(status=400)


class InplayGetApprovalAPI(View):
    def get(self, request, *arg, **kwargs):
        balance_package = request.GET.get('balancePackage')
        package_id = request.GET.get('packageid')
        date_sent = request.GET.get('dateSent')
        try:
            # balance_package = "ZwgZhGFWmUv5vDi5q2ruVAUij5STfGZ6ctAdoxbVdOUeW+RbwyYE91w8OXAeAgw5G8cVCxZC5Lt6MFBoaBxSfdVG6C55NSVcRYyB4Fk76mo="
            balance_package = balance_package.replace(' ', '+')
            data = des3Decryption(balance_package)
            data = "".join([data.rsplit("}" , 1)[0], "}"])
            data = json.loads(data)
            response = {}
            if data["EventTypeId"] == '1001':
                member_code = data["MemberCode"]
                amount = float(data["TransactionAmt"])
                user = CustomUser.objects.get(username=member_code)
                if user.main_wallet >= amount:
                    # response["DateReceived"] = timezone.now()
                    # response["DateSent"] = timezone.now()
                    response["StatusCode"] = 100
                    response["StatusMessage"] = "Balance is sufficient, go ahead"
                    response["PackageId"] = package_id
                    response["Balance"] = float(user.main_wallet)
                else:
                    response["StatusCode"] = -100
                    
                response = json.dumps(response)
                cipher_text = des3Encryption(response)
                return HttpResponse(cipher_text, content_type='text/plain', status=200)
            else:
                response["StatusCode"] = -100
                    
                response = json.dumps(response)
                cipher_text = des3Encryption(response)
                return HttpResponse(cipher_text, content_type='text/plain', status=200)
        except Exception as e:
            logger.error("FATAL__ERROR: IMES Get Approval Error -- {}".format(repr(e)))
            
            response = {}
            response["StatusCode"] = -100
            response["StatusMessage"] = "Internal Error"

            response = json.dumps(response)
            cipher_text = des3Encryption(response)

            return HttpResponse(cipher_text, content_type='text/plain', status=200)


class InplayDeductBalanceAPI(View):
    def get(self, request, *arg, **kwargs):
        balance_package = request.GET.get('balancePackage')
        package_id = request.GET.get('packageid')
        date_sent = request.GET.get('dateSent')

        try:
            balance_package = balance_package.replace(' ', '+')
            data = des3Decryption(balance_package)
            data = "".join([data.rsplit("}" , 1)[0] , "}"]) 
            data = json.loads(data)
            response = {}
            if data["EventTypeId"] == '1003':
                user = data["MemberCode"]
                amount = float(data["TransactionAmt"])
                user = CustomUser.objects.get(username=user)
                if user.main_wallet > amount:
                    trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

                    provider = GameProvider.objects.get(provider_name=IMES_PROVIDER)
                    category = Category.objects.get(name='Sports')

                    with transaction.atomic():
 
                        GameBet.objects.create(
                            provider=provider,
                            category=category,
                            user=user,
                            user_name=user.username,
                            amount_wagered=decimal.Decimal(amount),
                            transaction_id=trans_id,
                            market=ibetCN,
                            ref_no=package_id
                        )

                        user.main_wallet = user.main_wallet - decimal.Decimal(amount)
                        user.save()
                    
                        # res["DateReceived"] = str(timezone.now())
                        # res["DateSent"] = str(timezone.now())
                        response["StatusCode"] = 100
                        response["StatusMessage"] = "Success"
                        response["PackageId"] = package_id
                        response["Balance"] = float(user.main_wallet)
                else:
                    response["StatusCode"] = -100
                    response["StatusMessage"] = "Not enough balance"

                response = json.dumps(response)
                cipher_text = des3Encryption(response)

                return HttpResponse(cipher_text, content_type='text/plain', status=200)
            else:
                return HttpResponse("Wrong Event type")
        except Exception as e:
            logger.error("IMES Deduct Balance Error: {}".format(repr(e)))

            response["StatusCode"] = -100
            response["StatusMessage"] = "Internal Error"

            response = json.dumps(response)
            cipher_text = des3Encryption(response)

            return HttpResponse(cipher_text, content_type='text/plain', status=200)


class InplayUpdateBalanceAPI(View):
    def get(self, request, *arg, **kwargs):
        balance_package = request.GET.get('balancePackage')
        package_id = request.GET.get('packageid')
        date_sent = request.GET.get('dateSent')
        try:
            balance_package = balance_package.replace(' ', '+')
            data = des3Decryption(balance_package)
            data = "".join([data.rsplit("}" , 1)[0] , "}"])
            data = json.loads(data)
            if data["EventTypeId"] == '4002':
                provider = GameProvider.objects.get(provider_name=IMES_PROVIDER)
                category = Category.objects.get(name='Sports')

                match_no = data["MatchNo"]
                bet_detail_list = data["BetDetailList"]
                bet_detail_list = json.loads(bet_detail_list)
                for bet in bet_detail_list:
                    member_code = bet["MemberCode"]
                    bet_no = bet["BetNo"]
                    amount = bet["TransactionAmt"]

                    user = CustomUser.objects.get(username=member_code)

                    trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

                    with transaction.atomic():

                        GameBet.objects.get_or_create(
                            provider = provider,
                            category = category,
                            # game = models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True) # small game
                            # game_name = models.CharField(max_length=200, blank=True, null=True) # subset of category, (e.g within basketball, there's NBA, FIBA, euroleague, within soccer there's euroleague, premier league, etc.) 
                            user = user,
                            user_name = user.username,
                            # amount_wagered = decimal.Decimal(amount),
                            amount_won = decimal.Decimal(amount),
                            # # outcome = models.BooleanField() # true = win, false = lost
                            # outcome = models.SmallIntegerField(choices=OUTCOME_CHOICES, null=True, blank=True)
                            # odds = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=2,) # payout odds (in american odds), e.g. +500, -110, etc.
                            # bet_type = models.CharField(max_length=6, choices=BET_TYPES_CHOICES, null=True, blank=True)
                            # line = models.CharField(max_length=50, null=True, blank=True) # examples: if bet_type=spread: <+/-><point difference> | bet_type=moneyline: name of team | bet_type=total: <over/under> 200
                            transaction_id = trans_id,
                            # currency = models.SmallIntegerField(choices=CURRENCY_CHOICES, default=0, verbose_name=_("Currency"))
                            market = ibetCN,
                            ref_no = bet_no,
                            resolved_time = timezone.now(),
                            other_data = json.dumps({"bet_no" : bet_no})
                        )

                        user.main_wallet = user.main_wallet + decimal.Decimal(amount)
                        user.save()

                res = {}

                res["StatusCode"] = 100
                res["StatusMessage"] = "Acknowledged"

                return HttpResponse(json.dumps(res), content_type='application/json', status=200)
        except Exception as e:
            logger.error("IMES Update Balance Error: {}".format(repr(e)))
            return HttpResponse(repr(e), status=400)


class InplayPostBetDetailsAPI(View):
    def post(self, request, *arg, **kwargs):
        bet_package = request.POST.get('postPackage')
        
        try:
            bet_package = bet_package.replace(' ', '+')
            data = des3Decryption(data)
            data = "".join([data.rsplit(">" , 1)[0] , ">"])
            data = xmltodict.parse(data)

            member_bet_details = data["BetDetails"]["MemberBetDetails"]

            member_code = member_bet_details["memberCode"]
            bet_id = member_bet_details["betId"]
            bet_time = member_bet_details["betTime"]
            sports_name = member_bet_details["sportsName"]
            bet_amt = member_bet_details["betAmt"]
            odds = member_bet_details["odds"]

            user = CustomUser.objects.get(username=member_code)

            provider = GameProvider.objects.get(provider_name=IMES_PROVIDER)
            category = Category.objects.filter(name='SPORTS')

            trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

            GameBet.objects.get_or_create(
                provider = provider,
                category = category[0],
                # game = models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True) # small game
                # game_name = models.CharField(max_length=200, blank=True, null=True) # subset of category, (e.g within basketball, there's NBA, FIBA, euroleague, within soccer there's euroleague, premier league, etc.) 
                user = user,
                user_name = user.username,
                amount_wagered = decimal.Decimal(bet_amt),
                # amount_won = models.DecimalField(max_digits=12, decimal_places=2, null=True) # if amount_won = 0, outcome is also 0 (false)
                # # outcome = models.BooleanField() # true = win, false = lost
                # outcome = models.SmallIntegerField(choices=OUTCOME_CHOICES, null=True, blank=True)
                # odds = Decimal(odds) # payout odds (in american odds), e.g. +500, -110, etc.
                # bet_type = models.CharField(max_length=6, choices=BET_TYPES_CHOICES, null=True, blank=True)
                # line = models.CharField(max_length=50, null=True, blank=True) # examples: if bet_type=spread: <+/-><point difference> | bet_type=moneyline: name of team | bet_type=total: <over/under> 200
                transaction_id = trans_id,
                currency = user.currency,
                market = ibetCN,
                ref_no = bet_id,
                # resolved_time = models.DateTimeField(null=True, blank=True)
                other_data = json.loads({"data": data})
            )
            
            return HttpResponse(status=200)
        except Exception as e:
            logger.error("Inplay Post Bet Error {}".format(repr(e)))
            # return HttpResponse(repr(e), status=400) No return here


class TestDecryption(View):
    def get(self, request, *arg, **kwargs):
        try:
            api_no = request.GET.get('api')
            event_type_id = request.GET.get('EventTypeId')  # "EventTypeId": 1001,
            member_code = request.GET.get('MemberCode')  # "MemberCode": "bae02",
            transaction_amt = request.GET.get('TransactionAmt') # "TransactionAmt": 100.0
            match_no = request.GET.get('MatchNo') # "MatchNo": 1688512
            bet_detail_list = request.GET.get('BetDetailList')

            plain_json = {}
            plain_json["EventTypeId"] = event_type_id
            plain_json["MemberCode"] = member_code

            if api_no == '1':
                pass
                # plain_json = json.dumps(plain_json)
            elif api_no == '2':
                plain_json["TransactionAmt"] = transaction_amt
            elif api_no == '6':
                plain_json["MatchNo"] = match_no
                plain_json["BetDetailList"] = bet_detail_list

            plain_json = json.dumps(plain_json)
        
            # key = hashlib.md5(b'9d25ee5d1ffa0e01').digest()

            cipher_json = des3Encryption(plain_json)

            plain_json = des3Decryption(cipher_json)

            plain_json = "".join([plain_json.rsplit("}" , 1)[0] , "}"]) 

            plain_json = json.loads(plain_json)

            return HttpResponse(cipher_json)
        except Exception as e:
            print(repr(e))