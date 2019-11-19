from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from users.models import CustomUser
import simplejson as json
import xmltodict
import decimal
import requests
from utils.constants import *
import random
import hashlib 
import logging
import datetime
from datetime import date
from django.utils import timezone
import uuid
from  games.models import *
import json

from rest_framework.authtoken.models import Token
from Crypto.Cipher import DES3
# from pyDes import *
import base64
import pytz


logger = logging.getLogger('django')

# def des_decrypt(s):
#     encrypt_key = '9d25ee5d1ffa0e01'
#     iv = encrypt_key
#     k = des(encrypt_key, ECB, iv, pad=None, padmode=PAD_PKCS7)
#     de = k.decrypt(base64.b64decode(s), padmode=PAD_PKCS7)
#     return de

IMES_KEY = "9d25ee5d1ffa0e01" 


def pad(m):
    return m+chr(16-len(m)%16)*(16-len(m)%16)


def des3Encryption(plain_text):
    # key = hashlib.md5(b'9d25ee5d1ffa0e01').digest()
    key = hashlib.md5(IMES_KEY.encode()).digest()
    cipher = DES3.new(key, DES3.MODE_ECB)
    cipher_text = cipher.encrypt(pad(plain_text))

    return str(base64.b64encode(cipher_text), "utf-8")


def des3Decryption(cipher_text, key):
    cipher_text = base64.b64decode(cipher_text)
    cipher = DES3.new(key, DES3.MODE_ECB)
    plain_text = cipher.decrypt(cipher_text)
    return plain_text.decode()


class InplayLoginAPI(View):
    def post(self, request, *arg, **kwargs):
        try:
            data = request.body

            user = CustomUser.objects.get(username='Bobby')
            if user:
                # sessionToken = Token.objects.get(user_id=user)
                # print(sessionToken)
                token = {}
                token["agent"] = agent
                req_param["timestamp"] = str(timestamp)
                req_param["param"] = param
                req_param["key"] = key
                # url += "?agent=" + agent
                # url += "&timestamp=" + str(timestamp)
                # url += "&param=" + param
                # url += "&key=" + str(key)
                req = urllib.parse.urlencode(req_param)
            else:
                print("User not exist")


            key = hashlib.md5(b'9d25ee5d1ffa0e01').digest()

            cipher = DES3.new(key, DES3.MODE_ECB)
            time_stamp = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
            print(time_stamp)

            time_stamp = cipher.encrypt(pad(time_stamp))
            time_stamp = base64.b64encode(time_stamp)
            time_stamp = str(time_stamp, "utf-8")
            print(time_stamp)

            return HttpResponse(status=200)
        except Exception as e:
            print("Error:", repr(e))


class ValidateTokenAPI(View):
    def get(self, request, *arg, **kwargs):
        data = request.body
        print(data)
        return HttpResponse(status=400)


class InplayGetBalanceAPI(View):
    def get(self, request, *arg, **kwargs):
        
        balance_package = request.GET.get("balancePackage")
        dateSent = request.GET.GET("dateSent")
        # data = "lbGQtVNxUDypUuwmTwOg5ROUx6IUpDxu1EbE7B+cNNHTP3oIVqIw2QQ6AFB85L6Y"

        key = hashlib.md5('9d25ee5d1ffa0e01'.encode()).digest()
        # key = "9d25ee5d1ffa0e01"

        try:
            plain_json = des3Decryption(balance_package, key)

            member_code = plain_json["MemberCode"]

            user = CustomUser.objects.get(username=member_code)

            response = {}
            if user:
                response["StatusCode"] = 100
                response["StatusMessage"] = "Success"
                response["PackageId"] = uuid.uuid1()
                response["Balance"] = user.main_wallet

                response = json.dumps(response)

                ciphertext = des3Encryption(response)

            else:
                return HttpResponse(status=404)

            return HttpResponse(status=200)
        except Exception as e:
            print(e)


class InplayGetApprovalAPI(View):
    def get(self, request, *arg, **kwargs):
        balance_package = request.GET.get('balancePackage')
        package_id = request.GET.get('balancePackage')
        date_sent = request.GET.get('dateSent')

        # try:

        #     return HttpResponse(status=200)


# class InplayDeductBalanceAPI(View):
#     return HttpResponse(status=200)


# class InplayUpdateBalanceAPI(View):
#     return HttpResponse(status=200)


class TestDecryption(View):
    def get(self, request, *arg, **kwargs):

        event_type_id = request.GET.get('EventTypeId')  # "EventTypeId": 1001,
        member_code = request.GET.get('MemberCode')  # "MemberCode": "bae02",
        package_id = request.GET.get('TransactionAmt') # "TransactionAmt": 100.0
        
        plain_json = {}
        plain_json["Account"] = "Bobby"
        plain_json["Success"] = 0

        plain_json = json.dumps(plain_json)
        
        key = hashlib.md5(b'9d25ee5d1ffa0e01').digest()

        cipher_json = des3Encryption(plain_json, key)

        print(cipher_json)

        plain_json = des3Decryption(cipher_json, key)

        # plain_json = json.loads(plain_json)
        print(plain_json)

        return HttpResponse(status=200)