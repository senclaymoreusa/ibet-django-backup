import requests, json, logging, random, hashlib, base64, datetime, pytz, socket

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View, generic
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.signals import request_finished
from django.dispatch import receiver
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db import IntegrityError, DatabaseError, transaction

from rest_framework import parsers, renderers, status, generics
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes

from users.models import CustomUser
from accounting.models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from utils.constants import *
import utils.helpers as helpers
from users.serializers import LazyEncoder
from ..serializers import help2payDepositSerialize, help2payDepositResultSerialize
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from des import DesKey
from decimal import *
from time import gmtime, strftime, strptime, sleep
from users.views.helper import *


logger = logging.getLogger("django")
currency_Conversion = {
    '2': 'THB',
    '8': 'VND',
}
currencyConversion = {
    2: 'THB',
    8: 'VND',
}
convertCurrency = {
    'THB': 2,
    'VND': 8,
}


def MD5(code):
    res = hashlib.md5(code.encode()).hexdigest()
    return res


class SubmitDeposit(APIView):
    queryset = Transaction.objects.all()
    serializer_class = help2payDepositSerialize
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        language = self.request.POST.get("language")
        user_id = self.request.POST.get("user_id")
    
        trans_id = request.user.username+"-"+timezone.datetime.today().isoformat()+"-"+str(random.randint(0, 10000000))

        amount = float(self.request.POST.get("amount"))
        amount = str('%.2f' % amount)

        utc_datetime = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Shanghai'))
        Datetime = utc_datetime.strftime("%Y-%m-%d %H:%M:%S%p")
        key_time = utc_datetime.strftime("%Y%m%d%H%M%S")
        bank = self.request.POST.get("bank")

        ip = helpers.get_client_ip(request)
        currency = self.request.POST.get("currency")

        merchant_code = '123'
        secret_key = '123'
        if checkUserBlock(CustomUser.objects.get(pk=user_id)):
            errorMessage = _('The current user is blocked!')
            data = {
                "errorCode": ERROR_CODE_BLOCK,
                "errorMsg": {
                    "detail": [errorMessage]
                }
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        if currency == '2':
            merchant_code = HELP2PAY_MERCHANT_THB
            secret_key = HELP2PAY_SECURITY_THB
        elif currency == '8':
            merchant_code = HELP2PAY_MERCHANT_VND
            secret_key = HELP2PAY_SECURITY_VND

        data = {
            "Merchant": merchant_code,
            "Customer": user_id,
            "Currency": currency_Conversion[currency],
            "Reference": str(trans_id),
            "Key": MD5(merchant_code+trans_id+str(user_id)+amount+currency_Conversion[currency]+key_time+secret_key+ip),
            "Amount": amount,
            "Datetime": Datetime,
            "FrontURI": API_DOMAIN + HELP2PAY_SUCCESS_PATH,
            "BackURI": API_DOMAIN + HELP2PAY_CONFIRM_PATH,
            "Bank": bank,
            "Language": language,
            "ClientIP": ip,
        }
        r = requests.post(HELP2PAY_URL, data=data)
        rdata = r.text
        
        db_currency_code = 2 if currency == '2' else 7

        create = Transaction.objects.create(
            transaction_id=trans_id,
            amount=amount,
            user_id=CustomUser.objects.get(pk=user_id),
            method='Bank Transfer',
            currency=db_currency_code,
            transaction_type=TRANSACTION_DEPOSIT,
            channel=0,
            request_time=timezone.now(),
        )
        return HttpResponse(rdata)


class DepositResult(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = help2payDepositResultSerialize
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        trans_status = request.data.get('Status')
        depositID = request.data.get('ID')
        update_data = Transaction.objects.get(
            transaction_id=request.POST.get('Reference'),
            user_id=CustomUser.objects.get(pk=request.POST.get('Customer'))
        )
        if update_data.order_id != '0':  # attempting to confirm the same transaction twice
            logger.info("Callback was sent twice for Deposit #" + str(request.POST.get('Reference')))
            return JsonResponse({
                "error": "Transaction was already modified from 3rd party callback",
                "message": "Transaction already exists"
            })

        result = "Pending"
        if trans_status == '000':
            update_data.status = 0
            result = "Success"
            helpers.addOrWithdrawBalance(update_data.user_id, request.POST.get('Amount'), 'add')
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
        update_data.remark = result
        update_data.save()
        
        return Response({
            'message': 'Received callback from Help2Pay',
            'status': trans_status,
            'result': result
        }, status=status.HTTP_200_OK)

# help2pay requests withdraw info from user
def confirmWithdrawRequest(request):
    if request.method == "POST":
        
        if 'Status' in request.POST:
            try:
                trans_id = request.POST.get("TransactionID")
                amount = request.POST.get("Amount")
                trans_status = request.POST.get("Status")
                withdrawID = request.POST.get('ID')

                update_data = Transaction.objects.get(
                    transaction_id=trans_id,
                    amount=amount
                )
            except ObjectDoesNotExist as e:
                logger.error(repr(e))
                logger.error(f"transaction id {trans_id} does not exist")
                return HttpResponse("false")  

            if update_data.order_id != '0':  # attempting to confirm the same transaction twice
                logger.info("Callback was sent twice for Deposit #" + str(trans_id))
                return JsonResponse({
                    "error": "Transaction was already modified from 3rd party callback",
                    "message": "Transaction already exists"
                })
            result = "Pending"
            if trans_status == '000':
                update_data.status = 0
                result = "Success"
                helpers.addOrWithdrawBalance(update_data.user_id, amount, 'withdraw')
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

            update_data.order_id = withdrawID
            update_data.arrive_time = timezone.now()
            update_data.last_updated = timezone.now()
            update_data.remark = result
            update_data.save()
            
            return HttpResponse("true")
        
        else:
            
            try:
                trans_id = request.GET.get("transId")
                checksum = request.GET.get("key")
                withdraw_txn = Transaction.objects.get(transaction_id=trans_id)
                if withdraw_txn.other_data['checksum'].upper() == checksum.upper():
                    withdraw_txn.arrive_time = timezone.now()
                    withdraw_txn.last_updated = timezone.now()
                    withdraw_txn.status=TRAN_APPROVED_TYPE
                    withdraw_txn.save()
                    return HttpResponse("true")
                else:
                    return HttpResponse("false")
            except ObjectDoesNotExist as e:
                logger.error(repr(e))
                logger.error(f"transaction id {trans_id} does not exist")
                return HttpResponse("false")  

# user submits withdraw request
class SubmitPayout(View):
    def get(self, request):
        return HttpResponse(status=404) 

    def post(self, request): # user will need to submit bank acc information
        username = request.POST.get("username")
        try:
            user = CustomUser.objects.get(username=username)
            withdraw_password = request.POST.get("withdrawPassword")
            
            # toBankAccountName = 'orion'
            # toBankAccountNumber = '12345123'
            toBankAccountName = request.POST.get("toBankAccountName")
            toBankAccountNumber = request.POST.get("toBankAccountNumber")

            amount = float(request.POST.get("amount"))

            trans_id = username+"-"+timezone.datetime.today().isoformat()+"-"+str(random.randint(0, 10000000))
            # trans_id = "orion-"+timezone.datetime.today().isoformat()+"-"+str(random.randint(0, 10000000))
            ip = helpers.get_client_ip(request)
            bank = HELP2PAY_BANK
            
            user_id=user.pk
            currency = user.currency
            merchant_code = '123'
            secret_key = '123'
            payoutURL = '123'
            
            if currency == 2:
                merchant_code = HELP2PAY_MERCHANT_THB
                secret_key = HELP2PAY_SECURITY_THB
                payoutURL = H2P_PAYOUT_URL_THB
                
            elif currency == 8:
                merchant_code = HELP2PAY_MERCHANT_VND
                secret_key = HELP2PAY_SECURITY_VND
                payoutURL = H2P_PAYOUT_URL_VND
            
            
            strAmount = str('%.2f' % amount)
            
            utc_datetime = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Shanghai'))
            Datetime = utc_datetime.strftime("%Y-%m-%d %H:%M:%S%p")
            key_time = utc_datetime.strftime("%Y%m%d%H%M%S")
          
            secretMsg = merchant_code+trans_id+str(user_id)+strAmount+currencyConversion[currency]+key_time+toBankAccountNumber+secret_key
            
            checksum = MD5(secretMsg)
       
            db_currency_code = 2 if currency == 2 else 7
            if check_password(withdraw_password, user.withdraw_password):
                try:    
                    withdraw_request = Transaction(
                        transaction_id=trans_id,
                        amount=amount,
                        user_id=user,
                        method='Bank Transfer',
                        currency=currency,
                        transaction_type=TRANSACTION_WITHDRAWAL,
                        channel=0,
                        request_time=timezone.now(),
                        other_data={'checksum': checksum},
                    )
                    withdraw_request.save()
                    logger.info("Withdraw request created: " + str(withdraw_request))
                    # can_withdraw = helpers.addOrWithdrawBalance('orion', amount, "withdraw")
                    can_withdraw = helpers.addOrWithdrawBalance(username, amount, "withdraw")

                except (ObjectDoesNotExist, IntegrityError, DatabaseError) as e:
                    logger.error(repr(e))
                    traceback.print_exc(file=sys.stdout)
                    return HttpResponse(status=500)
            else:
                logger.error("withdraw password is not correct.")    
                return JsonResponse({
                    'status_code': ERROR_CODE_INVALID_INFO,
                    'message': 'Withdraw password is not correct.'
                })
        
            if can_withdraw:
                data = {
                    "Key": MD5(secretMsg),
                    "ClientIP": ip,
                    "ReturnURI": HELP2PAY_RETURN_URL,
                    "MerchantCode": merchant_code,
                    "TransactionID": str(trans_id),
                    "MemberCode": user_id,
                    "CurrencyCode": currencyConversion[currency],
                    "Amount": amount,
                    "TransactionDateTime": Datetime,
                    "BankCode": bank,
                    "toBankAccountName": toBankAccountName,
                    "toBankAccountNumber": toBankAccountNumber,
                }
                
                r = requests.post(payoutURL, data=data)
                
                if r.status_code == 200:
                    return HttpResponse(r.content)
                else:
                    return JsonResponse({
                        'status_code': ERROR_CODE_FAIL,
                        'message': 'Payment service unavailable'

                    })
            else:
                return JsonResponse({
                    'status_code': ERROR_CODE_FAIL,
                    'message': 'Insufficient funds'
                })
        except ObjectDoesNotExist as e:
            logger.error(repr(e))
            return HttpResponse(status=500)





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
    
    

        
    

