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

logger = logging.getLogger("django")

class GetAllGame(APIView):
    permission_classes = (AllowAny, )
    def get(self, request, *args, **kwargs):
        provider = request.GET['provider']
        game = Game.objects.filter(provider=provider)     
        return JsonResponse({
        'game': list(game.values())
    })
        #return JsonResponse(json.dumps(data),content_type='application/json',status=200)



class GetSessionKey(APIView):
    permission_classes = (AllowAny, )
    def get(self, request, *args, **kwargs):
        pk = request.GET['pk']
        try:
            user = FGSession.objects.get(user=pk)
            rr = requests.get(FG_SESSION_CHECK ,params={
                "sessionKey": user.session_key
            })
            if rr.status_code == 200:
                data = {
                    "sessionKey" : user.session_key,
                    "alive" :  rr.json()['alive']
                    
                }
                # rr = rr.text  
                
            else:
                # Handle error
                logger.info(rr)

               
        except Exception as e:
            data = {
                "sessionKey" : None
            }
            logger.error("no sessionKey", e)
        return HttpResponse(json.dumps(data),content_type='application/json',status=200)

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
            "currency": CURRENCY_CHOICES[currency][1],
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
            "realBalance" : math.floor(float(user.main_wallet * 100)) / 100,
            "bonusBalance" : math.floor(float(user.bonus_wallet * 100)) / 100,
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
        except Exception as e:
            response = {
                "errorcode" : "PLAYER_NOT_FOUND",
                "message" : "no user found"
            }
            logger.error("cannot find user", e)

        
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
                "realBalance" : math.floor(float(user.main_wallet * 100)) / 100,
               
                "bonusBalance" : math.floor(float(user.bonus_wallet * 100)) / 100,
            
            }
        except Exception as e:
            response = {
                "errorcode" : "PLAYER_NOT_FOUND",
                "message" : "no user found"
            }
            logger.error("cannot find user", e)

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
                wallet = user.main_wallet + decimal.Decimal(amount)
                if (wallet > 0):
                    with transaction.atomic():
                        user.main_wallet = wallet
                        user.save()
                        transactionId = re.sub("[^0-9]", "", timestamp)
                        GameBet.objects.get_or_create(provider=GameProvider.objects.get(provider_name="FG"),
                                                        category=Category.objects.get(name='Slots'),
                                                        username=user,
                                                        amount_wagered=-float(amount),
                                                        currency=currency,
                                                        amount_won=0.00,
                                                        market=ibetCN,
                                                        transaction_id=transactionId
                                                        )
                    response = {
                        "seq" : seq,
                        "omegaSessionKey" : omegaSessionKey,
                        "partyId" : fguser.party_id ,
                        "currency" : currency,
                        "transactionId" : transactionId,
                        "tranType" : tranType,
                        "gameInfoId" : gameInfoId,
                        "alreadyProcessed" : False,
                        "realBalance" : math.floor(float(user.main_wallet * 100)) / 100 ,
                        "bonusBalance" : math.floor(float(user.bonus_wallet * 100)) / 100, 
                        "realAmount" : float(amount),
                        "bonusAmount" : 0.00,
                        "errorCode" : None,
                        "message" : None

                    }
                else :
                    response = {
                        "errorcode" : "INSUFFICIENT_FUNDS",
                        "message" : "user balance is not enough"

                    }
                    logger.error("user balance is not enough")
               

        elif tranType == "GAME_WIN" :
                omegaSessionKey = request.GET['omegaSessionKey']
                gameInfoId = request.GET["gameInfoId"]
                #isFinal = request.GET["isFinal"]
                wallet = user.main_wallet + decimal.Decimal(amount)
                if (wallet > 0):
                    with transaction.atomic():
                        user.main_wallet = user.main_wallet + decimal.Decimal(amount)
                        user.save()
                        transactionId = re.sub("[^0-9]", "", timestamp)
                        GameBet.objects.get_or_create(provider=GameProvider.objects.get(provider_name="FG"),
                                                        category=Category.objects.get(name='Slots'),
                                                        username=user,
                                                        amount_wagered=0.00,
                                                        currency=currency,
                                                        amount_won=float(amount),
                                                        market=ibetCN,
                                                        transaction_id=transactionId
                                                        )
                    response = {
                        "seq" : seq,
                        "omegaSessionKey" : omegaSessionKey,
                        "partyId" : fguser.party_id ,
                        "gameInfoId" : gameInfoId,
                        "currency" : currency,
                        "transactionId" : transactionId,
                        "tranType" : tranType,
                        "alreadyProcessed" : False,
                        "realBalance" :  math.floor(float(user.main_wallet * 100)) / 100, 
                        "bonusBalance" : math.floor(float(user.bonus_wallet * 100)) / 100,
                        "realAmount" : amount,
                        "bonusAmount" : 0.00,
                        "errorCode" : None,
                        "message" : None

                    }

                else :
                    response = {
                        "errorcode" : "INSUFFICIENT_FUNDS",
                        "message" : "user balance is not enough"

                    }
                    logger.error("user balance is not enough")
                    

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
                    "transactionId" : re.sub("[^0-9]", "", timestamp),
                    "errorCode" : None,
                    "message" : None,
                    "alreadyProcessed" : isFinal,
                    "realBalance" : math.floor(float(user.main_wallet * 100)) / 100 ,
                    "bonusBalance" : math.floor(float(user.bonus_wallet * 100)) / 100,
                    "realAmount" : amount,
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
                    "transactionId" : re.sub("[^0-9]", "", timestamp) ,
                    "omegaSessionKey" : omegaSessionKey,
                    "alreadyProcessed" : True,
                    "realBalance" : math.floor(float(user.main_wallet * 100)) / 100  ,
                    "bonusBalance" : math.floor(float(user.bonus_wallet * 100)) / 100,
                    "realAmount" : amount,
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
                    "realBalance" : math.floor(float(user.main_wallet * 100)) / 100 ,
                    "bonusBalance" : math.floor(float(user.bonus_wallet * 100)) / 100,
                    "realAmount" : amount,
                    "bonusAmount" : 0.00,

                }  
       

        return HttpResponse(json.dumps(response,cls=DjangoJSONEncoder), content_type='application/json',status=200)



