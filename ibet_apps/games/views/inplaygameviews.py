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

from Crypto.Cipher import DES3
import base64


logger = logging.getLogger('django')

def pad(m):
    return m+chr(16-len(m)%16)*(16-len(m)%16)

class InplayLoginAPI(View):
    def post(self, request, *arg, **kwargs):
        try:
            user = CustomUser.objects.get(username='Bobby')
            token = user.token

            key = hashlib.md5('9d25ee5d1ffa0e01'.encode()).digest()

            cipher = DES3.new(key, DES3.MODE_ECB)
            time_stamp = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            print(time_stamp)

            time_stamp = cipher.encrypt(pad(time_stamp))
            time_stamp = base64.b64encode(time_stamp)
            time_stamp = str(time_stamp, "utf-8")
            print(time_stamp)

            return HttpResponse(status=200)
        except Exception as e:
            print("Error:", repr(e))


class InplayGetBalanceAPI(View):
    def get(self, request, *arg, **kwargs):
        params = requests
        return HttpResponse(status=200)


# class InplayGetApprovalAPI(View):
#     return HttpResponse(status=200)


# class InplayDeductBalanceAPI(View):
#     return HttpResponse(status=200)


# class InplayUpdateBalanceAPI(View):
#     return HttpResponse(status=200)