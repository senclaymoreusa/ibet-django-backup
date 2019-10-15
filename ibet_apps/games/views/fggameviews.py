from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from users.models import  CustomUser
import simplejson as json
import xmltodict
import decimal

class FGLogin(APIView):
    def get(self, request, *args, **kwargs):
        username = request.GET('username')
        user = CustomUser.objects.get(username=username)
        print(user)
        print("hhhh")
        brandId = '524',
        brandPassword = 'Flow6refg',
        currency = 'CNY',
        fgurl = 'https://lsl.omegasys.eu/ps/ssw/login'
        #print(url)

        rr = requests.get(fg, params={
            "brandId": brandId,
            "brandPassword": brandPassword, 
            "currency": currency,
            "uuid": user.pk,
            "loginName": username
            })
                  
        rrdata = rr.text
        # logger.info(rrdata)
        return HttpResponse(rrdata)




class GetAccountDetail(APIView):

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        seq = request.GET['seq']
        callerId = request.GET['callerId']
        callerPassword = request.GET['callerPassword']
        uuid = request.GET['uuid']
        omegaSessionKey = request.GET['omegaSessionKey']
        user = CustomUser.objects.get(username=callerId)


        response = {
            "seq" : seq,
            "partyId" : 1,
            "omegaSessionKey" : omegaSessionKey,
            "message" : "null",
            "errorCode" : "null",
            "uuid" : uuid,
            "realBalance" : user.main_wallet ,
            "bonusBalance" : user. bonus_wallet,
            "loginName" : user.username,
            "firstName" :  user.first_name ,
            "lastName" : user.last_name,
            "currency" : user.currency,
            "email" : user.email,
            "country" : user.country,
            "language" : "ZH",
            "birthDate" : user.date_of_birth,
    
        }
        return HttpResponse(json.dumps(response), content_type='application/json',status=200)

class GetBalance(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        seq = request.GET['seq']
        callerId = request.GET['callerId']
        callerPassword = request.GET['callerPassword']
        uuid = request.GET['uuid']
        omegaSessionKey = request.GET['omegaSessionKey']
        currency = request.GET["currency"]
        gameInfoId = request.GET["gameInfoId"]
        user = CustomUser.objects.get(username=callerId)


        response = {
            "seq" : seq,
            "partyId" : 1,
            "omegaSessionKey" : omegaSessionKey,
            "message" : "null",
            "errorCode" : "null",
            "realBalance" : user.main_wallet ,
            "bonusBalance" : user. bonus_wallet
        
        }
        return HttpResponse(json.dumps(response), content_type='application/json',status=200)

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



