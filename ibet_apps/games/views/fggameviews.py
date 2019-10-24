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

class SessionCheck(APIView):
    permission_classes = (AllowAny, )
    def get(self, request, *args, **kwargs):
        sessionKey = request.GET['sessionKey']
        rr = requests.get(FG_SESSION_CHECK ,params={
            "sessionKey": sessionKey
        })
        if rr.status_code == 200:
            rr = rr.text    
           
        else:
            # Handle error
            logger.info(rr)
        return HttpResponse(rr) 

class FGLogin(APIView):

    permission_classes = (AllowAny, )
    def get(self, request, *args, **kwargs):
        pk = request.GET['pk']
        user = CustomUser.objects.get(pk=pk)
        currency = user.currency
        uuid = 'fg'+ user.username
        rr = requests.get(FG_URL, params={
            "brandId": BRANDID,
            "brandPassword": BRAND_PASSWORD, 
            "currency": currency,
            "uuid": uuid,
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
                    FGSession.objects.create(user=pk,session_key=sessionKey,party_id=partyId, uuid=uuid)   
                

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


class GameLaunch(APIView):

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        gameId = request.GET['gameId']
        try:
            sessionKey = request.GET['sessionKey']
            rr = requests.get(LAUNCH_URL, params={
                "platform": PLATFORM,
                "brandId": BRANDID,
                "gameId" : gameId,
                "playForReal": "true",
                "lang" : "en",
                "sessionKey" : sessionKey
            })
            

        except:

            rr = requests.get(LAUNCH_URL, params={
                "platform": PLATFORM,
                "brandId": BRANDID,
                "gameId" : gameId,
                "playForReal": "false",
                "lang" : "en"
            })
        
        rr = rr.text    
        return HttpResponse(rr)

class GetAccountDetail(APIView):

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        seq = request.GET['seq']
        callerId = request.GET['callerId']
        callerPassword = request.GET['callerPassword']
        uuid = request.GET['uuid']
        omegaSessionKey = request.GET['omegaSessionKey']

        try:
            fguser = FGSession.objects.get(session_key=omegaSessionKey)
            user = CustomUser.objects.get(username=fguser.user)

            response = {
            "seq" : seq,
            "partyId" : fguser.party_id ,
            "omegaSessionKey" : omegaSessionKey,
            "message" : "null",
            "errorCode" : "null",
            "uuid" : uuid,
            "realBalance" : round(float(user.main_wallet),2),
            "bonusBalance" : round(float(user.bonus_wallet),2),
            "loginName" : user.username,
            "firstName" :  user.first_name ,
            "lastName" : user.last_name,
            "currency" : user.currency,
            "email" : user.email,
            "country" : user.country,
            "language" : "ZH",
            "birthDate" : user.date_of_birth
    
        }
        except:
            response = {
                "errorcode" : "PLAYER_NOT_FOUND",
                "message" : "no user found"
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
        try:
            fguser = FGSession.objects.get(session_key=omegaSessionKey)
            user = CustomUser.objects.get(username=fguser.user)

            response = {
                "seq" : seq,
                "partyId" : fguser.party_id ,
                "omegaSessionKey" : omegaSessionKey,
                "message" : "null",
                "errorCode" : "null",
                "realBalance" : round(float(user.main_wallet),2),
                "bonusBalance" : round(float(user.bonus_wallet),2),
            
            }
        except:
            response = {
                "errorcode" : "PLAYER_NOT_FOUND",
                "message" : "no user found"
            }

        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json',status=200)

class ProcessTransaction(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        seq = request.GET['seq']
        callerId = request.GET['callerId']
        callerPassword = request.GET['callerPassword']
        uuid = request.GET['uuid']
        #omegaSessionKey = request.GET['omegaSessionKey']
        currency = request.GET["currency"]
        amount = request.GET["amount"]
        tranType = request.GET["tranType"]
        timestamp = request.GET["timestamp"]
        providerTranId = request.GET["providerTranId"]
        platformCode = request.GET["platformCode"]
        gameTranId = request.GET["gameTranId"]
        #
        #
        try:
            fguser = FGSession.objects.get(uuid=uuid)
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
                    "alreadyProcessed" : "false",
                    "realBalance" : round(float(user.main_wallet),2),
                    "bonusBalance" : round(float(user.bonus_wallet),2), 
                    "realAmount" : amount,
                    "bonusAmount" : 0,

                }

            if tranType == "GAME_WIN" :
                
                response = {
                    "seq" : seq,
                    "partyId" : fguser.party_id ,
                    "currency" : currency,
                    "transactionId" : 1,
                    "tranType" : tranType,
                    "alreaduProcessed" : "false",
                    "realBalance" :  round(float(user.main_wallet),2), 
                    "bonusBalance" : round(float(user.bonus_wallet),2),
                    "realAmount" : amount,
                    "bonusAmount" : 0,

                }

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
                    "realBalance" : round(float(user.main_wallet),2) ,
                    "bonusBalance" : round(float(user.bonus_wallet),2),
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
                    "realBalance" : round(float(user.main_wallet),2) ,
                    "bonusBalance" : round(float(user.bonus_wallet),2),
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
                    "realBalance" : round(float(user.main_wallet),2) ,
                    "bonusBalance" : round(float(user.bonus_wallet),2),
                    "realAmount" : amount,
                    "bonusAmount" : 0,

                }  
        except:
            response = {
                "errorcode" : "PLAYER_NOT_FOUND",
                "message" : "no user found"
            }

        return HttpResponse(json.dumps(response,cls=DjangoJSONEncoder), content_type='application/json',status=200)



