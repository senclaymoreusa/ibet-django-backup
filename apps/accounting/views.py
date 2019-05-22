from django.shortcuts import render
from django.http import HttpResponse
from django.views import View, generic
from django.utils import timezone
from users.models import Game, CustomUser, Category, Config, NoticeMessage
from .models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes


from .serializers import depositMethodSerialize, bankListSerialize,bankLimitsSerialize,submitDepositSerialize,submitPayoutSerialize
from django.conf import settings
import requests,json
import os
import datetime,time
import hmac
import hashlib 
import base64
import logging

#payment
merchantId = settings.MERCHANTID
currency = settings.CURRENCY
merchantApiKey = settings.MERCHANTAPIKEY
apiVersion = settings.APIVERSION
method = settings.METHOD
api = settings.QAICASH_URL 
deposit_url = settings.DEPOSIT_URL

logger = logging.getLogger('django')

def generateHash(key, message):
    hash = hmac.new(key, msg=message, digestmod=hashlib.sha256)
    #hash.hexdigest()
    return hash.hexdigest()

class getDepositMethod(generics.RetrieveUpdateDestroyAPIView):
    queryset = DepositChannel.objects.all()
    serializer_class = depositMethodSerialize
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        
        serializer = depositMethodSerialize(self.queryset)

        url = api + apiVersion +'/' + merchantId + deposit_url + currency + '/methods'
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
                    'deviceType' : 'PC',
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
            
            create = DepositChannel.objects.get_or_create(
            thridParty_name= 3,
            method=x['method'],
            currency=3,
            min_amount=x['limits'].get('minTransactionAmount'),
            max_amount=x['limits'].get('maxTransactionAmount'),
            
        )
        return Response(data)

class getBankList(generics.RetrieveUpdateDestroyAPIView):
    queryset = DepositChannel.objects.all()
    serializer_class = bankListSerialize
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = depositMethodSerialize(self.queryset)
        url = api + apiVersion +'/' + merchantId + deposit_url +currency + '/methods/' + method + '/banks'
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
                    'deviceType' : 'PC',
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
        
        return Response(data)

class getBankLimits(generics.RetrieveUpdateDestroyAPIView):
    queryset = DepositChannel.objects.all()
    serializer_class = depositMethodSerialize
    
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = depositMethodSerialize(self.queryset)
        bank = 'CMBCCN'
        
        url =  api + apiVersion +'/' + merchantId + deposit_url + currency + '/methods/' + method + '/banks/' + bank + '/limits'
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
                    'deviceType' : 'PC',
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


        for x in DepositChannel._meta.get_field('currency').choices:

            if data['currency'] == x[1]:
                cur_val = x[0]
            
        create = DepositChannel.objects.get_or_create(
            thridParty_name= 3,
            method= method,
            currency= cur_val,
            min_amount=data['minTransactionAmount'],
            max_amount=data['maxTransactionAmount'],
            
        )
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
        print(url)
        dateTime = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%z')
        
        orderId = self.request.POST.get('order_id')
        amount =self.request.POST.get('amount')
        language = self.request.POST.get('language')
        userId = self.request.POST.get('user_id')
        mymethod = self.request.POST.get('method')
        list = [merchantId, orderId, amount, currency, dateTime, userId, method]
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
            'messageAuthenticationCode': my_hmac,
        })
        
        rdata = r.json()

        if rdata.get("ok"):
            user = CustomUser.objects.get(username=rdata['depositTransaction']['depositorUserId'])
            for x in Transaction._meta.get_field('currency').choices:
                if rdata["depositTransaction"]["currency"] == x[1]:
                    cur_val = x[0]

            for y in Transaction._meta.get_field('status').choices:
                if rdata["depositTransaction"]["status"] ==y[1]:
                    cur_status = y[0] 
            create = Transaction.objects.get_or_create(
                order_id= rdata['orderId'],
                #transaction_id=rdata["depositTransaction"]["transactionId"],
                request_time=rdata["depositTransaction"]["dateCreated"],
                amount=rdata["depositTransaction"]["amount"],
                status=cur_status,
                user_id=user,
                method= rdata["depositTransaction"]["depositMethod"],
                currency= cur_val,
                transaction_type=0,
            )
        else:
            logger.error("Please check the data you input, something is wrong.")
        
        print(rdata)
        
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
        print(url)
        dateTime = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%z')
        
        orderId = self.request.POST.get('order_id')
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
            'redirectUrl': 'https://www.google.com',
            'messageAuthenticationCode': my_hmac,
        })
        
        rdata = r.json()
        
        user = CustomUser.objects.get(username=rdata['payoutTransaction']['userId'])
        if r.status_code == 201:   
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
            )
        else:
            logger.error('post information is not correct, please try again')
        
        return Response(rdata)   
