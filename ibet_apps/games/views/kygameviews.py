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

def aes_encode(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    # cipher_chunks.append()
    cipher_text = cipher.encrypt(pad(data))
    return cipher_text


def get_timestamp():
    return int(round(time.time() * 1000))


"""
:param param: parameters to be encrypted
:param is_api: True -> API_URL, False -> RECORD_URL
:returns: URL
"""
def generateUrl(param, is_api):
    param = aes_encode(KY_AES_KEY, param)
    param = base64.b64encode(param)
    param = str(param, "utf-8")

    timestamp = get_timestamp()
    key = KY_AGENT + str(timestamp) + KY_MD5_KEY
    key = hashlib.md5(key.encode())
    key = key.hexdigest()

    if is_api:
        url = KY_API_URL
    else:
        url = KY_RECORD_URL

    req_param = {}
    req_param["agent"] = KY_AGENT
    req_param["timestamp"] = str(timestamp)
    req_param["param"] = param
    req_param["key"] = key
    req = urllib.parse.urlencode(req_param)
    url = url + '?' + req

    return url


class KyBets(View):
    def post(self, request, *args, **kwargs):
        try:
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

            data = res.json()

            if data['d']['code'] == 0:
                count = int(data['d']['count'])
                record_list = data['d']['list']

                provider = GameProvider.objects.get(provider_name=KY_PROVIDER)
                category = Category.objects.get(name='Table Games')

                game_id = record_list['GameID']
                accounts = record_list['Accounts']
                # server_id = record_list['ServerID']
                # kind_id = record_list['KindID']
                # table_id = record_list['TableID']
                cell_score = record_list['CellScore']
                profit = record_list['Profit']
                revenue = record_list['Revenue']

                for i in range(0, count):
                    username = accounts[i][6:]
                    user = CustomUser.objects.get(username=username)

                    trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

                    GameBet.objects.create(
                        provider=provider,
                        category=category,
                        user=user,
                        user_name=user.username,
                        amount_wagered=decimal.Decimal(cell_score[i]),
                        amount_won=decimal.Decimal(profit[i]) - decimal.Decimal(revenue[i]),
                        transaction_id=trans_id,
                        market=ibetCN,
                        ref_no=game_id[i],
                        resolved_time=timezone.now(),
                        other_data=json.dumps({"game_id": game_id[i]})
                    )

                return HttpResponse("You have add {} records".format(count), status=200)
            else:
                return HttpResponse("No record at this time", status=200)
        except Exception as e:
            logger.error("Kaiyuan Game Background Task Error: {}".format(repr(e)))
            return HttpResponse("Kaiyuan Game Background Task Error", status=400)


# @background(schedule=10)
'''
def getBets():
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

    data = res.json()

    if data['d']['code'] == 0:
        count = int(data['d']['count'])
        record_list = data['d']['list']

        provider = GameProvider.objects.get_or_create(provider_name=KY_PROVIDER, type=GAME_TYPE_TABLE_GAMES, market='letouCN, letouTH, letouVN')
        category = Category.objects.get_or_create(name='Table Games', notes="Kaiyuan Chess")

        game_id = record_list['GameID']
        accounts = record_list['Accounts']
        # server_id = record_list['ServerID']
        # kind_id = record_list['KindID']
        # table_id = record_list['TableID']
        cell_score = record_list['CellScore']
        profit = record_list['Profit']
        revenue = record_list['Revenue']

        for i in range(0, count):
            username = accounts[i][6:]
            user = CustomUser.objects.get(username=username)

            trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

            GameBet.objects.create(
                provider=provider[0],
                category=category[0],
                user=user,
                user_name=user.username,
                amount_wagered=decimal.Decimal(cell_score[i]),
                amount_won=decimal.Decimal(profit[i]) - decimal.Decimal(revenue[i]),
                transaction_id=trans_id,
                market=ibetCN,
                ref_no=game_id[i],
                resolved_time=timezone.now()
            )
    else:
        pass
    # print(res.json)
'''

"""
:param user: CustomUser object
:param amount: amount of money to transfer
:param wallet: wallet to deposit/withdraw
:param method: 0 -> Deposit, 1 -> Withdraw
:returns: IPv4 address
"""
def kyTransfer(user, amount, wallet, method):
    try:
        trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
        # trans_id = user.username + time.strftime("%Y%m%d%H%M%S") + str(random.randint(0,10000000))
        user_currency = int(user.currency)

        # Deposit
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

        # withdraw
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

        # agent = KY_AGENT
        orderid = KY_AGENT + str(order_time) + user.username
        param = "s=" + str(operation_type) + "&account=" + user.username + "&orderid=" + orderid + "&money=" + str(amount)

        url = generateUrl(param, True)
        
        res = requests.get(url)
        res_data = res.json()
        if res.status_code == 200:
            if res_data['s'] == 102:
                if res_data['d']['code'] == 0:
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
                    return True
                else:
                    logger.info("Deposit Not Success {}".format(res_data['d']))
                    return False
            elif res_data['s'] == 103:
                if res_data['d']['code'] == 0:
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
                    return True
                else:
                    logger.info("Withdraw Not Success {}".format(res_data['d']))
                    return False
            else:
                logger.info("Wrong S type: {}".format(res_data['s']))
                return False
        else:
            logger.info("Failed response: {}".format(res.status_code))
            return False

    except Exception as e:
        logger.error("Kaiyuan Game fundTransfer error: {}".format(repr(e)))
        return False


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


class TestGetRecord(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            if data['d']['code'] == 0:
                count = int(data['d']['count'])
                record_list = data['d']['list']

                provider = GameProvider.objects.get(provider_name=KY_PROVIDER)
                category = Category.objects.get(name='Table Games')

                game_id = record_list['GameID']
                accounts = record_list['Accounts']
                # server_id = record_list['ServerID']
                # kind_id = record_list['KindID']
                # table_id = record_list['TableID']
                cell_score = record_list['CellScore']
                profit = record_list['Profit']
                revenue = record_list['Revenue']

                for i in range(0, count):
                    username = accounts[i][6:]
                    user = CustomUser.objects.get(username=username)

                    trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

                    GameBet.objects.create(
                        provider=provider,
                        category=category,
                        user=user,
                        user_name=user.username,
                        amount_wagered=decimal.Decimal(cell_score[i]),
                        amount_won=decimal.Decimal(profit[i]) - decimal.Decimal(revenue[i]),
                        transaction_id=trans_id,
                        market=ibetCN,
                        ref_no=game_id[i],
                        resolved_time=timezone.now(),
                        other_data=json.dumps({"game_id": game_id[i]})
                    )
            
            return HttpResponse(status=200)
        except Exception as e:
            logger.error("KY Scheduled Task Error: {}".format(repr(e)))
            return HttpResponse(status=400)
            


class KaiyuanAPI(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            operation_type = data["s"]
            # ip = get_client_ip(request)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
        
            timestamp = get_timestamp()
            agent = KY_AGENT
            operation_type = int(operation_type)

            if operation_type != 6:
                account = data["account"]
                # user = CustomUser.objects.get(username=account)

            # Login
            if operation_type == 0:
                money = data["money"]
                order_time = time.strftime("%Y%m%d%H%M%S")
                orderid = agent + str(order_time) + account
                linecode = KY_LINE_CODE_1
                kind_id = data["KindID"]

                param = "s=" + str(operation_type) + "&account=" + account + "&money=" + money + "&orderid=" + orderid + "&ip=" + ip + "&lineCode=" + linecode + "&KindID=" + kind_id + "&lang=zh-CN"
            # Get Balance
            elif operation_type == 1:
                param = "s=" + str(operation_type) + "&account=" + account
            # Change Balance
            elif operation_type == 2:
                money = data["money"]
                order_time = time.strftime("%Y%m%d%H%M%S")
                orderid = agent + str(order_time) + account

                param = "s=" + str(operation_type) + "&account=" + account + "&orderid=" + orderid + "&money=" + money
            # Refund
            elif operation_type == 3:
                money = data["money"]
                order_time = time.strftime("%Y%m%d%H%M%S")
                orderid = agent + str(order_time) + account

                param = "s=" + str(operation_type) + "&account=" + account + "&orderid=" + orderid + "&money=" + money
            # Order Query
            elif operation_type == 4:
                # order_time = time.strftime("%Y%m%d%H%M%S")
                # orderid = agent + str(order_time) + account
                orderid = data["orderid"]

                param = "s=" + str(operation_type) + "&orderid=" + orderid
            # Query The Player's Online Status
            elif operation_type == 5:
                param = "s=" + str(operation_type) + "&account=" + account
            # Query Bet Order
            elif operation_type == 6:
                startTime = data["startTime"]
                endTime = data["endTime"]

                param = "s=" + str(operation_type) + "&startTime=" + startTime + "&endTime=" + endTime
            # Query The Player's Total Points
            elif operation_type == 7:
                param = "s=" + str(operation_type) + "&account=" + account
            # Kick Player off
            elif operation_type == 8:
                param = "s=" + str(operation_type) + "&account=" + account
            else:
                return HttpResponse("Undefined request type")
            
            
            # kind_id = '0' # game lobby
            # "&KindID=" + kind_id

            if operation_type != 6:
                url = generateUrl(param, True)
            else:
                url = generateUrl(param, False)
            
            res = requests.get(url)
            if res.status_code == 200:
                res_data = res.json()
                return HttpResponse(json.dumps(res.json()), content_type='application/json')
            else:
                return HttpResponse("404 Not Found")
        except Exception as e:
            logger.error("Bad Request for Kaiyuan Gaming: {}".format(repr(e)))
            return HttpResponse(status=400)