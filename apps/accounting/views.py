from django.shortcuts import render
from django.http import HttpResponse
from django.views import View, generic
from users.models import Game, CustomUser, Category, Config, NoticeMessage
from .models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes


from .serializers import depositMethodSerialize, bankListSerialize,bankLimitsSerialize
from django.conf import settings
import requests,json
import os

import hmac
import hashlib 
import base64

#payment
merchantId = settings.MERCHANTID
currency = settings.CURRENCY
merchantApiKey = settings.MERCHANTAPIKEY
apiVersion = settings.APIVERSION
method = settings.METHOD
api = settings.QAICASH_URL 
deposit_url = settings.DEPOSIT_URL



def generateHash(key, message):
    hash = hmac.new(key, msg=message, digestmod=hashlib.sha256)
    #hash.hexdigest()
    return hash.hexdigest()

class getDepositMethod(generics.RetrieveUpdateDestroyAPIView):
    lookup_filed = 'pk'  #id
    queryset = DepositChannel.objects.all()
    serializer_class = depositMethodSerialize
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        
        serializer = depositMethodSerialize(queryset)

        url = api + apiVersion +'/' + merchantId + deposit_url + currency + '/methods'
        headers = {'Accept': 'application/json'}
        # username = self.request.GET.get('username')
        # userId = CustomUser.objects.filter(username=username)
        
        message = bytes(merchantId + '|' + currency, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        
        my_hmac = generateHash(secret, message)
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
        url = api + apiVersion +'/' + merchantId + deposit_url +currency + '/methods/' + method + '/banks'
        headers = {'Accept': 'application/json'}
        # username = self.request.GET.get('username')
        # userId = CustomUser.objects.filter(username=username)
        message = bytes(merchantId + '|' + currency, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        my_hmac = generateHash(secret, message)

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
        queryset = DepositChannel.objects.all()
        serializer = depositMethodSerialize(queryset)
        bank = 'CMBCCN'
        
        url =  api + apiVersion +'/' + merchantId + deposit_url + currency + '/methods/' + method + '/banks/' + bank + '/limits'
        headers = {'Accept': 'application/json'}
        # username = self.request.GET.get('username')
        # userId = CustomUser.objects.filter(username=username)
        message = bytes(merchantId + '|' + currency, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        my_hmac = generateHash(secret, message)

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
            
       
