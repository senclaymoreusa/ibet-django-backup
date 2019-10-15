from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from users.models import  CustomUser
from django.core.serializers.json import DjangoJSONEncoder
import simplejson as json
from games.models import FGGame
import xmltodict
import decimal
import requests,json
import logging

logger = logging.getLogger("django")


class FGLogin(APIView):

    permission_classes = (AllowAny, )
    def get(self, request, *args, **kwargs):
        username = request.GET['username']
       # user = CustomUser.objects.get(username=username)
        
       
        brandId = '524'
        brandPassword = 'Flow6refg'
        currency = 'CNY'
        fgurl = 'https://lsl.omegasys.eu/ps/ssw/login'
        #print(url)

        rr = requests.get(fgurl, params={
            "brandId": brandId,
            "brandPassword": brandPassword, 
            "currency": currency,
            "uuid": 'fg' + username,
            "loginName": username
            })
                  
        rrdata = rr.json()
        # logger.info(rrdata)
        try:
            sessionKey = rrdata["sessionKey"]
            partyId = rrdata["partyId"]
    
            data = rrdata
            try:
                user = FGGame.objects.get(user_name =username)
                user.session_key=sessionKey
                user.save()
            except:
                
                FGGame.objects.create(user_name=username,session_key=sessionKey,party_id=partyId)   
            

        except:

            data = {
                    "status": rrdata["status"],
                    "message": rrdata["message"]
                    }

       
        return HttpResponse(json.dumps(data),content_type='application/json',status=200)




class GetAccountDetail(APIView):

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        seq = request.GET['seq']
        callerId = request.GET['callerId']
        callerPassword = request.GET['callerPassword']
        uuid = request.GET['uuid']
        omegaSessionKey = request.GET['omegaSessionKey']
        user = CustomUser.objects.get(username=callerId)
        fguser = FGGame.objects.get(user_name=callerId)


        #print(decimal.Decimal(user.main_wallet))
        response = {
            "seq" : seq,
            "partyId" : fguser.party_id ,
            "omegaSessionKey" : omegaSessionKey,
            "message" : "null",
            "errorCode" : "null",
            "uuid" : uuid,
            "realBalance" : decimal.Decimal(user.main_wallet) ,
            "bonusBalance" : decimal.Decimal(user.bonus_wallet),
            "loginName" : user.username,
            "firstName" :  user.first_name ,
            "lastName" : user.last_name,
            "currency" : user.currency,
            "email" : user.email,
            "country" : user.country,
            "language" : "ZH",
            "birthDate" : user.date_of_birth
    
        }
        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json',status=200)

class GetBalance(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        seq = request.GET['seq']
        callerId = request.GET['callerId']
        callerPassword = request.GET['callerPassword']
        uuid = request.GET['uuid']
        omegaSessionKey = request.GET['omegaSessionKey']
        currency = request.GET["currency"]
        #gameInfoId = request.GET["gameInfoId"]
        user = CustomUser.objects.get(username=callerId)
        fguser = FGGame.objects.get(user_name=callerId)

        response = {
            "seq" : seq,
            "partyId" : fguser.party_id ,
            "omegaSessionKey" : omegaSessionKey,
            "message" : "null",
            "errorCode" : "null",
            "realBalance" : decimal.Decimal(user.main_wallet),
            "bonusBalance" : decimal.Decimal(user.bonus_wallet)
        
        }
        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json',status=200)

class ProcessTransaction(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        seq = request.GET['seq']
        callerId = request.GET['callerId']
        callerPassword = request.GET['callerPassword']
        uuid = request.GET['uuid']
        omegaSessionKey = request.GET['omegaSessionKey']
        currency = request.GET["currency"]
        amount = request.GET["amount"]
        tranType = request.GET["tranType"]
        timestamp = request.GET["timestamp"]
        providerTranId = request.GET["providerTranId"]
        platformCode = request.GET["platformCode"]
        gameTranId = request.GET["gameTranId"]
        gameInfoId = request.GET["gameInfoId"]
        gameId = request.GET["gameId"]
        isFinal = request.GET["isFinal"]
        user = CustomUser.objects.get(username=callerId)

        if tranType == "GAME_BET" :
            response = {
                "seq" : seq,
                "omegaSessionKey" : omegaSessionKey,
                "partyId" : 1,
                "currency" : currency,
                "transactionId" : 1,
                "tranType" : tranType,
                "alreaduProcessed" : false,
                "realBalance" : user.main_wallet ,
                "bonusBalance" : user.bonus_wallet,
                "realAmount" : amount,
                "bonusAmount" : 0,

            }

        if tranType == "GAME_WIN" :
            response = {
                "seq" : seq,
                "partyId" : 1,
                "currency" : currency,
                "transactionId" : 1,
                "tranType" : tranType,
                "alreaduProcessed" : false,
                "realBalance" : user.main_wallet ,
                "bonusBalance" : user.bonus_wallet,
                "realAmount" : amount,
                "bonusAmount" : 0,

            }

        if tranType == "PLTFRM_BON" :
            response = {
                "seq" : seq,
                "omegaSessionKey" : omegaSessionKey,
                "tranType" : tranType,
                "gameInfoId" : gameInfoId,
                "partyId" : 1,
                "currency" : currency,
                "transactionId" : 1,
                "errorCode" : "null",
                "message" : "null",
                "alreaduProcessed" : false,
                "realBalance" : user.main_wallet ,
                "bonusBalance" : user.bonus_wallet,
                "realAmount" : amount,
                "bonusAmount" : 0,

            }    

        if tranType == "ROLLBACK" :
            response = {
                "seq" : seq,
                "tranType" : tranType,
                "partyId" : 1,
                "currency" : currency,
                "transactionId" : 1,
                "alreaduProcessed" : false,
                "realBalance" : user.main_wallet ,
                "bonusBalance" : user.bonus_wallet,
                "realAmount" : amount,
                "bonusAmount" : 0,

            }  

        if tranType == "END_GAME" :
            response = {
                "seq" : seq,
                "omegaSessionKey" : omegaSessionKey,
                "tranType" : tranType,
                "partyId" : 1,
                "currency" : currency,
                "alreaduProcessed" : false,
                "realBalance" : user.main_wallet ,
                "bonusBalance" : user.bonus_wallet,
                "realAmount" : amount,
                "bonusAmount" : 0,

            }      
        return HttpResponse(json.dumps(response), content_type='application/json',status=200)



