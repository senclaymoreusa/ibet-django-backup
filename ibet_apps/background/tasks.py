from background_task import background
from  games.models import *
from django.db import DatabaseError, transaction
import redis
from utils.redisClient import RedisClient
from utils.redisHelper import RedisHelper
import datetime
from datetime import date
from django.utils import timezone
from time import gmtime, strftime, strptime
import random, logging
from django.core.exceptions import  ObjectDoesNotExist
from users.models import CustomUser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
import time
import urllib
import requests
from utils.aws_helper import getThirdPartyKeys
from Crypto.Cipher import AES
from games.helper import *

logger = logging.getLogger('django')

# @background(schedule=10)
# def demo_task():
#     print ('THIS IS ONLY A TEST')

# connect AWS S3
third_party_keys = getThirdPartyKeys("ibet-admin-eudev", "config/gamesKeys.json")
KY_AES_KEY = third_party_keys["KAIYUAN"]["DESKEY"]
KY_MD5_KEY = third_party_keys["KAIYUAN"]["MD5KEY"]

@transaction.atomic
@background(schedule=5) 
def onebook_getBetDetail():
    try:
        PROVIDER = GameProvider.objects.get(provider_name=ONEBOOK_PROVIDER)
    except ObjectDoesNotExist:
        PROVIDER = GameProvider.objects.create(provider_name=ONEBOOK_PROVIDER,
                                        type=0,
                                        market='China',
                                        notes='2004')
        logger.error("PROVIDER AND/OR CATEGORY RELATIONS DO NOT EXIST.")
    headers =  {'Content-Type': 'application/x-www-form-urlencoded'}
    delay = 2
    success = False
    version_key = PROVIDER.notes
    onebook_run = "run"
    try:
        r = RedisClient().connect()
        redis = RedisHelper()
        # print(redis.check_onebook_bet_details(onebook_run))
        if redis.check_onebook_bet_details(onebook_run) is False: #if the key is not existed in redis
            redis.set_onebook_bet_details(onebook_run)  #insert the key to redis
            while(True):
                r = requests.post(ONEBOOK_API_URL + "GetBetDetail/", headers=headers, data={
                    "vendor_id": ONEBOOK_VENDORID,
                    "version_key": version_key,
                })
                rdata = r.json()
                logger.info(rdata)
                # print(rdata)
                version_key = rdata["Data"]["last_version_key"]        
                
                updates = GameProvider.objects.get(provider_name=ONEBOOK_PROVIDER)
                
                updates.notes = version_key
                updates.save()
                    
                if  "BetDetails" in rdata['Data']:
                    
                    # logger.info(rdata["Data"]["BetDetails"])
                    for i in range(len(rdata["Data"]["BetDetails"])):
                        username = str(rdata["Data"]["BetDetails"][i]["vendor_member_id"]).split('_')[0]
                        #print(username)
                        try:
                            cate = Category.objects.get(name='SPORTS')
                        except:
                            cate = Category.objects.create(name='SPORTS')
                            logger.info("create new game category.")
                        trans_id = rdata["Data"]["BetDetails"][i]["trans_id"]
                        user = CustomUser.objects.get(username=username)
                        transid = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
                        if rdata["Data"]["BetDetails"][i]["settlement_time"] == None:
                            # print("onebook")
                            GameBet.objects.create(provider=PROVIDER,
                                                        category=cate,
                                                        username=user,
                                                        transaction_id=transid,
                                                        odds=rdata["Data"]["BetDetails"][i]["odds"],
                                                        amount_wagered=rdata["Data"]["BetDetails"][i]["stake"],
                                                        currency=convertCurrency[rdata["Data"]["BetDetails"][i]["currency"]],
                                                        bet_type=rdata["Data"]["BetDetails"][i]["bet_type"],
                                                        amount_won=rdata["Data"]["BetDetails"][i]["winlost_amount"],
                                                        outcome=outcomeConversion[rdata["Data"]["BetDetails"][i]["ticket_status"]],
                                                        ref_no=trans_id,
                                                        market=ibetCN,
                                                        other_data=rdata,
                                                        )
                        else:
                            
                            resolve = datetime.datetime.strptime(rdata["Data"]["BetDetails"][i]["settlement_time"], '%Y-%m-%dT%H:%M:%S.%f')
                                
                            GameBet.objects.get_or_create(provider=PROVIDER,
                                                        category=cate,
                                                        transaction_id=transid,
                                                        username=user,
                                                        odds=rdata["Data"]["BetDetails"][i]["odds"],
                                                        amount_wagered=rdata["Data"]["BetDetails"][i]["stake"],
                                                        currency=convertCurrency[rdata["Data"]["BetDetails"][i]["currency"]],
                                                        bet_type=rdata["Data"]["BetDetails"][i]["bet_type"],
                                                        amount_won=rdata["Data"]["BetDetails"][i]["winlost_amount"],
                                                        outcome=outcomeConversion[rdata["Data"]["BetDetails"][i]["ticket_status"]],
                                                        resolved_time=utcToLocalDatetime(resolve),
                                                        ref_no=trans_id,
                                                        market=ibetCN,
                                                        other_data=rdata,
                                                        )
                    
                    sleep(delay)    
                else:
                    logger.info("BetDetails is not existed.")
                    break
            redis.remove_onebook_bet_details(onebook_run)  #remove the key from redis
            # print(redis.check_onebook_bet_details(onebook_run))        
            return rdata
        else:
            logger.info("skip running this time.")
    except:
        logger.error("There is something woring with Redis connection.")



BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

def aes_encode(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    # cipher_chunks.append()
    cipher_text = cipher.encrypt(pad(data))
    return cipher_text

def get_timestamp():
    return int(round(time.time() * 1000))    

@background(schedule=10)
def kaiyuan_getBets():
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

        provider = GameProvider.objects.get_or_create(provider_name=KY_PROVIDER, type=1, market=ibetCN)
        category = Category.objects.get_or_create(name='Chess', notes="Kaiyuan Chess")

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
                username=user,
                amount_wagered=decimal.Decimal(cell_score[i]),
                amount_won=decimal.Decimal(profit[i]) - decimal.Decimal(revenue[i]),
                transaction_id=trans_id,
                market=ibetCN,
                ref_no=game_id[i]
            )
    else:
        pass
    # print(res.json)
 