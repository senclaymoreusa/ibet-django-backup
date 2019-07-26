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
from ..serializers import help2payDepositSerialize,help2payDepositResultSerialize
from django.conf import settings
import requests,json
import logging, time, struct, hashlib, xml.etree.ElementTree as ET
from time import sleep
from des import DesKey
import base64
from time import gmtime, strftime, strptime
import datetime, pytz
from decimal import *
import xmltodict, socket
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
convertCurrency = {
    'CNY':'0',
    'USD':'1',
    'THB':'2',
    'IDR':'3',
    'HKD':'4',
    'AUD':'5',
    'THB':'6',
    'MYR':'7',
    'VND':'8',
    'MMK':'9',
    'XBT':'10',
}
def get_Host_name_IP(): 
    try: 
        host_name = socket.gethostname() 
        host_ip = socket.gethostbyname(host_name) 
        return host_ip
    except: 
        logger.info("Unable to get Hostname and IP") 
  

def MD5(code):
    res = hashlib.md5(code.encode()).hexdigest()
    return res


class submitDeposit(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = help2payDepositSerialize
    permission_classes = [AllowAny, ]
    def post(self, request, *args, **kwargs):
        language = self.request.POST.get("language")
        user_id = self.request.POST.get("user_id")
        order_id = self.request.POST.get("order_id")
        #order_id = "ibet" +strftime("%Y%m%d%H%M%S", gmtime())
        amount = int(self.request.POST.get("amount"))
        amount = str('%.2f' % amount)
        utc_datetime = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Shanghai'))
        Datetime = utc_datetime.strftime("%Y-%m-%d %H:%M:%S%p")
        key_time = utc_datetime.strftime("%Y%m%d%H%M%S")
        bank = self.request.POST.get("bank")
        ip = get_Host_name_IP()
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
            "BackURI":BackURI,
            "Bank":bank,
            "Language":language,
            "ClientIP":ip,
        }
        r = requests.post(HELP2PAY_URL, data=data)
        rdata = r.text
        create = Transaction.objects.create(
            order_id= order_id,
            amount=amount,
            user_id=CustomUser.objects.get(pk=user_id),
            method= 'Bank Transfer',
            currency= currency,
            transaction_type=0,
            channel=0,
        )
        
        return HttpResponse(rdata)

class depositResult(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = help2payDepositResultSerialize
    permission_classes = [AllowAny, ]
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        Status = self.request.data.get('Status')
        depositID = self.request.data.get('ID')
        update_data = Transaction.objects.get(order_id=self.request.POST.get('Reference'),
                                              user_id=CustomUser.objects.get(pk=self.request.POST.get('Customer')))
        update_data.transaction_id = depositID
        if  Status == '000':  
            update_data.status = 0
        elif Status == '001':
            update_data.status = 1
        elif Status == '006':
            update_data.status = 4
        elif Status == '007':
            update_data.status = 8
        elif Status == '009':
            update_data.status = 3
        update_data.save()
        
        return Response({'details': 'result successful arrived'}, status=status.HTTP_200_OK)
@api_view(['POST'])
@permission_classes((AllowAny,))
def depositFrontResult(request):
    order_id = request.data.get('Reference')
    if request.data.get('Status') == '000':
        return HttpResponse("Order[%s] is success." % (order_id))
    elif request.data.get('Status') == '001':
        return HttpResponse("Order[%s] is failed." % (order_id))
    elif request.data.get('Status') == '006':
        return HttpResponse("Order[%s] is approved." % (order_id))
    elif request.data.get('Status') == '007':
        return HttpResponse("Order[%s] is rejected." % (order_id))
    elif request.data.get('Status') == '009':
        return HttpResponse("Order[%s] is pending." % (order_id))

@api_view(['POST'])
@permission_classes((AllowAny,))
def depositStatus(request):
    order_id = request.data.get('order_id')
    getData = Transaction.objects.get(order_id=order_id)
    order_status = getData.status
    return Response(order_status)
    
    

        
    

