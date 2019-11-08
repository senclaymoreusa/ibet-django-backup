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
from utils.aws_helper import getThirdPartyKeys

logger = logging.getLogger('django')

import base64


# connect AWS S3
third_party_keys = getThirdPartyKeys("ibet-admin-eudev", "config/gamesKeys.json")
KY_AES_KEY = third_party_keys["KAIYUAN"]["DESKEY"]
KY_MD5_KEY = third_party_keys["KAIYUAN"]["MD5KEY"]


BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

"""
:param key: Http request in API views
:param data: data needs to be encrypt
:returns: IPv4 address
"""
def aes_encode(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    # cipher_chunks.append()
    cipher_text = cipher.encrypt(pad(data))
    return cipher_text


def get_timestamp():
    return int(round(time.time() * 1000))


class KaiyuanAPI(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            s = data["s"]
            ip = get_client_ip(request)

            # timestamp = lambda: int(round(time.time() * 1000))
            timestamp = get_timestamp()

            agent = KY_AGENT

            s = int(s)

            if s != 6:
                account = data["account"]
                usr = CustomUser.objects.get(username=account)

            # Login
            if s == 0:
                money = data["money"]
                order_time = time.strftime("%Y%m%d%H%M%S")
                orderid = agent + str(order_time) + account
                linecode = KY_LINE_CODE_1
                kind_id = data["KindID"]

                param = "s=" + str(s) + "&account=" + account + "&money=" + money + "&orderid=" + orderid + "&ip=" + ip + "&lineCode=" + linecode + "&KindID=" + kind_id + "&lang=zh-CN"
            # Get Balance
            elif s == 1:
                param = "s=" + str(s) + "&account=" + account
            # Change Balance
            elif s == 2:
                # req_data = {}
                # req_data["user_id"] = usr.pk
                # req_data["from_wallet"] = "main_wallet"
                # req_data["to_wallet"] ="ky_wallet"
                # req_data["amount"] = data["amount"]
                money = data["money"]
                if transferRequest(usr, money, "main", "ky"):
                    order_time = time.strftime("%Y%m%d%H%M%S")
                    orderid = agent + str(order_time) + account

                    param = "s=" + str(s) + "&account=" + account + "&orderid=" + orderid + "&money=" + money
                else:
                    return HttpResponse(status=400)

            # Refund
            elif s == 3:
                money = data["money"]
                order_time = time.strftime("%Y%m%d%H%M%S")
                orderid = agent + str(order_time) + account

                param = "s=" + str(s) + "&account=" + account + "&orderid=" + orderid + "&money=" + money
            # Order Query
            elif s == 4:
                order_time = time.strftime("%Y%m%d%H%M%S")
                orderid = agent + str(order_time) + account

                param = "s=" + str(s) + "&orderid=" + orderid
            # Query The Player's Online Status
            elif s == 5:
                param = "s=" + str(s) + "&account=" + account
            # Query Bet Order
            elif s == 6:
                startTime = data["startTime"]
                endTime = data["endTime"]

                param = "s=" + str(s) + "&startTime=" + startTime + "&endTime=" + endTime
            # Query The Player's Total Points
            elif s == 7:
                param = "s=" + str(s) + "&account=" + account
            # Kick Player off
            elif s == 8:
                param = "s=" + str(s) + "&account=" + account
            else:
                return HttpResponse("Undefined request type")
            
            
            # kind_id = '0' # game lobby
            # "&KindID=" + kind_id
            param = aes_encode(KY_AES_KEY, param)
            param = base64.b64encode(param)
            param = str(param, "utf-8")

            key = KY_AGENT + str(timestamp) + KY_MD5_KEY
            key = hashlib.md5(key.encode())
            key = key.hexdigest()

            url = KY_API_URL if s != 6 else KY_RECORD_URL

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
            res = requests.get(url)
            if res.status_code == 200:
                res_data = res.json()
                print(res_data)
                if res_data['s'] == 101:
                    balance = float(res_data['d']['money'])
                elif res_data['s'] == 102:
                    balance = float(res_data['d']['money'])

                return HttpResponse(json.dumps(res.json()), content_type='application/json')
            else:
                return HttpResponse("404 Not Found")
        except Exception as e:
            logger.error("Bad Request for Kaiyuan Gaming: {}".format(repr(e)))
            return HttpResponse(status=400)