from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from users.models import  CustomUser
from accounting.models import * 
from django.core.serializers.json import DjangoJSONEncoder
import simplejson as json
from games.models import FGSession, Game, GameBet, GameProvider, Category
from django.db import transaction
import xmltodict
import decimal,re, math
import requests,json
import logging
import random
from utils.constants import *
from datetime import date
from django.utils import timezone
import time, datetime
from time import mktime
import pytz
import utils.aws_helper
import os
import tempfile
import redis
from utils.redisHelper import RedisHelper


logger = logging.getLogger("django")
redis = RedisHelper()


def createUser(user):
    headers = {
        'Pragma': '',
        'Keep-Alive': 'timeout=5, max=100',
        'X_ENTITY_KEY': ENTITY_KEY
    }
    player = "IBETPU_" + user.username.upper()
    admininfo = '/adminname/IBETPCNYUAT/kioskname/IBETPCNYUAT/'
    userinfo = 'firstname/' + user.first_name + '/lastname/' + user.last_name +'/password/' + user.username

    # all the API cert file are local, will update to S3 and change the path before merge.
    try:
        # with tempfile.NamedTemporaryFile(delete=False) as temp:
        pt_key = tempfile.NamedTemporaryFile(delete=False)
        pt_key.write(PTKEY)
        pt_key.flush()    # ensure all data written
        # to get the path/file 
        pt_pem = tempfile.NamedTemporaryFile(delete=False)
        pt_pem.write(PTPEM)
        pt_pem.flush()
        rr = requests.post(PT_BASE_URL + "/player/create/playername/" + player + admininfo + userinfo, headers=headers, cert=(pt_pem.name, pt_key.name))
        # Just check status code here, other error will return to rrdata if 200 and be checked in other func.
        if rr.status_code == 200 :  
            rrdata = rr.json()
            logger.info(rrdata)
        else:
            logger.critical("FATAL__ERROR: in PT create user status code.")
            rrdata = {
                "errorInfo": "status_error:" + rr,
                "errorcode": PT_GENERAL_ERROR
                }

        return rrdata
    finally:
        # delete the file.
        os.unlink(pt_key.name)
        os.unlink(pt_pem.name)


class GetPlayer(APIView):
    """
    check if user exist in PT game before launch. Create a new player if user not exist, otherwise check balance.
    Make sure user has enough balance to play the game, alert to deposit if not.
    status code: 
    0 - player exist, can play the game directly.
    1 - error.
    2 - balance not enough, need alert to deposit.
    3 - create a new user, need alert to deposit.
    """

    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
        username = request.GET['username']
        try:
            user = CustomUser.objects.get(username=username)
        except Exception as e:
            logger.critical("FATAL__ERROR: PT user not exist" + str(e))   
            data = {
                "errorInfo": "PT user not exist",
                "status": PT_GENERAL_ERROR
            }
            return HttpResponse(json.dumps(data),content_type='application/json',status=200)  

        player = "IBETPU_" + username.upper()
        headers = {
            'Pragma': '',
            'Keep-Alive': 'timeout=5, max=100',
            'X_ENTITY_KEY': ENTITY_KEY
        }
        try:
            # with tempfile.NamedTemporaryFile(delete=False) as temp:
            pt_key = tempfile.NamedTemporaryFile(delete=False)
            pt_key.write(PTKEY)
            pt_key.flush()    # ensure all data written
            # to get the path/file 
            pt_pem = tempfile.NamedTemporaryFile(delete=False)
            pt_pem.write(PTPEM)
            pt_pem.flush() 
            rr = requests.post( PT_BASE_URL + "/player/info/playername/" + player, headers=headers, cert=(pt_pem.name, pt_key.name))
            if rr.status_code == 200 :    
                rrdata = rr.json()
                logger.info(rrdata)
            
                # error in get player info.
                if 'errorcode' in rrdata:
                    if rrdata['errorcode'] == 41:
                    # user does not exist, need create a new player.
                    
                        r_create_data = createUser(user)
                        # error in create player.
                        if 'errorcode' in r_create_data:
                            data = {
                                "errorInfo": "cannot create player",
                                "status": PT_GENERAL_ERROR
                            }
                            logger.critical("FATAL__ERROR: cannot create player in get errorcode." )   
                        else:
                        # create user successfully.
                            # print(r_create_data)
                            data = {
                                    "info": "create user successfully",
                                    "status": PT_NEWPLAYER_ALERT
                            }
                            
                    
                    else:
                    # other error in get player info.
                        data = {
                                "errorInfo": rrdata['error'],
                                "status": PT_GENERAL_ERROR
                        }
                        logger.error("Error: PT GAME - " + rrdata['error'])  
                

                else:              
                    #user exist, check balance
                    try:
                        balance = rrdata['result']['BALANCE']
                        bonus = rrdata['result']['BONUSBALANCE']
                        password = rrdata['result']['PASSWORD']
                        ptusername = rrdata['result']['PLAYERNAME']
                        if (float(balance) <= 0 and float(bonus) <= 0):
                            data = {
                                "errorInfo": "balance not enough",
                                "status": PT_BALANCE_ERROR
                            }
                            logger.info("PT GAME: balance not enough." )  
                        else:
                            data = {
                                "status": PT_STATUS_SUCCESS,
                                "info": "user exist, balance enough",
                                "password": password,
                                "playername": ptusername
                            }
                    except Exception as e:
                        data = {
                                "errorInfo": "cannot get balance",
                                "status": PT_GENERAL_ERROR
                        }
                        logger.error("Error: PT GAME - cannot get balance." )  

            else:
                logger.critical("FATAL__ERROR: in PT game get user info status code.")
                data = {
                    "errorInfo": "status_error:" + rr,
                    "status": PT_GENERAL_ERROR
                }

            return HttpResponse(json.dumps(data),content_type='application/json',status=200)  

        finally:
            # delete the file.
            os.unlink(pt_key.name)
            os.unlink(pt_pem.name)

class PTTransferTest(APIView):
    # that's only for test.
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
       
        data = json.loads(request.body)
        
        username = data["user"]
        try:
            user = CustomUser.objects.get(username=username)
        except Exception as e:
            logger.critical("FATAL__ERROR: PT user not exist" + str(e))  
            status = False
            return HttpResponse(status,status=200)
        amount = data["amt"]
        from_wallet = data["from_wallet"]
        method = int(data["method"])
        status = ptTransfer(user, amount, from_wallet, method)
        
        return HttpResponse(status,status=200)
      
def transferHelp(method, user, amount, trans_id, orderid, wallet):
   
    headers = {
                'Pragma': '',
                'Keep-Alive': 'timeout=5, max=100',
                'X_ENTITY_KEY': ENTITY_KEY
            }
    direction = "deposit" if method == 0 else "withdraw"
    
    player = "IBETPU_" + user.username.upper()
    url = PT_BASE_URL + "/player/" + direction + "/playername/" + player + "/amount/" + str(amount) + "/adminname/IBETPCNYUAT"
    
    try:
    # with tempfile.NamedTemporaryFile(delete=False) as temp:
        pt_key = tempfile.NamedTemporaryFile(delete=False)
        pt_key.write(PTKEY)
        pt_key.flush()    # ensure all data written
        # to get the path/file 
        pt_pem = tempfile.NamedTemporaryFile(delete=False)
        pt_pem.write(PTPEM)
        pt_pem.flush() 
       
        rr = requests.post(url, headers=headers, cert=(pt_pem.name, pt_key.name))
        
        if rr.status_code == 200 :    
            rrdata = rr.json()   
            logger.info(rrdata)
            if 'errorcode' in rrdata:
            # error exist.
                logger.error("Error: PT game transfer errorcode.")
                return False
            else:
                # deposit OK.
                if rrdata['result']['result'] == "Deposit OK":
                    
                    Transaction.objects.create(
                        transaction_id=trans_id,
                        user_id=user,
                        order_id=orderid,
                        amount=float(amount),
                        currency=user.currency,
                        transfer_from=wallet,
                        transfer_to='pt',
                        product=GAME_TYPE_GAMES,
                        transaction_type=TRANSACTION_TRANSFER,
                        channel=None,
                        status=TRAN_SUCCESS_TYPE
                    )
                
                    return True
                # withdraw OK.
                elif rrdata['result']['result'] == "Withdraw OK":
                    Transaction.objects.create(
                        transaction_id=trans_id,
                        user_id=user,
                        order_id=orderid,
                        amount=float(amount),
                        currency=user.currency,
                        transfer_from='pt',
                        transfer_to=wallet,
                        product=GAME_TYPE_GAMES,
                        transaction_type=TRANSACTION_TRANSFER,
                        channel=None,
                        status=TRAN_SUCCESS_TYPE
                    )
                    return True

                else:
                
                    return False
        else :
            logger.critical("FATAL__ERROR: PT game transfer status code.")
            return False
    finally:
        # delete the file.
        os.unlink(pt_key.name)
        os.unlink(pt_pem.name)



def ptTransfer(user, amount, wallet, method):
    try:
       
        trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
        user_currency = int(user.currency)
        order_time = time.strftime("%Y%m%d%H%M%S")
        orderid = "pt" + str(order_time) + user.username
        player = "IBETPU_" + user.username.upper()
        headers = {
            'Pragma': '',
            'Keep-Alive': 'timeout=5, max=100',
            'X_ENTITY_KEY': ENTITY_KEY
        }
       
        if user.currency == CURRENCY_CNY:
            amount = amount
        # check if user exist.
        r_create_data = createUser(user)
        # print(r_create_data)
        # error in create player.
        if 'errorcode' in r_create_data:
            # user already exist, transfer directly.
            if r_create_data['errorcode'] == 19:
                
                return transferHelp(method, user, amount, trans_id, orderid, wallet)
            else :
                logger.error("Error: user create error in pt transfer")
                return False
                
        else:
        # create user successfully. transfer then.

            return transferHelp(method, user, amount, trans_id, orderid, wallet)

    except Exception as e:
        return False

def getGMTtime() :
    gmt_time = time.gmtime()
    gmt_time_to_dt = datetime.datetime.fromtimestamp(mktime(gmt_time), tz=pytz.timezone('GMT'))
    # print(gmt_time_to_dt)
    # gmt_plus = gmt_time_to_dt + datetime.timedelta(minutes = -5)
    # print(gmt_plus.strftime('%Y-%m-%d%%20%H:%M:%S'))
    return gmt_time_to_dt.strftime('%Y-%m-%d%%20%H:%M:%S')

      

class GetBetHistory(APIView):

   
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
        headers = {
            'Pragma': '',
            'Keep-Alive': 'timeout=5, max=100',
            'X_ENTITY_KEY': ENTITY_KEY

        }
        try:
            # with tempfile.NamedTemporaryFile(delete=False) as temp:
            pt_key = tempfile.NamedTemporaryFile(delete=False)
            pt_key.write(PTKEY)
            pt_key.flush()    # ensure all data written
            # to get the path/file 
            pt_pem = tempfile.NamedTemporaryFile(delete=False)
            pt_pem.write(PTPEM)
            pt_pem.flush()

            # get time
            REDIS_KEY_PTSTARTTIME_GAMEBET = 'pt_starttime: game_bet'
            ts_from_redis = redis.get_pt_starttime(REDIS_KEY_PTSTARTTIME_GAMEBET)
            if ts_from_redis is None:
                startdate = getGMTtime()
                redis.set_pt_starttime(REDIS_KEY_PTSTARTTIME_GAMEBET, getGMTtime())
                return HttpResponse("PT set first time", status=200)  

            else:
                startdate = ts_from_redis.decode()
                enddate = getGMTtime()
               
                rr = requests.post(PT_BASE_URL + "/game/flow/startdate/" + startdate + "/enddate/" + enddate, headers=headers, cert=(pt_pem.name, pt_key.name))
            
                if rr.status_code == 200 :  
                    rrdata = rr.json()
                    try: 
                        records = rrdata['result']
                        # print(records)
                        provider = GameProvider.objects.get(provider_name=PT_PROVIDER)
                        category = Category.objects.get(name='Games')
                        for record in records:
                            # get user here
                            try:
                                playername = record['PLAYERNAME']
                                user = CustomUser.objects.get(username__iexact=playername.split('_')[1])
                                
                                trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
                                if (float(record['BET']) - float(record['WIN']) > 0) :
                                    outcome = 1 # lose
                                elif (float(record['BET']) - float(record['WIN']) == 0) :
                                    outcome = 2 # Tie/Push
                                else:
                                    outcome = 0 # win
                               
                                resolve = datetime.datetime.strptime(record['GAMEDATE'], '%Y-%m-%d %H:%M:%S')
                                resolve = resolve.replace(tzinfo=pytz.timezone(provider.timezone))
                                resolve = resolve.astimezone(pytz.utc)
                               
                                GameBet.objects.create(
                                        provider=provider,
                                        category=category,
                                        user=user,
                                        user_name=user.username,
                                        amount_wagered=float(record['BET']),
                                        amount_won=float(record['WIN']),
                                        outcome=outcome,
                                        transaction_id=trans_id,
                                        market=ibetCN,
                                        ref_no=record['GAMEID'],
                                        resolved_time=resolve,
                                        other_data={}
                                    )

                            
                            except Exception as e:
                                logger.error("PT cannot get customuser in get record.")
                                return HttpResponse("PT cannot get customuser in bet records.", status=200)  
                        
                        redis.set_pt_starttime(REDIS_KEY_PTSTARTTIME_GAMEBET, getGMTtime())
                        return HttpResponse("PT get {} bet records successfully".format(len(records)), status=200)  
                    except Exception as e:
                        logger.error("PT cannot get bet records")
                        return HttpResponse("PT cannot get bet records.", status=200)  


                else:
                    logger.critical("FATAL__ERROR: PT get bet record status code.")
                    return HttpResponse("PT get bad bet record status code.", status=200)
        finally:
            # delete the file.
            os.unlink(pt_key.name)
            os.unlink(pt_pem.name)
           
        
