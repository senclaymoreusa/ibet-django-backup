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

def pad(m):
    return m+chr(16-len(m)%16)*(16-len(m)%16)

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
        return HttpResponse("I love you!")

        # data = requests.body
        data = "lbGQtVNxUDypUuwmTwOg5ROUx6IUpDxu1EbE7B+cNNHTP3oIVqIw2QQ6AFB85L6Y"
        # key = hashlib.md5('9d25ee5d1ffa0e01'.encode()).digest()
        key = "9d25ee5d1ffa0e01"

        try:
            cipher = DES3.new(key, DES3.MODE_ECB)
            plain_text = cipher.decrypt(data)
            print(plain_text)
            print(str(plain_text, "utf-8"))

            return HttpResponse(status=200)
        except Exception as e:
            print(e)


# class InplayGetApprovalAPI(View):
#     return HttpResponse(status=200)


# class InplayDeductBalanceAPI(View):
#     return HttpResponse(status=200)


# class InplayUpdateBalanceAPI(View):
#     return HttpResponse(status=200)