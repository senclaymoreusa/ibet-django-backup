import requests,json, os, datetime, time, hmac, hashlib, base64, logging, uuid

from django.shortcuts import render
from django.http import HttpResponse
from django.views import View, generic
from django.utils import timezone
from django.db import IntegrityError
from django.conf import settings

from rest_framework import status, generics, parsers, renderers
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes

from utils.constants import *

from users.models import Game, CustomUser, Category, Config, NoticeMessage
from ..models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from ..serializers import depositMethodSerialize, bankListSerialize,bankLimitsSerialize,submitDepositSerialize,submitPayoutSerialize, payoutTransactionSerialize,approvePayoutSerialize,depositThirdPartySerialize, payoutMethodSerialize,payoutBanklistSerialize,payoutBanklimitsSerialize

from time import sleep, gmtime, strftime


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
}
REDIRECTURL = "http://localhost:3000/withdraw/success/"
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
        #retry
        for x in range(3):
            r = requests.get(url, headers=headers, params = {
                # 'userId' : userId,
                'hmac' : my_hmac,
                'deviceType' : 'PC',
            })
            responseJson = r.json()
            if r.status_code == 200:
                success = True
                break
            if r.status_code == 400 or r.status_code == 401:
                success = True
                # Handle error
                logger.info("Failed to complete a request for getDepositMethod...")
                logger.error(responseJson)
                return Response(responseJson)
            if r.status_code == 500:
                print("Request failed {} time(s)'.format(x+1)")
                print("Waiting for %s seconds before retrying again")
                sleep(delay)
        if not success:
            return Response(responseJson)
        for x in responseJson:
            print(x)
            depositData = {
                "thridParty_name": QAICASH_NAME, # third party name is hard-fixed to match the channel choice in models
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
            print("currency: " + currency_long + ", method: " + method_long)
            url = api + apiVersion +'/' + merchantId + deposit_url + currency_long + '/methods/' + method_long + '/banks'
            print(url)
            headers = {'Accept': 'application/json'}

            # username = self.request.GET.get('username')
            # userId = CustomUser.objects.filter(username=username)

            message = bytes(merchantId + '|' + currency_long, 'utf-8')
            secret = bytes(merchantApiKey, 'utf-8')

            my_hmac = generateHash(secret, message) # hmac format for qaicash api

            delay = kwargs.get("delay", 5)

            for x in range(3):
                r = requests.get(url, headers=headers, params = {
                    # 'userId' : userId,
                    'hmac' : my_hmac,
                    'deviceType' : 'PC',
                })
                data = r.json() # r.json() converts the string/byte return of the response into a JSON object
                if r.status_code == 200:
                    return Response(data)            
                if r.status_code == 400 or r.status_code == 401:
                    logger.info("Failed to complete a request for retrieving available bank lists (getBankList())")
                    logger.error(data)
                    return Response(data)
                if r.status_code == 500:
                    logger.info('Request failed {} time(s)'.format(x+1))
                    logger.debug("wating for %s seconds before retrying again")
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
        print(bank, currency, method)
        url =  api + apiVersion +'/' + merchantId + deposit_url + currency + '/methods/' + method + '/banks/' + bank + '/limits/'
        headers = {'Accept': 'application/json'}

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
                'deviceType' : 'PC',
            })
            print("bank limits response: ")
            print(r)
            if r.status_code == 200:
                success = True
                break
            if r.status_code == 400 or r.status_code == 401:
                print("There was something wrong with the result")
                print(r.text)
                logger.info("Failed to complete a request for retrieving available deposit methods..")
                logger.error(r.text)
                return Response(data)
            if r.status_code == 500:
                logger.info('Request failed {} time(s)'.format(x+1))
                logger.debug("wating for %s seconds before retrying again")
                sleep(delay) 

        if not success:
            logger.info("Failed to complete a request for getBankLimits()")
            return Response({"error" : "Qaicash API returned a status code of 500", "message": r.text})
        else:
            data = r.json()
            
        # save a single bank limit into the database...?
        depositData = {
            "thridParty_name": QAICASH_NAME,
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
        orderId = "ibet" + strftime("%Y%m%d%H%M%S", gmtime())
        amount =self.request.POST.get('amount')
        language = self.request.POST.get('language')
        userId = self.request.POST.get('user_id')
        mymethod = self.request.POST.get('method')
        list = [merchantId, orderId, amount, currency, dateTime, userId, mymethod]
        message = '|'.join(str(x) for x in list)
        
        mymessage = bytes(message, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        my_hmac = generateHash(secret, mymessage)
        delay = kwargs.get("delay", 5)
        
        first_name = self.request.GET.get('first_name')
        email = self.request.GET.get('email')
        
        
        r = requests.post(url, headers=headers, data = {
            'orderId' : orderId,
            'amount' : amount,
            'currency' : currency,
            'dateTime': dateTime,
            'language': language,
            'depositorUserId': userId,
            'depositorTier': '0',
            'depositMethod':  mymethod,
            'depositorEmail': CustomUser.objects.filter(email=email),
            'depositorName': CustomUser.objects.filter(first_name=first_name),
            'redirectUrl': 'https://www.google.com',
            'callbackUrl': 'http://128dbbc7.ngrok.io/api/qaicash/transaction_status',
            'messageAuthenticationCode': my_hmac,
        })
        
        rdata = r.json()
        print(rdata)
        
        create = Transaction.objects.create(
            order_id= rdata['depositTransaction']['orderId'],
            transaction_id=rdata["depositTransaction"]["transactionId"],
            amount=rdata["depositTransaction"]["amount"],
            status=2,
            user_id=CustomUser.objects.get(pk=userId),
            method= rdata["depositTransaction"]["depositMethod"],
            currency= curr,
            transaction_type=0,
            channel=3,
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
        mymethod = self.request.POST.get('method')
        list = [merchantId, orderId, amount, currency, dateTime, userId]
        message = '|'.join(str(x) for x in list)
        
        mymessage = bytes(message, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        my_hmac = generateHash(secret, mymessage)
        delay = kwargs.get("delay", 5)
        
        first_name = self.request.GET.get('first_name')
        email = self.request.GET.get('email')
         #retry
        success = False
        r = requests.post(url, headers=headers, data = {
            'orderId' : orderId,
            'amount' : amount,
            'currency' : currency,
            'dateTime': dateTime,
            'language': language,
            'userId': userId,
            'depositorTier': '0',
            'payoutMethod':  mymethod,
            'withdrawerEmail': CustomUser.objects.filter(email=email),
            'withdrawerName': CustomUser.objects.filter(first_name=first_name),
            'redirectUrl': REDIRECTURL,
            'messageAuthenticationCode': my_hmac,
        })
        
        rdata = r.json()
        if r.status_code == 201:  
            user = CustomUser.objects.get(username=rdata['payoutTransaction']['userId'])
         
            for x in Transaction._meta.get_field('currency').choices:
                if rdata["payoutTransaction"]["currency"] == x[1]:
                    cur_val = x[0]

            for y in Transaction._meta.get_field('status').choices:
                if rdata["payoutTransaction"]["status"] ==y[1]:
                    cur_status = y[0] 
            create = Transaction.objects.get_or_create(
                order_id= rdata["payoutTransaction"]['orderId'],
                request_time=rdata["payoutTransaction"]["dateCreated"],
                amount=rdata["payoutTransaction"]["amount"],
                status=cur_status,
                user_id=user,
                method= rdata["payoutTransaction"]["payoutMethod"],
                currency= cur_val,
                transaction_type=1,
                channel=3,
            )
        else:
            logger.error('post information is not correct, please try again')

        print(rdata)
        return Response(rdata)
           
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
            logger.info('Failed to complete a request for payout transaction')
        # Handle error

        rdata = r.json()
        print(rdata)
        if r.status_code == 200:  
            user = CustomUser.objects.get(username=rdata['userId'])   
            update_data = Transaction.objects.get(order_id=rdata['orderId'],
                                                method=rdata["payoutMethod"],                                                                      
            )
            update_data.transaction_id=rdata['transactionId']
            update_data.request_time=rdata["dateCreated"]
            update_data.status=6
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
                logger.info('Request failed {} time(s)'.format(x+1))
                logger.debug("wating for %s seconds before retrying again")
                sleep(delay) 
        if not success:
            logger.info('Failed to complete a request for payout transaction')
        # Handle error

        rdata = r.json()
        print(rdata)
        user = CustomUser.objects.get(username=rdata['userId'])   
        update_data = Transaction.objects.get(order_id=rdata['orderId']                                                                  
        )
        update_data.transaction_id=rdata['transactionId']
        update_data.request_time=rdata["dateUpdated"]
        update_data.status=4
        update_data.save()
        
        return Response(rdata)
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
                logger.info('Request failed {} time(s)'.format(x+1))
                logger.debug("wating for %s seconds before retrying again")
                sleep(delay)  
        if not success:
            logger.info('Failed to complete a request for payout transaction')
        # Handle error

        rdata = r.json()
        print(rdata)
        if r.status_code == 201:  
            
            for x in Transaction._meta.get_field('currency').choices:

                if rdata['currency'] == x[1]:
                    cur_val = x[0]
            for y in Transaction._meta.get_field('status').choices:
                if rdata["depositTransaction"]["status"] ==y[1]:
                    cur_status = y[0] 

            user = CustomUser.objects.get(username=rdata['userId'])   
            create = Transaction.objects.get_or_create(
                order_id= rdata['orderId'],
                request_time=rdata["dateCreated"],
                amount=rdata["amount"],
                status=cur_status,
                user_id=user,
                method= rdata["payoutMethod"],
                currency= cur_val,
                transaction_type=1,
                review_status=2,
                channel=3,
            )
        else:
            logger.error('The request information is nor correct, please try again')
        
        
        return Response(rdata)
class getDepositTransaction(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = payoutTransactionSerialize
    permission_classes = [AllowAny,]
    

    def post(self, request, *args, **kwargs):
        serializer = payoutTransactionSerialize(self.queryset, many=True)
        
        orderId = self.request.POST['order_id']
        message = bytes(merchantId + '|' + orderId, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        
        my_hmac = generateHash(secret, message)
        url =  api + apiVersion +'/' + merchantId + '/deposit/' + orderId + '/mac/' + my_hmac
        headers = {'Accept': 'application/json'}
         #retry
        success = False
        for x in range(3):
            try:
                r = requests.get(url, headers=headers)
                if r.status_code == 200:
                    success = True
                    break
            except ValueError:
                logger.info('Request failed {} time(s)'.format(x+1))
                logger.debug("wating for %s seconds before retrying again")
                sleep(delay) 
        if not success:
            logger.info('Failed to complete a request for payout transaction')
        # Handle error

        rdata = r.json()
        print(rdata)
        
        for x in Transaction._meta.get_field('currency').choices:

            if rdata['currency'] == x[1]:
                cur_val = x[0]
        
        update_data = Transaction.objects.get(order_id=rdata['orderId'],amount=rdata["amount"],method= rdata["depositMethod"],status=2)
        update_data.status=6
        update_data.request_time=rdata["dateCreated"]
        update_data.save()
      
        return Response(rdata)

class transactionStatusUpdate(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = depositThirdPartySerialize
    permission_classes = [AllowAny,]
     
    def post(self, request, *args, **kwargs):
        print("result:")
        serializer = self.serializer_class(self.get_queryset(), many=True)
        mystatus = self.request.POST['status']
        method=self.request.POST['method']
        amount=self.request.POST['amount']
        user = CustomUser.objects.get(username=self.request.POST['user_id'])  
        for x in Transaction._meta.get_field('status').choices:
                if mystatus == x[1]:
                    cur_status = x[0] 
        order = self.request.POST['order_id']
        order_id = Transaction.objects.get(order_id=order)

        try: 
            order_id = Transaction.objects.filter(order_id=self.request.POST['order_id'])
        except Transaction.DoesNotExist:
            order_id = None

        if order_id:          
            update = order_id.update(status=cur_status)
            status_code = status.HTTP_200_OK
        else:
            status_code = status.HTTP_404_NOT_FOUND 

        return Response({'details': 'successful update'}, status=status_code)

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
                logger.info('Request failed {} time(s)'.format(x+1))
                logger.debug("wating for %s seconds before retrying again")
                sleep(delay) 
        if not success:
            logger.info('Failed to complete a request for...')
        # Handle error

        data = r.json()
        #print (my_hmac)
        
        for x in data:
            for y in WithdrawChannel._meta.get_field('currency').choices:
                if x['limits'].get('currency') == y[1]:
                    cur_val = y[0]
            create = WithdrawChannel.objects.get_or_create(
            thridParty_name= 3,
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
                logger.info('Request failed {} time(s)'.format(x+1))
                logger.debug("wating for %s seconds before retrying again")
                sleep(delay) 
        if not success:
            logger.info('Failed to complete a request for...')   
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
            logger.info('Failed to complete a request for...')
        if r.status_code == 500:
            print('Response content is not in JSON format.')
            data = '500 Internal Error'    
        else:
            data = r.json()

        if r.status_code == 201:  
            
            for x in WithdrawChannel._meta.get_field('currency').choices:

                if rdata['currency'] == x[1]:
                    cur_val = x[0]

            create = WithdrawChannel.objects.save(
                thridParty_name= 3,
                method= method,
                currency= cur_val,
                min_amount=data['minTransactionAmount'],
                max_amount=data['maxTransactionAmount'],
            
            )
        else:
            logger.error('The request information is nor correct, please try again')
        
        return Response(data)