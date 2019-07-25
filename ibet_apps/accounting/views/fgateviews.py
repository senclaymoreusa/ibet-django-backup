from django.shortcuts import render
from django.http import HttpResponse
from django.views import View, generic
from users.models import CustomUser
from ..models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from utils.constants import *
#from djauth.third_party_keys import *
from rest_framework import generics
from ..serializers import fgateChargeCardSerialize
from django.conf import settings
import requests,json
import logging, time, struct, hashlib, xml.etree.ElementTree as ET
from time import sleep
from des import DesKey
import base64,hmac
from time import gmtime, strftime, strptime
import datetime, pytz
from decimal import *
import xmltodict
logger = logging.getLogger("django")
def generateHash(key, message):
    hash = hmac.new(key, msg=message, digestmod=hashlib.sha256)
    #hash.hexdigest()
    return hash.hexdigest()

class chargeCard(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = fgateChargeCardSerialize
    permission_classes = [AllowAny, ]
    def post(self, request, *args, **kwargs):
        user = self.request.POST.get("user")
        pin = self.request.POST.get("pin")
        serial = self.request.POST.get("serial")
        order_id = "ibet" +strftime("%Y%m%d%H%M%S", gmtime())
        message = bytes(order_id + pin + serial + FGATE_TYPE, 'utf-8')
        secret = bytes(FGATE_PARTNERKEY, 'utf-8')
        token = generateHash(secret, message)
        #headers = {'Content-type': 'multipart/form-data'}
        data = {
            "pin": pin,
            "serial": serial,
            "tran_id": order_id,
            "type": FGATE_TYPE,
            "token": token,
            "partner_id": FGATE_PARTNERID,
        }
        print(data)
        delay = kwargs.get("delay", 5)
        success = False
        #retry
        for x in range(3):
            r = requests.post(FGATE_URL,  data=data)
            rdata = r.json()
            print(rdata)
            if r.status_code == 200:
                success = True
                break
            if r.status_code == 400 or r.status_code == 401:
                success = True
                # Handle error
                logger.info("Failed to complete a request for getDepositMethod...")
                logger.error(rdata)
                return Response(rdata)
            if r.status_code == 500:
                print("Request failed {} time(s)'.format(x+1)")
                print("Waiting for %s seconds before retrying again")
                sleep(delay)
        if rdata["error_code"] == '00' and rdata["status"] == 1:
            create = Transaction.objects.create(
                order_id=order_id,
                amount=rdata["amount"],
                user_id=CustomUser.objects.get(username=user),
                method= 'Fgo',
                transaction_type=0,
                channel=0,
            )
        else:
            return Response(rdata)
        return  Response(rdata)



