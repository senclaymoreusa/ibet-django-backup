import requests,json, os, datetime, time, hmac, hashlib, base64, logging, uuid, random

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.views import View, generic
from django.utils import timezone
from django.db import DatabaseError, transaction
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import status, generics, parsers, renderers
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes,renderer_classes
from django.core.exceptions import ObjectDoesNotExist
from utils.constants import *
from users.serializers import LazyEncoder
from users.models import CustomUser, Config, NoticeMessage
from accounting.models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from accounting.serializers import depositMethodSerialize, bankListSerialize,bankLimitsSerialize,submitDepositSerialize,submitPayoutSerialize, payoutTransactionSerialize,approvePayoutSerialize,depositThirdPartySerialize, payoutMethodSerialize,payoutBanklistSerialize,payoutBanklimitsSerialize
from utils.helpers import addOrWithdrawBalance
from django.utils.translation import ugettext_lazy as _
from time import sleep, gmtime, strftime
from users.views.helper import *


QAICASH_NAME = 3

#payment
merchantId = MERCHANTID
merchantApiKey = MERCHANTAPIKEY
apiVersion = APIVERSION
api = QAICASH_URL 
deposit_url = DEPOSIT_URL
payout_url = PAYOUT_URL
logger = logging.getLogger('django')

# currency conversion dictionary for supported currencies
currencyConversion = {
    "0": "CNY",
    "1": "USD",
    "2": "PHP",
    "3": "IDR",
}
methodConversion = {
    "0": "LBT_ONLINE",
    "1": "LBT_ATM",
    "2": "LBT_OTC",
    "3": "DIRECT_PAYMENT",
    "4": "BANK_TRANSFER",
    "5": "IBT"
}

statusConversion = {
    "SUCCESS":0,
    "FAILED":1,
    "CREATED":2,
    "PENDING":3,
    "APPROVED":4,
    "REJECTED":5,
    "COMPLETED":6,
    "RESEND":7,
    "REJECTED": 8,
    "HELD": 9,
}
reviewStatusConversion = {
    'APPROVED': 0,
    'PENDING': 1,
    'REJECTED': 2,
    'SUCCESSFUL': 3,
    'FAILED': 4,
    'RESEND': 5,
    'HELD': 6,
}
REDIRECTURL = "https://ibet-web-dev.claymoreeuro.com/p/banking/withdraw"
def generateHash(key, message):
    hash = hmac.new(key, msg=message, digestmod=hashlib.sha256)
    #hash.hexdigest()
    return hash.hexdigest()

# get available methods and save/update to database
class getDepositMethod(generics.GenericAPIView):
    queryset = DepositChannel.objects.all()
    serializer_class = depositMethodSerialize
    permission_classes = (AllowAny,)
    
    def post(self, request, *args, **kwargs):
        currency = self.request.POST['currency'] # should come in as a number ("0", "1", "2", etc.)
        try:
            currency_long = currencyConversion[currency] # convert number to international currency format
        except KeyError:
            return Response({"error" : "Unsupported currency format"})
        url = api + apiVersion +'/' + merchantId + deposit_url + currency_long + '/methods'
        headers = {'Accept': 'application/json'}

        # username = self.request.GET.get('username')
        # userId = CustomUser.objects.filter(username=username)

        message = bytes(merchantId + '|' + currency_long, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        
        my_hmac = generateHash(secret, message)
        delay = kwargs.get("delay", 5)
        success = False
        
        if request.user_agent.is_pc:
            deviceType = 'PC'
        else:
            deviceType = 'MOBILE'

        #retry
        for x in range(3):
            r = requests.get(url, headers=headers, params = {
                # 'userId' : userId,
                'hmac' : my_hmac,
                'deviceType' : deviceType,
            })
            responseJson = r.json()
            if r.status_code == 200:
                success = True
                break
            if r.status_code == 400 or r.status_code == 401:
                success = True
                # Handle error
                logger.critical("Failed to complete a request for qaicash getDepositMethod...")
                
                return Response(responseJson)
            if r.status_code == 500:
                
                logger.info("Request failed {} time(s) Waiting for %s seconds before retrying again".format(x+1))
                sleep(delay)
        if not success:
            return Response(responseJson)
        for x in responseJson:
            logger.info(x)
            depositData = {
                "thirdParty_name": QAICASH_NAME, # third party name is hard-fixed to match the channel choice in models
                "method": x['method'],
                "currency": currency,
                "min_amount": x['limits'].get('minTransactionAmount'),
                "max_amount": x['limits'].get('maxTransactionAmount'),
            }
            data = depositMethodSerialize(data=depositData)
            if (data.is_valid()):
                data.save()
            else:
                return Response({"error": "Invalid data passed into serializer", "description": data.errors})
        return Response(responseJson)

# fetch supported bank list for the specified currency + deposit method from qaicash API
class getBankList(generics.GenericAPIView):
    queryset = DepositChannel.objects.all()
    serializer_class = bankListSerialize # appears that we need to override this attribute for every GenericAPIView
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        currency = self.request.POST['currency']
        method = self.request.POST['method']

        serializer = bankListSerialize(data={ # validate POST data
            "currency": currency,
            "method": method
        }) 

        if (serializer.is_valid()):
            currency_long = currencyConversion[currency]
            method_long = methodConversion[method]
            logger.info("currency: " + currency_long + ", method: " + method_long)
            url = api + apiVersion +'/' + merchantId + deposit_url + currency_long + '/methods/' + method_long + '/banks'
            logger.info(url)
            headers = {'Accept': 'application/json'}

            # username = self.request.GET.get('username')
            # userId = CustomUser.objects.filter(username=username)

            message = bytes(merchantId + '|' + currency_long, 'utf-8')
            secret = bytes(merchantApiKey, 'utf-8')

            my_hmac = generateHash(secret, message) # hmac format for qaicash api

            delay = kwargs.get("delay", 5)
            if request.user_agent.is_pc:
                deviceType = 'PC'
            else:
                deviceType = 'MOBILE'

            for x in range(3):
                r = requests.get(url, headers=headers, params = {
                    # 'userId' : userId,
                    'hmac' : my_hmac,
                    'deviceType' : deviceType,
                })
                data = r.json() # r.json() converts the string/byte return of the response into a JSON object
                if r.status_code == 200:
                    return Response(data)            
                if r.status_code == 400 or r.status_code == 401:
                    logger.critical("Failed to complete a request for Qaicash retrieving available bank lists (getBankList())")
                    
                    return Response(data)
                if r.status_code == 500:
                    
                    logger.info("Request failed {} time(s) wating for %s seconds before retrying again".format(x+1))
                    sleep(delay) 
            return Response(data)
        else:
            return Response({"error": "Invalid data passed into serializer", "description": serializer.errors})


# get the specific min/max amounts for a specific bank and for a specific currency
class getBankLimits(generics.GenericAPIView):
    queryset = DepositChannel.objects.all()
    serializer_class = bankLimitsSerialize
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # POST params:
        # bank - bank code, sandbox 
        # currency - currency ISO code
        # method - deposit method

        bank = self.request.POST['bank']
        currency = self.request.POST['currency']
        method = self.request.POST['method']

        # currency_long = currencyConversion[currency]
        # method_long = methodConversion[method]
        logger.info(bank, currency, method)
        url =  api + apiVersion +'/' + merchantId + deposit_url + currency + '/methods/' + method + '/banks/' + bank + '/limits/'
        headers = {'Accept': 'application/json'}
        if request.user_agent.is_pc:
                deviceType = 'PC'
        else:
            deviceType = 'MOBILE'

        # username = self.request.GET.get('username')
        # userId = CustomUser.objects.filter(username=username)

        secret = bytes(merchantApiKey, 'utf-8')
        message = bytes(merchantId + '|' + currency, 'utf-8')

        my_hmac = generateHash(secret, message)
        delay = kwargs.get("delay", 5)

         #retry
        success = False
        
        for x in range(3):
            r = requests.get(url, headers=headers, params = {
                # 'userId' : userId,
                'hmac' : my_hmac,
                'deviceType' : deviceType,
            })
            logger.info("bank limits response: ")
            logger.info(r)
            if r.status_code == 200:
                success = True
                break
            if r.status_code == 400 or r.status_code == 401:
                
                logger.info("Failed to complete a request for retrieving available Qaicash Bank Limits")
                
                return Response(data)
            if r.status_code == 500:
                logger.info('Request failed {} time(s) wating for %s seconds before retrying again'.format(x+1))
                
                sleep(delay) 

        if not success:
            logger.critical("Failed to complete a request for getBankLimits()")
            return Response({"error" : "Qaicash API returned a status code of 500", "message": r.text})
        else:
            data = r.json()
            
        # save a single bank limit into the database...?
        depositData = {
            "thirdParty_name": QAICASH_NAME,
            "method": method,
            "currency": currency,
            "min_amount":data["minTransactionAmount"],
            "max_amount":data["maxTransactionAmount"],
        }
        # serializer = depositMethodSerialize(data=depositData)

        # print("have the following data for serializer:")
        # if (serializer.is_valid()):
        #     print(serializer.validated_data)
        #     serializer.save()
        # else:
        #     return Response({"error": "Invalid data passed into serializer"})
        return Response(data)

class submitDeposit(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = submitDepositSerialize
    permission_classes = [AllowAny, ]
    
    def get_response(self,request):
        serializer_class = self.get_response_serializer()
        serializer = serializer_class(instance=data,
                                          context={'request': self.request})
        if serializer.is_valid():
            serializer.save() 
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):

        serializer = submitDepositSerialize(self.queryset, many=True)
        url =  api + apiVersion + '/' + merchantId + '/deposit/'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        dateTime = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%z')
        curr = self.request.POST.get('currency')
        currency = currencyConversion[curr]
        userId = self.request.POST.get('user_id')
        user = CustomUser.objects.get(pk=userId)
        trans_id = user.username+"-"+timezone.datetime.today().isoformat()+"-"+str(random.randint(0,10000000))
        #orderId = "ibet" + strftime("%Y%m%d%H%M%S", gmtime())
        amount =self.request.POST.get('amount')
        language = self.request.POST.get('language')
        
        mymethod = self.request.POST.get('method')
        
        depositorBank = self.request.POST.get('bank')
        depositorEmail = user.email
        depositorName = user.first_name + " " + user.last_name
        if "-" in user.phone:
            depositorPhone = user.phone.split("-")[1]
        else:
            depositorPhone = user.phone
        
        list = [merchantId, trans_id, amount, currency, dateTime, userId, mymethod]
        message = '|'.join(str(x) for x in list)
        
        mymessage = bytes(message, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        my_hmac = generateHash(secret, mymessage)
        delay = kwargs.get("delay", 5)
        
        first_name = self.request.GET.get('first_name')
        email = self.request.GET.get('email')
        
        delay = kwargs.get("delay", 5)
        if request.user_agent.is_pc:
            deviceType = 'PC'
        else:
            deviceType = 'MOBILE'

        #retry
        success = False
        if checkUserBlock(user):
            errorMessage = _('The current user is blocked!')
            data = {
                "errorCode": ERROR_CODE_BLOCK,
                "errorMsg": {
                    "detail": [errorMessage]
                }
            }
            return Response(data)

        r = requests.post(url, headers=headers, data = {
            'orderId' : trans_id,
            'amount' : amount,
            'currency' : currency,
            'dateTime': dateTime,
            'language': language,
            'depositorUserId': userId,
            'depositorTier': '0',
            'depositMethod':  mymethod,
            'depositorEmail': depositorEmail,
            'depositorName': depositorName,
            'depositorBank':depositorBank,
            'depositorPhone':depositorPhone,
            'redirectUrl': 'https://www.google.com',
            'callbackUrl': CALLBACK_URL,
            'messageAuthenticationCode': my_hmac,
        })
        rdata = r.json()
        if r.status_code == 200 or r.status_code == 201:
            success = True
        if r.status_code == 400 or r.status_code == 401:
            
            logger.error("Failed to complete a request for submitting Qaciash deposit..")
            
            return Response(rdata)
        if r.status_code == 500:
            logger.info('Request failed {} time(s) wating for %s seconds before retrying again'.format(x+1))
            
            sleep(delay) 
        
        
        if not success:
            logger.critical("Failed to complete a request for Qaicash deposit")
            return Response({"error" : "Qaicash API returned a status code of 500", "message": r.text})
        else:
            create = Transaction.objects.create(
                order_id= rdata["depositTransaction"]["transactionId"],
                transaction_id=rdata['depositTransaction']['orderId'],
                amount=rdata["depositTransaction"]["amount"],
                status=TRAN_CREATE_TYPE,
                user_id=CustomUser.objects.get(pk=userId),
                method= rdata["depositTransaction"]["depositMethod"],
                currency= curr,
                transaction_type=TRANSACTION_DEPOSIT,
                channel=QAICASH,
                request_time=rdata["depositTransaction"]["dateCreated"],
            )
            return Response(rdata)
 
class submitPayout(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = submitPayoutSerialize
    permission_classes = [AllowAny, ]
    
    def get_response(self,request):
        serializer_class = self.get_response_serializer()
        serializer = serializer_class(instance=data,
                                          context={'request': self.request})
        if serializer.is_valid():
            serializer.save() 
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):

        serializer = submitPayoutSerialize(self.queryset, many=True)
        url =  api + apiVersion + '/' + merchantId + '/payout/'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        currency = self.request.POST['currency']
        dateTime = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%z')
        
        orderId = "ibet" + strftime("%Y%m%d%H%M%S", gmtime())
        amount =self.request.POST.get('amount')
        language = self.request.POST.get('language')
        userId = self.request.POST.get('user_id')
        withdraw_password = self.request.POST.get("withdraw_password")
        try:
            user = CustomUser.objects.get(username=userId)
        except ObjectDoesNotExist:
            logger.error("The  user does not exist.")
            return Response({"error":"The  user does not exist."}) 
        trans_id = user.username+strftime("%Y%m%d%H%M%S", gmtime())+str(random.randint(0,10000000))
        mymethod = self.request.POST.get('method')
        list = [merchantId, trans_id, amount, currency, dateTime, userId]
        message = '|'.join(str(x) for x in list)
        
        mymessage = bytes(message, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        my_hmac = generateHash(secret, mymessage)
        delay = kwargs.get("delay", 5)
        
        first_name = self.request.GET.get('first_name')
        email = self.request.GET.get('email')
         #retry
        success = False
        if checkUserBlock(user):
            errorMessage = _('The current user is blocked!')
            data = {
                "errorCode": ERROR_CODE_BLOCK,
                "errorMsg": {
                    "detail": [errorMessage]
                }
            }
            return Response(data)
        if check_password(withdraw_password, user.withdraw_password):
            r = requests.post(url, headers=headers, data = {
                'orderId' : trans_id,
                'amount' : amount,
                'currency' : currency,
                'dateTime': dateTime,
                'language': language,
                'userId': userId,
                'depositorTier': '0',
                'payoutMethod':  mymethod,
                'withdrawerEmail': user.email,
                'withdrawerName': user.first_name + " " + user.last_name,
                'redirectUrl': REDIRECTURL,
                'withdrawerEmail':user.email,
                'callbackUrl':CALLBACK_URL,
                'messageAuthenticationCode': my_hmac,
            })
            
            rdata = r.json()
            
        else:
            logger.error("withdraw password is not correct.")    
            return JsonResponse({
                'status_code': ERROR_CODE_INVALID_INFO,
                'message': 'Withdraw password is not correct.'
            })
        if r.status_code == 201:  
            user = CustomUser.objects.get(username=rdata['payoutTransaction']['userId'])
            cur_status = 0
            for x in Transaction._meta.get_field('currency').choices:
                if rdata["payoutTransaction"]["currency"] == x[1]:
                    cur_val = x[0]

            # for y in Transaction._meta.get_field('status').choices:
            #     if rdata["payoutTransaction"]["status"] ==y[1]:
            #         cur_status = y[0] 
            create = Transaction.objects.create(
                transaction_id= rdata["payoutTransaction"]['orderId'],
                order_id=rdata["payoutTransaction"]["transactionId"],
                amount=rdata["payoutTransaction"]["amount"],
                status=statusConversion[rdata["payoutTransaction"]["status"]],
                user_id=user,
                method= rdata["payoutTransaction"]["payoutMethod"],
                currency= cur_val,
                transaction_type=TRANSACTION_WITHDRAWAL,
                channel=QAICASH,
                request_time=rdata['payoutTransaction']['dateCreated'],
            )
            
            return Response(rdata)
        else:
            logger.critical('Qaicash::Unable to submit payout request.')
            return Response({"error":"Qaicash::Unable to submit payout request."})

        
           
class getPayoutTransaction(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = payoutTransactionSerialize
    permission_classes = [AllowAny,]
    

    def post(self, request, *args, **kwargs):
        serializer = payoutTransactionSerialize(self.queryset, many=True)
        
        orderId = self.request.POST['order_id']
        message = bytes(merchantId + '|' + orderId, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        
        my_hmac = generateHash(secret, message)
        url =  api + apiVersion +'/' + merchantId + '/payout/' + orderId + '/mac/' + my_hmac
        headers = {'Accept': 'application/json'}
         #retry
        success = False
        for x in range(3):
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                success = True
                break
            if r.status_code == 500:
                logger.info('Request failed {} time(s)'.format(x+1))
                logger.debug("wating for %s seconds before retrying again")
                sleep(delay) 
        if not success:
            logger.critical('Failed to complete a request for qaicash payout transaction')
        # Handle error

        rdata = r.json()
        #print(rdata)
        logger.info(rdata)
        if r.status_code == 200:  
               
            update_data = Transaction.objects.get(transaction_id=rdata['orderId'],
                                                method=rdata["payoutMethod"],                                                                      
            )
            update_data.order_id=rdata['transactionId']
            update_data.last_updated=rdata["dateUpdated"]
            update_data.status=reviewStatusConversion[rdata["status"]]
            update_data.save()
            # create = Transaction.objects.get_or_create(
            #     order_id= rdata['orderId'],
            #     request_time=rdata["dateCreated"],
            #     amount=rdata["amount"],
            #     status=cur_status,
            #     user_id=user,
            #     method= rdata["payoutMethod"],
            #     currency= cur_val,
            #     transaction_type=1,
            #     channel=3,
            # )
        else:
            logger.error('The request information is nor correct, please try again')
        
        
        return Response(rdata)
class approvePayout(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = approvePayoutSerialize
    permission_classes = [AllowAny,]

    def post(self, request, *args, **kwargs):
        serializer = approvePayoutSerialize(self.queryset, many=True)
        
        orderId = self.request.POST['order_id']
        userId = self.request.POST['user_id']
        notes = self.request.POST.get('remark')
        list = [merchantId, orderId, userId, notes]
        message = '|'.join(str(x) for x in list)
        mymessage = bytes(message, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        my_hmac = generateHash(secret, mymessage)

        url =  api + apiVersion +'/' + merchantId + '/payout/' + orderId + '/approve' 
        headers = {'Accept': 'application/json'}
         #retry
        success = False
        for x in range(3):
            try:
                r = requests.post(url, headers=headers, data={
                    'approvedBy': userId,
                    'notes': notes,
                    'messageAuthenticationCode': my_hmac,
                })
                if r.status_code == 200:
                    success = True
                    break
            except ValueError:
                logger.info('Request failed {} time(s). wating for %s seconds before retrying again'.format(x+1))
                
                sleep(delay) 
        if not success:
            logger.critical('Failed to complete a request for approving payout transaction')
        # Handle error
        
        rdata = r.json()
        logger.info(rdata)

        try:
            user = CustomUser.objects.get(username=rdata['userId'])
            update_data = Transaction.objects.get(transaction_id=rdata['orderId'])

            update_data.order_id = rdata['transactionId']
            update_data.last_updated = rdata["dateUpdated"]
            update_data.status = TRAN_APPROVED_TYPE
            update_data.review_status = REVIEW_APP
            update_data.remark = notes
            update_data.release_by = user
            update_data.current_balance = user.main_walllet - update_data.amount
            update_data.save()

            logger.info('Finish updating the status of withdraw ' + str(rdata['orderId']) + ' to Approve')
            return Response(rdata)

        except ObjectDoesNotExist as e:
            
            logger.info("matching user or transaction not found / does not exist" + str(e))
            return Response({"error": "Could not find matching user or transaction", "code": ERROR_CODE_NOT_FOUND})

        # this withdrawal transaction may not in held status
        except Exception as e:
            logger.error("Error approving this qaicash transaction " + str(e))
            return Response({"error": "Error approving this transaction ", "code": ERROR_CODE_INVAILD_INFO})


class rejectPayout(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = approvePayoutSerialize
    permission_classes = [AllowAny,]
    

    def post(self, request, *args, **kwargs):
        serializer = approvePayoutSerialize(self.queryset,context={'request': request}, many=True)
        
        orderId = self.request.POST['order_id']
        userId = self.request.POST['user_id']
        notes = self.request.POST['remark']
        list = [merchantId, orderId, userId, notes]
        message = '|'.join(str(x) for x in list)
        mymessage = bytes(message, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        my_hmac = generateHash(secret, mymessage)

        url =  api + apiVersion +'/' + merchantId + '/payout/' + orderId + '/reject' 
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        delay = kwargs.get("delay", 5)

         #retry
        success = False
        for x in range(3):
            try:
                r = requests.post(url, headers=headers, data={
                    'rejectedBy': userId,
                    'notes': notes,
                    'messageAuthenticationCode': my_hmac,
                })
                if r.status_code == 200:
                    success = True
                    break
            except ValueError:
                logger.info('Request failed {} time(s).wating for %s seconds before retrying again'.format(x+1))
                
                sleep(delay)  
        if not success:
            logger.critical('Failed to complete a request for rejecting payout transaction')
        # Handle error

        rdata = r.json()
        #print(rdata)
        

        if r.status_code == 200:  
            
            for x in Transaction._meta.get_field('currency').choices:

                if rdata['currency'] == x[1]:
                    cur_val = x[0]
            for y in Transaction._meta.get_field('status').choices:
                if rdata["status"] ==y[1]:
                    cur_status = y[0] 
            try:
                with transaction.atomic():
                    user = CustomUser.objects.get(username=rdata['userId'])
                    update_data = Transaction.objects.get(transaction_id=rdata['orderId'])

                    update_data.order_id = rdata['transactionId']
                    update_data.last_updated = rdata["dateUpdated"]
                    update_data.status = TRAN_REJECTED_TYPE
                    update_data.review_status = REVIEW_REJ
                    update_data.remark = notes
                    update_data.release_by = user
                    update_data.save()

                    addOrWithdrawBalance(user.username, update_data.amount, 'add')

                    logger.info('Finish updating the status of withdraw ' + str(rdata['orderId']) + ' to Approve')
                    return Response(rdata)
            except ObjectDoesNotExist as e:
                
                logger.error("matching transaction not found / does not exist for qaicash rejecting payout")
                return Response({"error": "Could not find matching transaction for qaicash rejecting payout","code": ERROR_CODE_NOT_FOUND})

            except DatabaseError as e:
                logger.info("Error update transaction for qaicash rejecting payout" + str(e))
                return Response({"error": "Error updating transaction for qaicash rejecting payout", "code": ERROR_CODE_DATABASE})

        else:
            logger.error('The request information is not correct for qaicash rejecting payout, please try again.')
            return Response({"error": "The request information is not correct for qaicash rejecting payout", "code": ERROR_CODE_INVALID_INFO})
class getDepositTransaction(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = payoutTransactionSerialize
    permission_classes = [AllowAny,]
    

    def post(self, request, *args, **kwargs):
        serializer = payoutTransactionSerialize(self.queryset, many=True)
        
        trans_id = self.request.POST.get('order_id')
        # print(trans_id)
        message = bytes(merchantId + '|' + trans_id, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        
        my_hmac = generateHash(secret, message)
        url =  api + apiVersion +'/' + merchantId + '/deposit/' + trans_id + '/mac/' + my_hmac
        headers = {'Accept': 'application/json'}
         #retry
        success = False
        
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                success = True
                
        except ValueError:
            logger.info('Request failed {} time(s).wating for %s seconds before retrying again'.format(x+1))
            
            sleep(delay) 
        if not success:
            logger.critical('Failed to complete a request for payout transaction')
        # Handle error

        rdata = r.json()
        logger.info(rdata)
        
        for x in Transaction._meta.get_field('currency').choices:

            if rdata['currency'] == x[1]:
                cur_val = x[0]
        if success:
            update_data = Transaction.objects.get(transaction_id=rdata['orderId'],amount=rdata["amount"],method= rdata["depositMethod"],status=2)
            update_data.status=statusConversion[rdata["status"]]
            update_data.last_updated=rdata["dateUpdated"]
            update_data.save()
      
        return Response(rdata)
# @api_view(['POST'])
# @permission_classes((AllowAny,))   
#@renderer_classes([renderers.OpenAPIRenderer, renderers.JSONRenderer])
def transactionConfirm(request):
    body = json.loads(request.body)
    orderId = body.get('orderId')
    Status = body.get('status') 
    cur_status = statusConversion[Status]
    notes = body.get('notes')
    try:
        order_id = Transaction.objects.get(transaction_id=orderId)
    except Transaction.DoesNotExist:
        order_id = None
        logger.error("Transaction does not exist for qaicash transaction confirm")
        return HttpResponse("Transaction does not exist for qaicash transaction confirm", content_type="text/plain")

    if order_id: 
        # update = order_id.update(
        #     status=cur_status,
        #     last_updated=timezone.now(),
        # )
        order_id.status = cur_status
        order_id.last_updated = timezone.now()

        if cur_status == 0:
            if order_id.transaction_type == TRANSACTION_DEPOSIT:
                try:
                    user = CustomUser.objects.get(username=order_id.user_id)
                except ObjectDoesNotExist:
                    logger.error("Qaicash:: the user does not exist for transaction Confirm.")
                    return HttpResponse("the user does not exist for transaction Confirm", content_type="text/plain")
                # update = order_id.update(
                #     arrive_time=timezone.now(),
                #     #current_balance= + update.amount,
                #     remark = 'Transaction success!')
                order_id.arrive_time = timezone.now()
                order_id.current_balance = user.main_wallet + order_id.amount
                order_id.remark = 'Transaction success!'
                order_id.save()

            elif order_id.transaction_type == TRANSACTION_WITHDRAWAL:

                # update = order_id.update(
                #     arrive_time=timezone.now(),
                #     current_balance=update.current_balance - update.amount,
                #     remark = 'Transaction success!')
                order_id.arrive_time = timezone.now()
                order_id.current_balance = user.main_wallet - order_id.amount
                order_id.remark = 'Transaction success!'
                order_id.save()

            
        else :
            
            # update = order_id.update(
            #     remark = notes)
            order_id.remark = notes
            order_id.save()
    return HttpResponse("Transaction is " + Status, content_type="text/plain")

@api_view(['POST'])
@permission_classes((AllowAny,))   
def get_transaction_status(request):
    trans_id = request.data.get('trans_id')
    try:
        transaction = Transaction.objects.get(
            transaction_id=trans_id
        )
        logger.info(transaction)
        status = transaction.status
        return Response({"status": status})
    except ObjectDoesNotExist as e:
        
        logger.error("matching transaction not found / does not exist for qaicash get_transaction_status method")
        return Response({"message": "Could not find matching transaction for qaicash get_transaction_status method"})


# class transactionStatusUpdate(generics.GenericAPIView):
#     queryset = Transaction.objects.all()
#     serializer_class = depositThirdPartySerialize
#     permission_classes = [AllowAny,]
#     renderer_classes = [renderers.OpenAPIRenderer, renderers.JSONRenderer]
     
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(self.get_queryset(), many=True)
#         orderId = self.request.data.get('orderId')
#         Status = self.request.data.get('status') 
#         for x in Transaction._meta.get_field('status').choices:
#                 if Status == x[1]:
#                     cur_status = x[0]
#         try: 
#             order_id = Transaction.objects.filter(order_id=orderId)
#         except Transaction.DoesNotExist:
#             order_id = None

#         if order_id: 
#             update = order_id.update(status=cur_status)
#             status_code = status.HTTP_200_OK
#             if cur_status == 0:
#                 update = order_id.update(arrive_time=timezone.now())
#             return Response({'Status': Status}, status=status_code)
#         else:
#             status_code = status.HTTP_404_NOT_FOUND 
#             return Response({'Error': 'Can not find the order.'}, status=status_code)

class payoutMethod(generics.GenericAPIView):
    queryset = WithdrawChannel.objects.all()
    serializer_class = payoutMethodSerialize
    permission_classes = (AllowAny,)
    
    def post(self, request, *args, **kwargs):
        
        serializer = payoutMethodSerialize(self.queryset, many=True)
        currency = self.request.POST['currency']
        url = api + apiVersion +'/' + merchantId + payout_url + currency + '/methods'
        headers = {'Accept': 'application/json'}
        # username = self.request.GET.get('username')
        # userId = CustomUser.objects.filter(username=username)
        
        message = bytes(merchantId + '|' + currency, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        
        my_hmac = generateHash(secret, message)
        delay = kwargs.get("delay", 5)
        #retry
        success = False
        for x in range(3):
            try:
                r = requests.get(url, headers=headers, params = {
                    # 'userId' : userId,
                    'hmac' : my_hmac,
                    
                })
                if r.status_code == 200:
                    success = True
                    break
            except ValueError:
                logger.info('Request failed {} time(s).wating for %s seconds before retrying again'.format(x+1))
               
                sleep(delay) 
        if not success:
            logger.error('Failed to complete a request to get qaicash payout Method...')
        # Handle error

        data = r.json()
        #print (my_hmac)
        
        for x in data:
            for y in WithdrawChannel._meta.get_field('currency').choices:
                if x['limits'].get('currency') == y[1]:
                    cur_val = y[0]
            create = WithdrawChannel.objects.get_or_create(
            thirdParty_name= 3,
            method=x['method'],
            currency=cur_val,
            min_amount=x['limits'].get('minTransactionAmount'),
            max_amount=x['limits'].get('maxTransactionAmount'),
            
            )

        return Response(data)
class getPayoutBankList(generics.GenericAPIView):
    queryset = WithdrawChannel.objects.all()
    serializer_class = payoutBanklistSerialize
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = payoutBanklistSerialize(self.queryset, many=True)
        currency = self.request.POST['currency']
        method = self.request.POST['method']
        url = api + apiVersion +'/' + merchantId + payout_url +currency + '/methods/' + method + '/banks'
        headers = {'Accept': 'application/json'}
        message = bytes(merchantId + '|' + currency, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        my_hmac = generateHash(secret, message)
        delay = kwargs.get("delay", 5)
        #retry
        success = False
        for x in range(3):
            try:
                r = requests.get(url, headers=headers, params = {
                    'hmac' : my_hmac,
                })
                if r.status_code == 200:
                    success = True
                    break
            except ValueError:
                logger.info('Request failed {} time(s).wating for %s seconds before retrying again'.format(x+1))
                
                sleep(delay) 
        if not success:
            logger.error('Failed to complete a request to get qaicash Payout Bank List...')   
        data = r.json()
        
        return Response(data)
class getPayoutBankLimits(generics.GenericAPIView):
    queryset = WithdrawChannel.objects.all()
    serializer_class = payoutBanklimitsSerialize
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = payoutBanklimitsSerialize(self.queryset, many=True)
        bank = self.request.POST['bank']
        currency = self.request.POST['currency']
        method = self.request.POST['method']
        url =  api + apiVersion +'/' + merchantId + payout_url + currency + '/methods/' + method + '/banks/' + bank + '/limits'
        headers = {'Accept': 'application/json'}
        message = bytes(merchantId + '|' + currency, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        my_hmac = generateHash(secret, message)
        delay = kwargs.get("delay", 5)
         #retry
        success = False
        for x in range(3):
            try:
                r = requests.get(url, headers=headers, params = {
                    'hmac' : my_hmac,
                })
                if r.status_code == 200:
                    success = True
                    break
            except ValueError:
                logger.info('Request failed {} time(s)'.format(x+1))
                logger.debug("wating for %s seconds before retrying again")
                sleep(delay)  
        if not success:
            logger.error('Failed to complete a request to get qaicash Payout Bank Limits...')
        if r.status_code == 500:
            logger.info('Response content is not in JSON format.')
            data = '500 Internal Error'    
        else:
            data = r.json()

        if r.status_code == 201:  
            
            for x in WithdrawChannel._meta.get_field('currency').choices:

                if rdata['currency'] == x[1]:
                    cur_val = x[0]

            create = WithdrawChannel.objects.save(
                thirdParty_name= 3,
                method= method,
                currency= cur_val,
                min_amount=data['minTransactionAmount'],
                max_amount=data['maxTransactionAmount'],
            
            )
        else:
            logger.error('The request information is nor correct for qaicash Payout Bank Limits, please try again')
        
        return Response(data)