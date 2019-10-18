from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from users.models import CustomUser
import simplejson as json
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
import time
import urllib

from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad
from games.helper import *

logger = logging.getLogger('django')

import base64
BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

"""
:param key: Http request in API views
:param data: data needs to be encrypt
:returns: IPv4 address
"""
def aes_encode(key, data):
    cipher_chunks = []
    cipher = AES.new(key, AES.MODE_ECB)
    # cipher_chunks.append()
    cipher_text = cipher.encrypt(pad(data))
    return cipher_text


def get_timestamp():
    return int(round(time.time() * 1000))


class KaiyuanLogin(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        print(data)

        s = data["s"]
        ip = get_client_ip(request)

        # timestamp = lambda: int(round(time.time() * 1000))
        timestamp = get_timestamp()

        agent = KY_AGENT

        s = int(s)

        # Login
        if s == 0:
            account = data["account"]
            money = data["money"]
            order_time = time.strftime("%Y%m%d%H%M%S")
            orderid = agent + str(order_time) + account
            linecode = KY_LINE_CODE_1

            param = "s=" + str(s) + "&account=" + account + "&money=" + money + "&orderid=" + orderid + "&ip=" + ip + "&lineCode=" + linecode + "&lang=zh-CN"
        # Get Balance
        elif s == 1:
            param = "s=" + s + "&account=" + account
        # Change Balance
        elif s == 2:
            param = "s=" + s + "&account=" + account + "&orderid=" + orderId + "&money=" + money + "&ip=" + ip
        # Refund
        elif s == 3:
            param = "s=" + s + "&account=" + account + "&orderid=" + orderId + "&money=" + money + "&ip=" + ip
        # Order Query
        elif s == 4:
            param = "s=" + s + "&orderid=" + orderId
        # Query The Player's Online Status
        elif s == 5:
            param = "s=" + s + "&account=" + account
        # Query Bet Order
        elif s == 6:
            startTime = data["startTime"]
            endTime = data["endTime"]
            param = "s=" + s + "&startTime=" + startTime + "&endTime=" + endTime
        # Query The Player's Total Points
        elif s == 7:
            param = "s=" + s + "&account=" + account
        # Kick Player off
        elif s == 8:
            param = "s=" + s + "&account=" + account
        
        
        # kind_id = '0' # game lobby
        # "&KindID=" + kind_id
        try:
            param = aes_encode(KY_AES_KEY, param)
            # print(param)
            # param = param.decode('utf-8')
            param = base64.b64encode(param)
            param = str(param, "utf-8")
            # print(param)
            
            key = KY_AGENT + str(timestamp) + KY_MD5_KEY
            key = hashlib.md5(key.encode())
            key = key.hexdigest()

            url = KY_API_URL

            req_param = {}
            req_param["agent"] = agent
            req_param["timestamp"] = str(timestamp)
            req_param["param"] = param
            req_param["key"] = key
            # url += "?agent=" + agent
            # url += "&timestamp=" + str(timestamp)
            # url += "&param=" + param
            # url += "&key=" + str(key)
            req = urllib.parse.urlencode(req_param)
            url = url + '?' + req
            print(url)
            # ky_login_api = "https://kyapi.ky206.com:189/channelHandle" + "?agent=" + agent + "&timestamp=" + timestamp + "&"
            return HttpResponse(status=200)
        except Exception as e:
            print(e)
            return HttpResponse(status=400)