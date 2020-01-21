import datetime, pytz, base64, hmac, requests, json, logging, time, struct, hashlib, xmltodict, xml.etree.ElementTree as ET

from django.shortcuts import render
from django.http import HttpResponse
from django.views import View, generic
from users.models import CustomUser

from accounting.models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from accounting.serializers import fgateChargeCardSerialize

from rest_framework import parsers, renderers, status,generics
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes

from utils.constants import *
from des import DesKey
from time import gmtime, strftime, strptime, sleep
from decimal import *
from django.utils import timezone
from users.views.helper import *
from django.utils.translation import ugettext_lazy as _
logger = logging.getLogger("django")
def generateHash(key, message):
    hash = hmac.new(key, msg=message, digestmod=hashlib.sha256)
    return hash.hexdigest()

class chargeCard(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = fgateChargeCardSerialize
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        user = self.request.POST.get("user")
        pin = self.request.POST.get("pin")
        serial = self.request.POST.get("serial")
        transaction_id = "ibet" + strftime("%Y%m%d%H%M%S", gmtime())
        message = bytes(transaction_id + pin + serial + FGATE_TYPE, 'utf-8')
        secret = bytes(FGATE_PARTNERKEY, 'utf-8')
        token = generateHash(secret, message)
        if checkUserBlock(CustomUser.objects.get(username=user)):
            errorMessage = _('The current user is blocked!')
            data = {
                "errorCode": ERROR_CODE_BLOCK,
                "errorMsg": {
                    "detail": [errorMessage]
                }
            }
            return Response(data)
        data = {
            "pin": pin,
            "serial": serial,
            "tran_id": transaction_id,
            "type": FGATE_TYPE,
            "token": token,
            "partner_id": FGATE_PARTNERID,
        }
        delay = kwargs.get("delay", 5)

        success = False
        # retry
        for x in range(3):
            r = requests.post(FGATE_URL,  data=data)
            rdata = r.json()
            logger.info(rdata)
            if r.status_code == 200:
                success = True
                break
            if r.status_code == 400 or r.status_code == 401:
                success = True
                # Handle error
                logger.info("Failed to complete a request for Fgo Deposit...")
                logger.info(rdata)
                return Response(rdata)
            if r.status_code == 500:
                logger.info("Request failed {} time(s)'.format(x+1)")
                logger.info("Waiting for %s seconds before retrying again")
                sleep(delay)
        if rdata["error_code"] == '00' and rdata["status"] == 1:
            create = Transaction.objects.create(
                transaction_id=transaction_id,
                amount=rdata["amount"],
                user_id=CustomUser.objects.get(username=user),
                method='Fgo',
                transaction_type=0,
                channel=8,
                status=0,
                request_time=timezone.now(),
                arrive_time=timezone.now(),
            )
        else:
            return Response(rdata)
        return Response(rdata)



