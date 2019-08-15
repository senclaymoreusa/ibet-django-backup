import requests, json, logging, hashlib, base64, datetime, pytz, socket

from django.shortcuts import render
from django.http import HttpResponse
from django.views import View, generic
from django.utils import timezone

from rest_framework import parsers, renderers, status, generics
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes


from users.models import CustomUser
from ..models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement

from ..serializers import help2payDepositSerialize,help2payDepositResultSerialize
from django.conf import settings
from time import sleep
from des import DesKey
from decimal import *
from time import gmtime, strftime, strptime

from utils.constants import *
import utils.helpers as helpers

logger = logging.getLogger("django")
currencyConversion = {
    '2': 'THB',
    '8': 'VND',
}
convertCurrency = {
    'THB': '2',
    'VND': '8',
}


def MD5(code):
    res = hashlib.md5(code.encode()).hexdigest()
    return res


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class SubmitDeposit(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = help2payDepositSerialize
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        language = self.request.POST.get("language")
        user_id = self.request.POST.get("user_id")

        trans_id = self.request.POST.get("order_id")
        # order_id = "ibet" +strftime("%Y%m%d%H%M%S", gmtime())

        amount = float(self.request.POST.get("amount"))
        amount = str('%.2f' % amount)
        utc_datetime = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Shanghai'))
        Datetime = utc_datetime.strftime("%Y-%m-%d %H:%M:%S%p")
        key_time = utc_datetime.strftime("%Y%m%d%H%M%S")
        bank = self.request.POST.get("bank")
        # ip = get_Host_name_IP()
        ip = get_client_ip(request)
        currency = self.request.POST.get("currency")
        
        if currency == '2':
            help2pay_merchant = HELP2PAY_MERCHANT_THB
            help2pay_security = HELP2PAY_SECURITY_THB
        elif currency == '8':
            help2pay_merchant = HELP2PAY_MERCHANT_VND
            help2pay_security = HELP2PAY_SECURITY_VND
        print(help2pay_merchant)
        print(user_id)
        print(ip)
        data = {
            "Merchant": help2pay_merchant,
            "Customer": user_id,
            "Currency": currencyConversion[currency],
            "Reference": str(trans_id),
            "Key": MD5(help2pay_merchant+str(trans_id)+str(user_id)+amount+currencyConversion[currency]+key_time+help2pay_security+ip),
            "Amount": amount,
            "Datetime": Datetime,
            # "FrontURI": "http://localhost:3000/deposit/success/",
            "FrontURI": "https://03720ad2.ngrok.io/" + HELP2PAY_CONFIRM_PATH,
            "BackURI": "https://03720ad2.ngrok.io/" + HELP2PAY_CONFIRM_PATH,
            "Bank": bank,
            "Language": language,
            "ClientIP": ip,
        }
        r = requests.post(HELP2PAY_URL, data=data)
        rdata = r.text
        create = Transaction.objects.create(
            transaction_id=trans_id,
            amount=amount,
            user_id=CustomUser.objects.get(pk=user_id),
            method='Bank Transfer',
            currency=currency,
            transaction_type=0,
            channel=0,
            request_time=timezone.now(),
        )
        
        return HttpResponse(rdata)


class DepositResult(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = help2payDepositResultSerialize
    permission_classes = [AllowAny, ]
    def post(self, request, *args, **kwargs):
        print(request.POST)
        serializer = self.serializer_class(self.get_queryset(), many=True)
        trans_status = self.request.data.get('Status')
        depositID = self.request.data.get('ID')
        update_data = Transaction.objects.get(transaction_id=self.request.POST.get('Reference'),
                                              user_id=CustomUser.objects.get(pk=self.request.POST.get('Customer')))
        result = "Pending"
        if trans_status == '000':
            update_data.status = 0
            result = "Success"
            helpers.addOrWithdrawBalance(update_data.user_id, request.POST.get('amount'), 'add')
        elif trans_status == '001':
            update_data.status = 1
            result = "Failed"
        elif trans_status == '006':
            update_data.status = 4
            result = "Approved"
        elif trans_status == '007':
            update_data.status = 8
            result = "Rejected"
        elif trans_status == '009':
            update_data.status = 3
            result = "Pending"

        update_data.order_id = depositID
        update_data.arrive_time = timezone.now()
        update_data.last_updated = timezone.now()
        update_data.save()
        
        return Response({
            'message': 'Result successfully arrived',
            'status': trans_status,
            'result': result
        }, status=status.HTTP_200_OK)


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
@permission_classes((IsAuthenticated,))
def depositStatus(request):
    order_id = request.data.get('order_id')
    getData = Transaction.objects.get(order_id=order_id)
    order_status = getData.status
    return Response(order_status)
    
    

        
    

