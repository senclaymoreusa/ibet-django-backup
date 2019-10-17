from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from users.models import  CustomUser
from django.core.serializers.json import DjangoJSONEncoder
import simplejson as json
from games.models import FGSession
import xmltodict
import decimal
import requests,json
import logging
from utils.constants import *

logger = logging.getLogger("django")


class FGLogin(APIView):

    permission_classes = (AllowAny, )
    def get(self, request, *args, **kwargs):
        pk = request.GET['pk']
        user = CustomUser.objects.get(pk=pk)
        currency = user.currency

        rr = requests.get(FG_URL, params={
            "brandId": BRANDID,
            "brandPassword": BRAND_PASSWORD, 
            "currency": currency,
            "uuid": 'fg'+ user.username,
            "loginName": user.username
            })
        
        if rr.status_code == 200 :    
               
            rrdata = rr.json()
            # logger.info(rrdata)
            try:
                sessionKey = rrdata["sessionKey"]
                partyId = rrdata["partyId"]
                data = rrdata
                
                try:
                    user = FGSession.objects.get(user=pk)
                    user.session_key=sessionKey
                    user.save()
                except:
                    
                    pk = CustomUser.objects.get(pk=pk)        
                    FGSession.objects.create(user=pk,session_key=sessionKey,party_id=partyId)   
                

            except:

                data = {
                        "status": rrdata["status"],
                        "message": rrdata["message"]
                        }

        
            return HttpResponse(json.dumps(data),content_type='application/json',status=200)
        else:
            # Handle error
            logger.info(rr)
            return Response(rr)




class GetAccountDetail(APIView):

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        seq = request.GET['seq']
        callerId = request.GET['callerId']
        callerPassword = request.GET['callerPassword']
        uuid = request.GET['uuid']
        omegaSessionKey = request.GET['omegaSessionKey']
        fguser = FGSession.objects.get(session_key=omegaSessionKey)
        user = CustomUser.objects.get(username=fguser.user)

        response = {
            "seq" : seq,
            "partyId" : fguser.party_id ,
            "omegaSessionKey" : omegaSessionKey,
            "message" : "null",
            "errorCode" : "null",
            "uuid" : uuid,
            "realBalance" : decimal.Decimal(user.main_wallet).quantize(decimal.Decimal('0.00')) ,
            "bonusBalance" : decimal.Decimal(user.bonus_wallet).quantize(decimal.Decimal('0.00')),
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
        fguser = FGSession.objects.get(session_key=omegaSessionKey)
        user = CustomUser.objects.get(username=fguser.user)

        response = {
            "seq" : seq,
            "partyId" : fguser.party_id ,
            "omegaSessionKey" : omegaSessionKey,
            "message" : "null",
            "errorCode" : "null",
            "realBalance" : decimal.Decimal(user.main_wallet).quantize(decimal.Decimal('0.00')),
            "bonusBalance" : decimal.Decimal(user.bonus_wallet).quantize(decimal.Decimal('0.00')),
        
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
        #
        #
        fguser = FGSession.objects.get(session_key=omegaSessionKey)
        user = CustomUser.objects.get(username=fguser)

        if tranType == "GAME_BET" :
            omegaSessionKey = request.GET['omegaSessionKey']
            gameId = request.GET["gameId"]
            response = {
                "seq" : seq,
                "omegaSessionKey" : omegaSessionKey,
                "partyId" : fguser.party_id ,
                "currency" : currency,
                "transactionId" : 1,
                "tranType" : tranType,
                "alreaduProcessed" : "false",
                "realBalance" : decimal.Decimal(user.main_wallet).quantize(decimal.Decimal('0.00')) ,
                "bonusBalance" : decimal.Decimal(user.bonus_wallet).quantize(decimal.Decimal('0.00')),
                "realAmount" : amount,
                "bonusAmount" : 0,

            }

        # if tranType == "GAME_WIN" :
            
        #     response = {
        #         "seq" : seq,
        #         "partyId" : fguser.party_id ,
        #         "currency" : currency,
        #         "transactionId" : 1,
        #         "tranType" : tranType,
        #         "alreaduProcessed" : "false",
        #         "realBalance" :  decimal.Decimal(user.main_wallet) ,
        #         "bonusBalance" : decimal.Decimal(user.bonus_wallet),
        #         "realAmount" : amount,
        #         "bonusAmount" : 0,

        #     }

        if tranType == "PLTFRM_BON" :
            omegaSessionKey = request.GET['omegaSessionKey']
            gameInfoId = request.GET["gameInfoId"]
            isFinal = request.GET["isFinal"]
            response = {
                "seq" : seq,
                "omegaSessionKey" : omegaSessionKey,
                "tranType" : tranType,
                "gameInfoId" : gameInfoId,
                "partyId" : fguser.party_id ,
                "currency" : currency,
                "transactionId" : 1,
                "errorCode" : "null",
                "message" : "null",
                "alreaduProcessed" : "false",
                "realBalance" : decimal.Decimal(user.main_wallet).quantize(decimal.Decimal('0.00')) ,
                "bonusBalance" : decimal.Decimal(user.bonus_wallet).quantize(decimal.Decimal('0.00')),
                "realAmount" : amount,
                "bonusAmount" : 0,

            }    

        if tranType == "ROLLBACK" :
            gameId = request.GET["gameId"]
            response = {
                "seq" : seq,
                "tranType" : tranType,
                "partyId" : fguser.party_id ,
                "currency" : currency,
                "transactionId" : 1,
                "alreaduProcessed" : "false",
                "realBalance" : decimal.Decimal(user.main_wallet).quantize(decimal.Decimal('0.00')) ,
                "bonusBalance" : decimal.Decimal(user.bonus_wallet).quantize(decimal.Decimal('0.00')),
                "realAmount" : amount,
                "bonusAmount" : 0,

            }  

        if tranType == "END_GAME" :
            omegaSessionKey = request.GET['omegaSessionKey']
            gameInfoId = request.GET["gameInfoId"]
            isFinal = request.GET["isFinal"]
            response = {
                "seq" : seq,
                "omegaSessionKey" : omegaSessionKey,
                "tranType" : tranType,
                "partyId" : fguser.party_id ,
                "currency" : currency,
                "alreaduProcessed" : "false",
                "realBalance" : decimal.Decimal(user.main_wallet).quantize(decimal.Decimal('0.00')) ,
                "bonusBalance" : decimal.Decimal(user.bonus_wallet).quantize(decimal.Decimal('0.00')),
                "realAmount" : amount,
                "bonusAmount" : 0,

            }      
        return HttpResponse(json.dumps(response,cls=DjangoJSONEncoder), content_type='application/json',status=200)



