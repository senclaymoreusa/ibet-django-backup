from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
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
from django.utils import timezone
import uuid
from  games.models import *
import json

from rest_framework.authtoken.models import Token
from Crypto.Cipher import DES3
# from pyDes import *
import base64
import pytz
import urllib


logger = logging.getLogger('django')

# def des_decrypt(s):
#     encrypt_key = '9d25ee5d1ffa0e01'
#     iv = encrypt_key
#     k = des(encrypt_key, ECB, iv, pad=None, padmode=PAD_PKCS7)
#     de = k.decrypt(base64.b64decode(s), padmode=PAD_PKCS7)
#     return de

IMES_KEY = "9d25ee5d1ffa0e01" 
IMES_URL = "http://ibet.esapi.test.imapi.net/"

def pad(m):
    return m+chr(16-len(m)%16)*(16-len(m)%16)


def des3Encryption(plain_text):
    # key = hashlib.md5(b'9d25ee5d1ffa0e01').digest()
    key = hashlib.md5(IMES_KEY.encode()).digest()
    cipher = DES3.new(key, DES3.MODE_ECB)
    cipher_text = cipher.encrypt(pad(plain_text))

    return str(base64.b64encode(cipher_text), "utf-8")


def des3Decryption(cipher_text):
    try:
        key = hashlib.md5(IMES_KEY.encode()).digest()
        cipher_text = base64.b64decode(cipher_text)
        cipher = DES3.new(key, DES3.MODE_ECB)
        plain_text = cipher.decrypt(cipher_text)
        return plain_text.decode()
    except Exception as e:
        print("Decrypt Error: {}".format(repr(e)))


def isLessThanFiveMin(req_time):
    try:
        print(req_time)
        req_time = datetime.datetime.strptime(req_time, '%b/%d/%Y %I:%M:%S %p')
        print(req_time)
        return True
    except Exception as e:
        print(repr(e))
        return False


class InplayLoginAPI(View):
    def post(self, request, *arg, **kwargs):
        try:
            data = json.loads(request.body)

            username = data['username']
            user = CustomUser.objects.get(username=username)

            post_data = {}
            sessionToken = Token.objects.get(user_id=user)
            post_data['Token'] = str(sessionToken)

            time_stamp = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
            time_stamp = des3Encryption(time_stamp)
            post_data['TimeStamp'] = str(time_stamp)
            
            url = IMES_URL + "api/login"
            
            res = requests.post(url, data=post_data)
            res = res.json()
            print(res)

            return HttpResponse(json.dumps(res), content_type='application/json')

            # if res['StatusCode'] == 0:
            #     return HttpResponse(status=200)
            # else:
            #     return HttpResponse(status=400)
        except Exception as e:
            logger.error("Inplay Matrix login error: {}".format(repr(e)))
            return HttpResponse(status=400)


class ValidateTokenAPI(View):
    def get(self, request, *arg, **kwargs):
        try:
            # data = json(request.body)
            # print(data)
            token = request.GET.get("token")
            user = Token.objects.get(key=token).user

            res = {}
            res["memberCode"] = user.username
            res["CurrencyCode"] = "RMB"
            # res["IPAddress"] = "127.0.0.1"
            res["statusCode"] = 100
            res["statusDesc"] = "Success"

            return HttpResponse(json.dumps(res), content_type="application/json", status=200)
        except Exception as e:
            logger.error("Inplay Matrix validation error: {}".format(repr(e)))
            return HttpResponse(status=400)


class InplayGetBalanceAPI(View):
    def get(self, request, *arg, **kwargs):
        balance_package = request.GET.get("balancePackage")
        date_sent = request.GET.get("dateSent")
        # data = "lbGQtVNxUDypUuwmTwOg5ROUx6IUpDxu1EbE7B+cNNHTP3oIVqIw2QQ6AFB85L6Y"
        # balance_package = "ZwgZhGFWmUv5vDi5q2ruVNc3lf+JmmxTctAdoxbVdOUeW+RbwyYE95B0M4EiVX/k"
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
                # response[]
                return HttpResponse("Wrong Event Type")
        except Exception as e:
            logger.error("Error: {}".format(repr(e)))
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
                return HttpResponse("Wrong event type")
        except Exception as e:
            logger.error("Error: {}".format(repr(e)))
            return HttpResponse(status=400)


class InplayDeductBalanceAPI(View):
    def get(self, request, *arg, **kwargs):
        balance_package = request.GET.get('balancePackage')
        package_id = request.GET.get('packageid')
        date_sent = request.GET.get('dateSent')

        try:
            # balance_package = "ZwgZhGFWmUv5vDi5q2ruVNNlKC+WU/nkctAdoxbVdOUeW+RbwyYE91w8OXAeAgw5G8cVCxZC5Lt6MFBoaBxSfdVG6C55NSVcRYyB4Fk76mo="
            balance_package = balance_package.replace(' ', '+')
            data = des3Decryption(balance_package)
            data = "".join([data.rsplit("}" , 1)[0] , "}"]) 
            data = json.loads(data)
            print(data)
            response = {}
            if data["EventTypeId"] == '1003':
                user = data["MemberCode"]
                amount = float(data["TransactionAmt"])
                user = CustomUser.objects.get(username=user)
                if user.main_wallet > amount:
                    # trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
                    # trans = Transaction.objects.create(
                    #     transaction_id=trans_id,
                    #     user_id=user,
                    #     order_id=package_id,
                    #     amount=amount,
                    #     currency=user_currency,
                    #     transfer_from="IMES",
                    #     transfer_to="main",
                    #     product=0,
                    #     transaction_type=TRANSACTION_TRANSFER,
                    #     status=TRAN_PENDING_TYPE
                    # )
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
            logger.error("Error: {}".format(repr(e)))
            return HttpResponse(status=400)


class InplayUpdateBalanceAPI(View):
    def post(self, request, *arg, **kwargs):
        data = json.loads(request.body)
        try:
            balance_package = "ZwgZhGFWmUv5vDi5q2ruVNNlKC+WU/nkctAdoxbVdOUeW+RbwyYE91w8OXAeAgw5G8cVCxZC5Lt6MFBoaBxSfTnRLW6RazhbRYyB4Fk76mo="
            print(balance_package)
            data = des3Decryption(balance_package)
            data = "".join([data.rsplit("}" , 1)[0] , "}"]) 
            # print(data)
            # print(data["EventTypeId"])
            #  data = json.dumps(str(data))
            data = json.loads(data)
            if data["EventTypeId"] == '4002':
                user = data["MemberCode"]
                # amount = float(data["TransactionAmt"])
                # user = CustomUser.objects.get(username=user)
                match_no = data["MatchNo"]
                bet_detail_list = data["BetDetailList"]
                for bet in bet_detail_list:
                    member_code = bet["MemberCode"]
                    bet_no = bet["BetNo"]
                    amount = bet["TransactionAmt"]

                    user = CustomUser.objects.get(user)

                    trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

                    with transaction.atomic():
                        trans = Transaction.objects.create(
                            transaction_id=trans_id,
                            user_id=user,
                            order_id=trans_id,
                            amount=amount,
                            currency=user_currency,
                            transfer_from="IMES",
                            transfer_to="main",
                            product=0,
                            transaction_type=TRANSACTION_TRANSFER,
                            status=TRAN_PENDING_TYPE
                        )

                        user.imes_wallet += amount
                        user.save()

                    res = {}
                    res["DateReceived"] = timezone.now()
                    res["DateSent"] = timezone.now()
                    res["StatusCode"] = 100
                    res["StatusMessage"] = "Success"
                    res["PackageId"] = 374
                    res["Balance"] = 0.0

                    return HttpResponse(json.dumps(res), content_type='application/json', status=200)
                print(amount)
        except Exception as e:
            print("Error: {}".format(repr(e)))

        return HttpResponse(status=200)


class TestDecryption(View):
    def get(self, request, *arg, **kwargs):
        try:
            api_no = request.GET.get('api')
            event_type_id = request.GET.get('EventTypeId')  # "EventTypeId": 1001,
            member_code = request.GET.get('MemberCode')  # "MemberCode": "bae02",
            transaction_amt = request.GET.get('TransactionAmt') # "TransactionAmt": 100.0
        
            plain_json = {}
            plain_json["EventTypeId"] = event_type_id
            plain_json["MemberCode"] = member_code

            if api_no == '1':
                pass
                # plain_json = json.dumps(plain_json)
            elif api_no == '2':
                plain_json["TransactionAmt"] = transaction_amt

            plain_json = json.dumps(plain_json)
            print(plain_json)
            print(type(plain_json))
        
            # key = hashlib.md5(b'9d25ee5d1ffa0e01').digest()

            cipher_json = des3Encryption(plain_json)

            print(cipher_json)

            plain_json = des3Decryption(cipher_json)

            plain_json = "".join([plain_json.rsplit("}" , 1)[0] , "}"]) 
            print(plain_json)

            plain_json = json.loads(plain_json)

            return HttpResponse(cipher_json)
        except Exception as e:
            print(e)