from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from django.db import transaction, IntegrityError
from users.models import CustomUser
from accounting.models import * 
import simplejson as json
from decimal import Decimal
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
from background_task import background
import redis
from utils.redisClient import RedisClient
from utils.redisHelper import RedisHelper

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


def kyTransfer(user, amount, wallet, method):
    try:
        # trans_id = user.username + strftime("%Y%m%d%H%M%S", gmtime())+str(random.randint(0,10000000))
        trans_id = user.username + time.strftime("%Y%m%d%H%M%S") + str(random.randint(0,10000000))
        user_currency = int(user.currency)

        if method == 0:
            operation_type = 2
            if user.currency == CURRENCY_CNY:
                amount = amount
            elif user.currency == CURRENCY_USD:
                amount = 6.2808 * amount
            elif user.currency == CURRENCY_THB:
                amount = 0.2016 * amount
            elif user.currency == CURRENCY_EUR:
                amount = 7.616 * amount
            elif user.currency == CURRENCY_IDR:
                amount = 0.0005 * amount
            elif user.currency == CURRENCY_VND:
                amount = 0.0003 * amount
            elif user.currency == CURRENCY_MYR:
                amount = 1.6229 * amount
            elif user.currency == CURRENCY_TEST or (user.currency == CURRENCY_TTC):
                amount = 20
            else:
                amount = 10

        elif method == 1:
            operation_type = 3
            if user.currency == CURRENCY_CNY:
                amount = amount
            elif user.currency == CURRENCY_USD:
                amount = amount / 6.2808
            elif user.currency == CURRENCY_THB:
                amount = amount / 0.2016
            elif user.currency == CURRENCY_EUR:
                amount = amount /  7.616
            elif user.currency == CURRENCY_IDR:
                amount = amount / 0.0005
            elif user.currency == CURRENCY_VND:
                amount = amount / 0.0003
            elif user.currency == CURRENCY_MYR:
                amount = amount / 1.6229
            elif user.currency == CURRENCY_TEST or (user.currency == CURRENCY_TTC):
                amount = 20
            else:
                amount = 10
        
        else:
            amount = 0

        # trans = Transaction.objects.create(
        #     transaction_id=trans_id,
        #     user_id=user,
        #     order_id=trans_id,
        #     amount=amount,
        #     currency=user_currency,
        #     transfer_from=from_wallet,
        #     transfer_to="KY",
        #     product=1,
        #     transaction_type=TRANSACTION_TRANSFER,
        #     status=TRAN_PENDING_TYPE
        # )

        order_time = time.strftime("%Y%m%d%H%M%S")

        agent = KY_AGENT
        orderid = agent + str(order_time) + user.username
        param = "s=" + str(operation_type) + "&account=" + user.username + "&orderid=" + orderid + "&money=" + amount

        param = aes_encode(KY_AES_KEY, param)
        param = base64.b64encode(param)
        param = str(param, "utf-8")

        timestamp = get_timestamp()
        key = KY_AGENT + str(timestamp) + KY_MD5_KEY
        key = hashlib.md5(key.encode())
        key = key.hexdigest()

        url = KY_API_URL

        req_param = {}
        req_param["agent"] = agent
        req_param["timestamp"] = str(timestamp)
        req_param["param"] = param
        req_param["key"] = key
        req = urllib.parse.urlencode(req_param)
        url = url + '?' + req

        res = requests.get(url)

        if res.status_code == 200:
            res_data = res.json()
            if res_data['s'] == 102:
                Transaction.objects.create(
                    transaction_id=trans_id,
                    user_id=user,
                    order_id=orderid,
                    amount=amount,
                    currency=user.currency,
                    transfer_from=wallet,
                    transfer_to='ky',
                    product=1,
                    transaction_type=TRANSACTION_DEPOSIT,
                    status=TRAN_SUCCESS_TYPE
                )
            elif res_data['s'] == 103:
                Transaction.objects.create(
                    transaction_id=trans_id,
                    user_id=user,
                    order_id=orderid,
                    amount=amount,
                    currency=user.currency,
                    transfer_from='ky',
                    transfer_to=wallet,
                    product=1,
                    transaction_type=TRANSACTION_DEPOSIT,
                    status=TRAN_SUCCESS_TYPE
                )
            else:
                logger.info("Wrong S type: {}".format(res_data['s']))
        else:
            logger.info("Failed response: {}".format(res.status_code))

    except Exception as e:
        logger.error("Kaiyuan Game fundTransfer error: {}".format(repr(e)))
        return HttpResponse(status=400)


@background(schedule=10)
def generateUrl():
    # Query Bet Order
    timestamp = get_timestamp()

    startTime = get_timestamp() - 300000 # five minutes before now
    endTime = get_timestamp() - 60000 # one minute before now

    param = "s=6" + "&startTime=" + str(startTime) + "&endTime=" + str(endTime)

    param = aes_encode(KY_AES_KEY, param)
    param = base64.b64encode(param)
    param = str(param, "utf-8")

    key = KY_AGENT + str(timestamp) + KY_MD5_KEY
    key = hashlib.md5(key.encode())
    key = key.hexdigest()

    url = KY_RECORD_URL

    req_param = {}
    req_param["agent"] = KY_AGENT
    req_param["timestamp"] = str(timestamp)
    req_param["param"] = param
    req_param["key"] = key

    req = urllib.parse.urlencode(req_param)
    url = url + '?' + req
    res = requests.get(url)

    # print(res.json)


class TestTransferAPI(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            account = data["account"]
            user = CustomUser.objects.get(username=account)
            amount = data["money"]
            from_wallet = data["from_wallet"]
            method = int(data["method"])
            kyTransfer(user, amount, from_wallet, method)
            return HttpResponse(status=200)
        except Exception as e:
            logger.error("Error: {}".format(repr(e)))
            return HttpResponse(status=400)


class KaiyuanAPI(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            s = data["s"]
            # ip = get_client_ip(request)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
        
            # timestamp = lambda: int(round(time.time() * 1000))
            timestamp = get_timestamp()
            agent = KY_AGENT
            s = int(s)

            if s != 6:
                account = data["account"]
                # user = CustomUser.objects.get(username=account)

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
                money = float(data["money"])
                # money = self.fundTransfer(money)
                order_time = time.strftime("%Y%m%d%H%M%S")
                orderid = agent + str(order_time) + account

                param = "s=" + str(s) + "&account=" + account + "&orderid=" + orderid + "&money=" + money

            # Refund
            elif s == 3:
                money = data["money"]
                order_time = time.strftime("%Y%m%d%H%M%S")
                orderid = agent + str(order_time) + account

                param = "s=" + str(s) + "&account=" + account + "&orderid=" + orderid + "&money=" + money
            # Order Query
            elif s == 4:
                order_time = time.strftime("%Y%m%d%H%M%S")
                # orderid = agent + str(order_time) + account
                orderid = data["orderid"]

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
                return HttpResponse(json.dumps(res.json()), content_type='application/json')
            else:
                return HttpResponse("404 Not Found")
        except Exception as e:
            logger.error("Bad Request for Kaiyuan Gaming: {}".format(repr(e)))
            return HttpResponse(status=400)