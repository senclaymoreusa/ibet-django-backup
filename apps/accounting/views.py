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

from .serializers import depositMethodSerialize, bankListSerialize
import requests,json

import hmac
import hashlib 
import base64

merchantId = '1'
currency = 'CNY'
merchantApiKey = 'secret'
apiVersion = 'v2.0'
method = 'LBT_ONLINE'

def generateHash(key, message):
    hash = hmac.new(key, msg=message, digestmod=hashlib.sha256)
    #hash.hexdigest()
    return hash.hexdigest()

class getDepositMethod(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = depositMethodSerialize

    def get(self, request, *args, **kwargs):
        url = 'https://public-services.qaicash.com/ago/integration/v2.0/' + merchantId + '/deposit/routing/' + currency + '/methods'
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
        return Response(json.dumps(data)) 

class getBankList(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = bankListSerialize

    def get(self, request, *args, **kwargs):
        url = 'https://public-services.qaicash.com/ago/integration/' + apiVersion +'/' + merchantId + '/deposit/routing/' +currency + '/methods/' + method + '/banks'
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
        return Response(json.dumps(data))