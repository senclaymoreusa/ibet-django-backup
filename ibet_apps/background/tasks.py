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
import random
from django.core.exceptions import  ObjectDoesNotExist
from users.models import CustomUser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings

@background(schedule=10)
def demo_task():
    print ('THIS IS ONLY A TEST')



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
    
    
 