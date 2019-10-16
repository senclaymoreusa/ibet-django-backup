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
def des_encode(key, data):
    cipher_chunks = []
    cipher = AES.new(key, AES.MODE_ECB)
    cipher_text = cipher.encrypt(pad(data))
    return cipher_text


class KaiyuanLogin(View):
    def post(self, request, *args, **kwargs):
        data = request.body
        api = "https://kyapi.ky206.com:189/channelHandle"

        ip = get_client_ip(request)
        timestamp = lambda: int(round(time.time() * 1000))


        agent = KY_AGENT
        timestamp = lambda: int(round(time.time() * 1000))
        print(timestamp())

        param = ''
        s = '0'
        s = int(s)

        # Login
        if s == 0:
            account = data["account"]
            money = data["money"]
            orderid = agent + order_time + account
            linecode = "00001"

            param = "s=" + s + "&account=" + account + "&money=" + money + "&orderid=" + orderid + "&ip=" + ip + "&lineCode=" + linecode + "&lang=zh-CN"
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
        
        
        key = '0'
        linecode = "00001"
        # kind_id = '0' # game lobby
        # "&KindID=" + kind_id
       
        param = des_encode('DE675375C948CF2B', param)
        param = base64.b64encode(param)
        # ky_login_api = "https://kyapi.ky206.com:189/channelHandle" + "?agent=" + agent + "&timestamp=" + timestamp + "&"
        return HttpResponse(status=200)