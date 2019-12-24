from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from users.models import  CustomUser
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

logger = logging.getLogger("django")


class GetPlayer(APIView):
    """
    status code: 
    0 - player exist, can play the game directly.
    1 - error.
    2 - balance not enough, need alert to deposit.
    3 - create a new user, need alert to deposit.
    """

    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
        username = request.GET['username']
        user = CustomUser.objects.get(username=username)
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
                    player = "IBETPU_" + username.upper()
                    admininfo = '/adminname/IBETPCNYUAT/kioskname/IBETPCNYUAT/'
                    userinfo = 'firstname/' + user.first_name + '/lastname/' + user.last_name 
                    r_create = requests.post(PT_BASE_URL + "/player/create/playername/" + player + admininfo + userinfo, headers=headers, cert=('/Users/jenniehu/Documents/work/Game/PT/fwdplaytechuatibetp/CNY_UAT_FB88/CNY_UAT_FB88.pem','/Users/jenniehu/Documents/work/Game/PT/fwdplaytechuatibetp/CNY_UAT_FB88/CNY_UAT_FB88.key'))
                    r_create_data = r_create.json()
                    # error in create player.
                    if 'errorcode' in r_create_data:
                         data = {
                            "errorInfo": "cannot create player",
                            "status": 1,
                        }
                    else:
                    # create user successfully.
                        # print(r_create_data)
                        data = {
                                "info": "create user successfully",
                                "status": 3,
                        }
                   
                else:
                # other error in get player info.
                    data = {
                            "errorInfo": rrdata['error'],
                            "status": 1,
                    }
            

            else:              
                #user exist, check balance
                try:
                    balance = rrdata['result']['BALANCE']
                    bonus = rrdata['result']['BONUSBALANCE']
                    if (float(balance) <= 0 and float(bonus) <= 0):
                        data = {
                            "errorInfo": "balance not enough",
                            "status": 2,

                        }
                    else:
                        data = {
                            "status": 0,
                            "info": "user exist, balance enough"
                        }
                except Exception as e:
                    data = {
                            "errorInfo": "cannot get balance",
                            "status": 1,
                    }

        else:
            logger.error(rr)
            data = {
                "errorInfo": "status_error:" + rr,
                "status": 1,
            }

        return HttpResponse(json.dumps(data),content_type='application/json',status=200)  
       

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
        # Deposit
        if method == 0:
            operation_type = 2
            if user.currency == CURRENCY_CNY:
                amount = amount
            
            url = PT_BASE_URL + "/player/deposit/playername/" + player + "/amount/" + amount + "/adminname/IBETPCNYUAT/externaltranid/" + trans_id
            
            rr = requests.post(url, headers=headers, cert=('/Users/jenniehu/Documents/work/Game/PT/fwdplaytechuatibetp/CNY_UAT_FB88/CNY_UAT_FB88.pem','/Users/jenniehu/Documents/work/Game/PT/fwdplaytechuatibetp/CNY_UAT_FB88/CNY_UAT_FB88.key'))
        
            if rr.status_code == 200 :    
                rrdata = rr.json()
                try:
                    if rrdata['result']['result'] == "Deposit OK":
                        Transaction.objects.create(
                            transaction_id=trans_id,
                            user_id=user,
                            order_id=orderid,
                            amount=amount,
                            currency=user.currency,
                            transfer_from=wallet,
                            transfer_to='pt',
                            product=1,
                            transaction_type=TRANSACTION_TRANSFER,
                            status=TRAN_SUCCESS_TYPE
                        )
                        return True

                    else:
                        return False

                except Exception as e:
                    logger.info("PT Deposit Not Success")
                    return False
            else:
                logger.info("Failed response: {}".format(res.status_code))
                return False
                

        # withdraw
        elif method == 1:
            operation_type = 3
            if user.currency == CURRENCY_CNY:
                amount = amount

            url = PT_BASE_URL + "/player/withdraw/playername/" + player + "/amount/" + amount + "/adminname/IBETPCNYUAT/externaltranid/" + trans_id        
            rr = requests.post(url, headers=headers, cert=('/Users/jenniehu/Documents/work/Game/PT/fwdplaytechuatibetp/CNY_UAT_FB88/CNY_UAT_FB88.pem','/Users/jenniehu/Documents/work/Game/PT/fwdplaytechuatibetp/CNY_UAT_FB88/CNY_UAT_FB88.key'))
        
            if rr.status_code == 200 :    
                rrdata = rr.json()
                try:
                    if rrdata['result']['result'] == "Withdraw OK":
                        Transaction.objects.create(
                            transaction_id=trans_id,
                            user_id=user,
                            order_id=orderid,
                            amount=amount,
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

                except Exception as e:
                    logger.info("PT Withdraw Not Success")
                    return False

            else:
                logger.info("Failed response: {}".format(res.status_code))
                return False

            
        else:
            amount = 0


    except Exception as e:
        logger.error("Playtech Game fundTransfer error: {}".format(repr(e)))
        return False


class GetBetHistory(APIView):
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
