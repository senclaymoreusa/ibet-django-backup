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

class PTtest(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        headers = {
            'Pragma': '',
            'Keep-Alive': 'timeout=5, max=100',
            'X_ENTITY_KEY': '19969fca479e990e5eec11bc1db6cd5f711132a52eb99df9a02587c11ee2d9472a2cf1b3ad437d1d2f147b8923a200e70e670c1c06920c12280c9603f70e9fe2'

        }
        # rr = requests.post("https://kioskpublicapi.luckydragon88.com/entity/list", headers=headers)
        
        # if rr.status_code == 200 :    
               
        #     rrdata = rr.json()
        t = request.GET['t']
        data = {
            "test" : None
        }
        if 'test' in data:
            test = {
                "test": t
            }
        else:
            test = {
                "test": "hoho"
            }
           
        return HttpResponse(json.dumps(test),content_type='application/json',status=200)

class GetPlayer(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
        username = request.GET['username']
        user = CustomUser.objects.get(username=username)
        headers = {
            'Pragma': '',
            'Keep-Alive': 'timeout=5, max=100',
            'X_ENTITY_KEY': '19969fca479e990e5eec11bc1db6cd5f711132a52eb99df9a02587c11ee2d9472a2cf1b3ad437d1d2f147b8923a200e70e670c1c06920c12280c9603f70e9fe2'
        }
       
        rr = requests.post("https://kioskpublicapi.luckydragon88.com/player/info/playername/" + username, headers=headers)
        
        if rr.status_code == 200 :    
            rrdata = rr.json()
            if 'errorcode' in rrdata:
                if rrdata['errorcode'] == '41':
                    #user does not exist, create player.
                    admininfo = 'adminname/IBETPCNYUAT/kioskname/IBETPCNYUAT/'
                    userinfo = 'firstname/' + user.firstname + '/lastname/' + user.lastname 
                    rr = requests.post("https://kioskpublicapi.luckydragon88.com/player/create/playername" + username + admininfo + userinfo, headers=headers)
                    #error check

                #elif other error

            else:              
                #check balance
                print("test")

           
           
        return HttpResponse(json.dumps(rrdata),content_type='application/json',status=200)

def ptTransfer(user, amount, wallet, method):
    try:
        trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
        user_currency = int(user.currency)
        order_time = time.strftime("%Y%m%d%H%M%S")
        orderid = "pt" + str(order_time) + user.username
        headers = {
            'Pragma': '',
            'Keep-Alive': 'timeout=5, max=100',
            'X_ENTITY_KEY': '19969fca479e990e5eec11bc1db6cd5f711132a52eb99df9a02587c11ee2d9472a2cf1b3ad437d1d2f147b8923a200e70e670c1c06920c12280c9603f70e9fe2'
        }
        # Deposit
        if method == 0:
            operation_type = 2
            if user.currency == CURRENCY_CNY:
                amount = amount
            
            url = "https://kioskpublicapi.luckydragon88.com/player/deposit/playername/" + user.username + "/amount/" + amount + "/adminname/IBETPCNYUAT/externaltranid/" + trans_id
            
            rr = requests.post(url, headers=headers)
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

            url = "https://kioskpublicapi.luckydragon88.com/player/withdraw/playername/" + user.username + "/amount/" + amount + "/adminname/IBETPCNYUAT/externaltranid/" + trans_id        
            rr = requests.post(url, headers=headers)
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
            'X_ENTITY_KEY': '19969fca479e990e5eec11bc1db6cd5f711132a52eb99df9a02587c11ee2d9472a2cf1b3ad437d1d2f147b8923a200e70e670c1c06920c12280c9603f70e9fe2'

        }
        rr = requests.get("https://kioskpublicapi.luckydragon88.com/entity/list", headers=headers)
        
        if rr.status_code == 200 :    
               
            rrdata = rr.json()
            data = {
                "test" : None
            }
           
        return HttpResponse(json.dumps(rrdata),content_type='application/json',status=200)
