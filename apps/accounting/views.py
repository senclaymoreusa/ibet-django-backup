from django.shortcuts import render
from django.http import HttpResponse
from django.views import View, generic
from users.models import Game, CustomUser, Category, Config, NoticeMessage

from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics

from .serializers import depositMethodSerialize, bankListSerialize,bankLimitsSerialize
from django.conf import settings
import requests,json
import os

import hmac
import hashlib 
import base64

merchantId = '1'
currency = 'IDR'
merchantApiKey = 'secret'
apiVersion = 'v2.0'
method = 'LBT_ONLINE'

#payment
merchantId = settings.MERCHANTID
currency = settings.CURRENCY
merchantApiKey = settings.MERCHANTAPIKEY
apiVersion = settings.APIVERSION
method = settings.METHOD
api = settings.QAICASH_URL 
deposit_url = settings.DEPOSIT_URL

class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'

def generateHash(key, message):
    hash = hmac.new(key, msg=message, digestmod=hashlib.sha256)
    #hash.hexdigest()
    return hash.hexdigest()

class getDepositMethod(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = depositMethodSerialize

    def get(self, request, *args, **kwargs):
        url = api + apiVersion +'/' + merchantId + deposit_url + currency + '/methods'
        headers = {'Accept': 'application/json'}
        username = self.request.GET.get('username')
        userId = CustomUser.objects.filter(username=username)
        
        message = bytes(merchantId + '|' + currency, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        
        my_hmac = generateHash(secret, message)

        r = requests.get(url, headers=headers, params = {
            'userId' : userId,
            'hmac' : my_hmac,
            'deviceType' : 'PC',
        })
        data = r.json()
        #print (my_hmac)
        if r.status_code == 503:
            raise ServiceUnavailable
        else:
            return Response(json.dumps(data)) 

class getBankList(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = bankListSerialize

    def get(self, request, *args, **kwargs):
        url = api + apiVersion +'/' + merchantId + deposit_url +currency + '/methods/' + method + '/banks'
        headers = {'Accept': 'application/json'}
        username = self.request.GET.get('username')
        userId = CustomUser.objects.filter(username=username)
        message = bytes(merchantId + '|' + currency, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        my_hmac = generateHash(secret, message)

        r = requests.get(url, headers=headers, params = {
            'userId' : userId,
            'hmac' : my_hmac,
            'deviceType' : 'PC',
        })
        data = r.json()
        #print (my_hmac)
        if r.status_code == 503:
            raise ServiceUnavailable
        else:
            return Response(json.dumps(data))

class getBankLimits(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = bankLimitsSerialize

    def get(self, request, *args, **kwargs):
        bank = 'CMBCCN'
        url =  api + apiVersion +'/' + merchantId + deposit_url + currency + '/methods/' + method + '/banks/' + bank + '/limits'
        headers = {'Accept': 'application/json'}
        username = self.request.GET.get('username')
        userId = CustomUser.objects.filter(username=username)
        message = bytes(merchantId + '|' + currency, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        my_hmac = generateHash(secret, message)

        r = requests.get(url, headers=headers, params = {
            'userId' : userId,
            'hmac' : my_hmac,
            'deviceType' : 'PC',
        })
        data = r.json()
        #print (my_hmac)
        if r.status_code == 503:
            raise ServiceUnavailable
        else:
            return Response(json.dumps(data))
            
       
