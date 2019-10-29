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
import random
from utils.constants import *

logger = logging.getLogger("django")

class SessionCheck(APIView):
    permission_classes = (AllowAny, )
    def get(self, request, *args, **kwargs):
        """
        The session check API is for checking whether the session key is alive.
        """
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
        """
        FGLogin - generate new session key and update in database.
        """
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
        """
        GetAccountDetail - return the user info.
        """

        seq = request.GET['seq']
        callerId = request.GET['callerId']
        callerPassword = request.GET['callerPassword']
        uuid = request.GET['uuid']
        omegaSessionKey = request.GET['omegaSessionKey']

        try:
            fguser = FGSession.objects.get(uuid=uuid)
            user = CustomUser.objects.get(username=fguser.user)

            response = {
            "seq" : seq,
            "partyId" : fguser.party_id ,
            "omegaSessionKey" : omegaSessionKey,
            "message" : None,
            "errorCode" : None,
            "uuid" : uuid,
            "realBalance" : round(float(user.main_wallet),2),
            "bonusBalance" : round(float(user.bonus_wallet),2),
            "loginName" : user.username,
            "firstName" :  user.first_name ,
            "lastName" : user.last_name,
            "currency" : user.currency,
            "email" : user.email,
            "country" : user.country,
            "city": user.city,
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
        """
        GetBalance - return the user account balance to provider.
        """
        seq = request.GET['seq']
        callerId = request.GET['callerId']
        callerPassword = request.GET['callerPassword']
        uuid = request.GET['uuid']
        omegaSessionKey = request.GET['omegaSessionKey']
        currency = request.GET["currency"]
        try:
            fguser = FGSession.objects.get(uuid=uuid)
            user = CustomUser.objects.get(username=fguser.user)

            response = {
                "seq" : seq,
                "partyId" : fguser.party_id ,
                "omegaSessionKey" : omegaSessionKey,
                "message" : None,
                "errorCode" : None,
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

        """
        ProcessTransaction - process in game bet, game win, bonus, rollback and end game.
        """

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
        #transactionId = ""
        
        try:
            fguser = FGSession.objects.get(uuid=uuid)
            user = CustomUser.objects.get(username=fguser.user)
          

        except:
            response = {
                "errorcode" : "PLAYER_NOT_FOUND",
                "message" : "no user found"
            }

        if tranType == "GAME_BET" :
                omegaSessionKey = request.GET['omegaSessionKey']
                gameInfoId = request.GET["gameInfoId"]

                user.main_wallet = user.main_wallet + decimal.Decimal(amount)
                user.save()
                response = {
                    "seq" : seq,
                    "omegaSessionKey" : omegaSessionKey,
                    "partyId" : fguser.party_id ,
                    "currency" : currency,
                    "transactionId" : 2019 + random.randint(1000,9999) ,
                    "tranType" : tranType,
                    "gameInfoId" : gameInfoId,
                    "alreadyProcessed" : False,
                    "realBalance" : round(float(user.main_wallet),2) ,
                    "bonusBalance" : round(float(user.bonus_wallet),2), 
                    "realAmount" : round(float(amount),2),
                    "bonusAmount" : 0.00,
                    "errorCode" : None,
                    "message" : None

                }
               

        elif tranType == "GAME_WIN" :
                omegaSessionKey = request.GET['omegaSessionKey']
                gameInfoId = request.GET["gameInfoId"]
                #isFinal = request.GET["isFinal"]
                user.main_wallet = user.main_wallet + decimal.Decimal(amount)
                user.save()
                response = {
                    "seq" : seq,
                    "omegaSessionKey" : omegaSessionKey,
                    "partyId" : fguser.party_id ,
                    "gameInfoId" : gameInfoId,
                    "currency" : currency,
                    "transactionId" : 2019 + random.randint(1000,9999),
                    "tranType" : tranType,
                    "alreadyProcessed" : False,
                    "realBalance" :  round(float(user.main_wallet),2), 
                    "bonusBalance" : round(float(user.bonus_wallet),2),
                    "realAmount" : round(float(amount),2),
                    "bonusAmount" : 0.00,
                    "errorCode" : None,
                    "message" : None

                }
                

        elif tranType == "PLTFRM_BON" :
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
                    "transactionId" : 2019 + random.randint(1000,9999),
                    "errorCode" : None,
                    "message" : None,
                    "alreadyProcessed" : isFinal,
                    "realBalance" : round(float(user.main_wallet),2) ,
                    "bonusBalance" : round(float(user.bonus_wallet),2),
                    "realAmount" : round(float(amount),2),
                    "bonusAmount" : 0.00,

                }    

        elif tranType == "ROLLBACK" :
                gameInfoId = request.GET["gameInfoId"]
                omegaSessionKey = request.GET['omegaSessionKey']
                response = {
                    "seq" : seq,
                    "tranType" : tranType,
                    "partyId" : fguser.party_id ,
                    "currency" : currency,
                    "transactionId" : 2019 + random.randint(1000,9999) ,
                    "omegaSessionKey" : omegaSessionKey,
                    "alreadyProcessed" : True,
                    "realBalance" : round(float(user.main_wallet),2) ,
                    "bonusBalance" : round(float(user.bonus_wallet),2),
                    "realAmount" : round(float(amount),2),
                    "bonusAmount" : 0.00,
                    "errorCode" : None,
                    "message" : None
                }  

        elif tranType == "END_GAME" :
                omegaSessionKey = request.GET['omegaSessionKey']
                gameInfoId = request.GET["gameInfoId"]
                isFinal = request.GET["isFinal"]
                response = {
                    "seq" : seq,
                    "omegaSessionKey" : omegaSessionKey,
                    "tranType" : tranType,
                    "partyId" : fguser.party_id ,
                    "currency" : currency,
                    "alreadyProcessed" : False,
                    "realBalance" : round(float(user.main_wallet),2) ,
                    "bonusBalance" : round(float(user.bonus_wallet),2),
                    "realAmount" : round(float(amount),2),
                    "bonusAmount" : 0.00,

                }  
       

        return HttpResponse(json.dumps(response,cls=DjangoJSONEncoder), content_type='application/json',status=200)



