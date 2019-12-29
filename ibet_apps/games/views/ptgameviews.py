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
import datetime
from datetime import date
from django.utils import timezone
import time

logger = logging.getLogger("django")



def createUser(user):
    headers = {
        'Pragma': '',
        'Keep-Alive': 'timeout=5, max=100',
        'X_ENTITY_KEY': ENTITY_KEY
    }
    player = "IBETPU_" + user.username.upper()
    admininfo = '/adminname/IBETPCNYUAT/kioskname/IBETPCNYUAT/'
    userinfo = 'firstname/' + user.first_name + '/lastname/' + user.last_name 

    # all the API cert file are local, will update to S3 and change the path before merge.
    rr = requests.post(PT_BASE_URL + "/player/create/playername/" + player + admininfo + userinfo, headers=headers, cert=('/Users/jenniehu/Documents/work/Game/PT/fwdplaytechuatibetp/CNY_UAT_FB88/CNY_UAT_FB88.pem','/Users/jenniehu/Documents/work/Game/PT/fwdplaytechuatibetp/CNY_UAT_FB88/CNY_UAT_FB88.key'))
    # Just check status code here, other error will return to rrdata if 200 and be checked in other func.
    if rr.status_code == 200 :  
        rrdata = rr.json()
    else:
        logger.error(rr)
        rrdata = {
            "errorInfo": "status_error:" + rr,
            "errorcode": PT_GENERAL_ERROR
            }

    return rrdata


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
            logger.error("PT user not exist" + str(e))   
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
       
        rr = requests.post( PT_BASE_URL + "/player/info/playername/" + player, headers=headers, cert=('/Users/jenniehu/Documents/work/Game/PT/fwdplaytechuatibetp/CNY_UAT_FB88/CNY_UAT_FB88.pem','/Users/jenniehu/Documents/work/Game/PT/fwdplaytechuatibetp/CNY_UAT_FB88/CNY_UAT_FB88.key'))
        
        if rr.status_code == 200 :    
            rrdata = rr.json()
            # print(rrdata)
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
            

            else:              
                #user exist, check balance
                try:
                    balance = rrdata['result']['BALANCE']
                    bonus = rrdata['result']['BONUSBALANCE']
                    if (float(balance) <= 0 and float(bonus) <= 0):
                        data = {
                            "errorInfo": "balance not enough",
                            "status": PT_BALANCE_ERROR
,

                        }
                    else:
                        data = {
                            "status": PT_STATUS_SUCCESS,
                            "info": "user exist, balance enough"
                        }
                except Exception as e:
                    data = {
                            "errorInfo": "cannot get balance",
                            "status": PT_GENERAL_ERROR
                    }

        else:
            logger.error(rr)
            data = {
                "errorInfo": "status_error:" + rr,
                "status": PT_GENERAL_ERROR
            }

        return HttpResponse(json.dumps(data),content_type='application/json',status=200)  

class PTTransferTest(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
       
        data = json.loads(request.body)
        username = data["user"]
        user = CustomUser.objects.get(username=username)
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

    url = PT_BASE_URL + "/player/" + direction + "/playername/" + player + "/amount/" + amount + "/adminname/IBETPCNYUAT"
    
    rr = requests.post(url, headers=headers, cert=('/Users/jenniehu/Documents/work/Game/PT/fwdplaytechuatibetp/CNY_UAT_FB88/CNY_UAT_FB88.pem','/Users/jenniehu/Documents/work/Game/PT/fwdplaytechuatibetp/CNY_UAT_FB88/CNY_UAT_FB88.key'))
    if rr.status_code == 200 :    
        rrdata = rr.json()   
        if 'errorcode' in rrdata:
        # error exist.
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
                    product=1,
                    transaction_type=TRANSACTION_TRANSFER,
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
                    product=1,
                    transaction_type=TRANSACTION_TRANSFER,
                    status=TRAN_SUCCESS_TYPE
                )
                return True

            else:
               
                return False
    else :
        logger.info("Failed response: {}".format(rr.status_code))
        return False




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
                logger.error("user create error in pt transfer")
                return False
                
        else:
        # create user successfully. transfer then.

            return transferHelp(method, user, amount, trans_id, orderid, wallet)

    except Exception as e:
        return False

      

class GetBetHistory(APIView):

    # other work still needed....
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
        headers = {
            'Pragma': '',
            'Keep-Alive': 'timeout=5, max=100',
            'X_ENTITY_KEY': ENTITY_KEY

        }
        rr = requests.get(PT_BASE_URL + "/customreport/getdata/reportname/PlayerGames", headers=headers, cert=('/Users/jenniehu/Documents/work/Game/PT/fwdplaytechuatibetp/CNY_UAT_FB88/CNY_UAT_FB88.pem','/Users/jenniehu/Documents/work/Game/PT/fwdplaytechuatibetp/CNY_UAT_FB88/CNY_UAT_FB88.key'))
        
        
        if rr.status_code == 200 :    
               
            rrdata = rr.json()
            data = {
                "test" : None
            }
           
        return HttpResponse(json.dumps(rrdata),content_type='application/json',status=200)
