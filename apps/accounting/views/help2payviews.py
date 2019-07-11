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
from ..serializers import help2payDepositSerialize
from django.conf import settings
import requests,json
import logging, time, struct, hashlib, xml.etree.ElementTree as ET
from time import sleep
from des import DesKey
import base64
from time import gmtime, strftime, strptime
import datetime, pytz
from decimal import *
import xmltodict
logger = logging.getLogger("django")
currencyConversion = {
    '0': 'CNY',
    '1': 'USD',
    '2': 'THB',
    '3': 'IDR',
    '4': 'HKD',
    '5': 'AUD',
    '6':'THB',
    '7': 'MYR',
    '8': 'VND',
    '9': 'MMK',
    '10': 'XBT',
}
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def MD5(code):
    res = hashlib.md5(code.encode()).hexdigest()
    return res

REDIRECTURL = "http://localhost:3000/withdraw/success/"
class submitDeposit(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = help2payDepositSerialize
    permission_classes = [AllowAny, ]
    def post(self, request, *args, **kwargs):
        language = self.request.POST.get("language")
        user_id = self.request.POST.get("user_id")
        order_id = "ibet" +strftime("%Y%m%d%H%M%S", gmtime())
        amount = int(self.request.POST.get("amount"))
        amount = str('%.2f' % amount)
        #print(amount)
        utc_datetime = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Shanghai'))
        #print(utc_datetime)
        Datetime = utc_datetime.strftime("%Y-%m-%d %H:%M:%S%p")
        #print(Datetime)
        key_time = utc_datetime.strftime("%Y%m%d%H%M%S")
        #print(key_time)
        bank = self.request.POST.get("bank")
        ip = get_client_ip(request)
        currency = self.request.POST.get("currency")
        
        data = {
            "Merchant":HELP2PAY_MERCHANT,
            "Customer":user_id,
            "Currency":currencyConversion[currency],
            "Reference":str(order_id),
            "Key":MD5(HELP2PAY_MERCHANT+str(order_id)+str(user_id)+amount+currencyConversion[currency]+key_time+HELP2PAY_SECURITY+ip),
            "Amount":amount,
            "Datetime":Datetime,
            "FrontURI":REDIRECTURL,
            "BackURI":REDIRECTURL,
            "Bank":bank,
            "Language":language,
            "ClientIP":ip,
        }
        print(data)
        r = requests.post(HELP2PAY_URL, data=data)
        rdata = r.text
        print(r.status_code)
        print(rdata)
        return Response(rdata)
