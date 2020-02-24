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
    trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))  
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
        r = requests.post(OPUS_API_URL + key, headers=headers, data=(data))
        rdata = r.text
        # print(rdata)
        # print(r.status_code)
        # if r.status_code == 200:
        #     success = True
        #     break
        # elif r.status_code == 204:
        #     success = True
        #     # Handle error
        #     logger.info("Failed to complete a request for opus transfer...")
        #     logger.error(rdata)
        #     return ERROR_CODE_FAIL
        # elif r.status_code == 500:
        #     logger.info("Request failed {} time(s)'.format(x+1)")
        #     logger.info("Waiting for %s seconds before retrying again")
        #     sleep(delay)
        # if not success:
        #     logger.critical("OPUS:: Unable to request fund transfer.")
        #     return ERROR_CODE_FAIL
        # return CODE_SUCCESS
        return HttpResponse(rdata)

class Test(View):
    def get(self, request, *args, **kwargs):
        user = CustomUser.objects.get(pk=16)
        
        #response = createMember(user, 13, "2")
        response = transfer(user, 100, 'main', 'IN')
        return HttpResponse(response)
    
