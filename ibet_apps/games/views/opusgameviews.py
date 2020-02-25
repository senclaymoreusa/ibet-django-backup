from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from users.models import CustomUser
from  games.models import *
import hashlib,logging,hmac,requests,xmltodict,random,string
import xml.etree.ElementTree as ET
from time import gmtime, strftime, strptime
from rest_framework.authtoken.models import Token
from django.core.exceptions import  ObjectDoesNotExist
from decimal import Decimal
from time import sleep
import datetime
from datetime import date
from utils.constants import *
from django.utils import timezone
import random
from rest_framework.decorators import api_view, permission_classes
logger = logging.getLogger('django')

def transfer(user, amount, fund_wallet, direction):
    #trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))  
    headers =  {'Content-Type': 'application/json'}
    delay = 5
    success = False

    if direction == 'IN':
        key = "TransferIn"
    elif direction == 'OUT':
        key = "TransferOut"
    data = {
        "userId": user.pk,
        "transferBalance": amount,
        "currency": user.currency
    }
    for x in range(3):
        r = requests.post(OPUS_API_URL + key, headers=headers, json=data)
        rdata = r.text
        if "referenceId" in rdata:
            return CODE_SUCCESS
        else:
            return ERROR_CODE_FAIL
        

# class Test(View):
#     def get(self, request, *args, **kwargs):
#         user = CustomUser.objects.get(pk=16)
        
#         #response = createMember(user, 13, "2")
#         #response = transfer(user, 100, 'main', 'IN')
#         response = transfer(user, 100, 'main', 'OUT')
#         return HttpResponse(response)

class Login(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        userid = request.POST["userid"]
        language = request.POST["language"]
        try:
            user = CustomUser.objects.get(pk=userid)
        except ObjectDoesNotExist:
            logger.error("user does not exist in opus login api")
            Response({"error":"The user does not exist in opus login api"},status=status.HTTP_400_BAD_REQUEST) 
        headers =  {'Content-Type': 'application/json'}
        delay = 5
        success = False

        data = {
            "userId": user.pk,
            "userName": user.username,
            "language": language,
            "currency": user.currency
        }
        for x in range(3):
            r = requests.post(OPUS_API_URL + 'login', headers=headers, json=data)
            rdata = r.json()
            #print(rdata)
            if rdata["result"]["url"]:
                url = rdata["result"]["url"]
                #print(url)
                return Response({"URL": url},status=status.HTTP_200_OK)
            else:
                logger.info({"error": "we cannot get the login url for OPUS"})
                return Response({"error": "we cannot get the login url for OPUS"},status=status.HTTP_400_BAD_REQUEST)

def getBalance(user):
    userid = user.pk
    delay = 5
    success = False
    for x in range(3):
        r = requests.get(OPUS_API_URL + 'balance/' + str(userid))
        rdata = r.json()
        #print(rdata)
        if r.status_code == 200:
            success = True
            break
        else:
            logger.info("Request failed {} time(s)'.format(x+1)")
            logger.info("Waiting for %s seconds before retrying again")
            sleep(delay)
    if not success:
        logger.error("OPUS::Cannot find the data for OPUS check user balance.")
        balance = 0.0
        return json.dumps({"balance":balance})
    
    try:
        balance = rdata['result'] 
        
        if balance == None:
            balance = 0.00
        else: 
            balance = float(balance)
        
        return json.dumps({"balance":balance})
    except:
        balance = 0.00
        logger.error("OPUS::Cannot find the data for OPUS check user balance.")
        return json.dumps({"error": "Cannot find the data for OPUS check user balance.", "balance":balance})

class Test(View):
    def get(self, request, *args, **kwargs):
        user = CustomUser.objects.get(pk=16)
        
        response = getBalance(user)
        #response = transfer(user, 100, 'main', 'IN')
        #response = transfer(user, 100, 'main', 'OUT')
        return HttpResponse(response)

