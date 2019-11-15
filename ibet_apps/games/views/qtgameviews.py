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


#path('api/qt/getBalance', sagameviews.RegUserInfo.as_view(), name="sa_register_user"),

def verifySession(request, playerId, gameId=None):
    
    sessionid = request.META.get('Wallet-Session')
    passkey = request.META.get('Pass-Key')



def getBalance(request, playerid, gameid=None):
    
    sessionid = request.META.get('Wallet-Session')
    passkey = request.META.get('Pass-Key')
    
    try:
        qtuser = UserSession.objects.get(session_key=sessionid)
        user = CustomUser.objects.get(username=playerid)
        
        response = {
            "balance" : math.floor(float(user.main_wallet * 100)) / 100,
            "currency" : user.currency,
        }
        
        code = 200
    except Exception as e:
        msg = ''
        if passkey != QT_PASS_KEY:
            code = 401
            errcode = 'LOGIN_FAILED'
            msg = 'The given pass-key is incorrect.'
        else: 
            code = 400
            errcode = 'REQUEST_DECLINED'
            msg = 'Request could not be processed'
        
        response = {
            "code": errcode,
            "message": msg
        }
        
        
        logger.error("cannot find user", e)
    
    return HttpResponse(response, content_type='application/json', status=code)