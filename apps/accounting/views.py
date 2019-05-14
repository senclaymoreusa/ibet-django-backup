from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from users.models import Game, CustomUser, Category, Config, NoticeMessage

from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.permissions import IsAuthenticated, AllowAny

import requests,json

import hmac
import hashlib 
import base64

merchantId = '1'
currency = 'CNY'
merchantApiKey = 'secret'
apiVersion = 'v2.0'


class getDepositMethod(View):
    
    def get(self, request, *args, **kwargs):
        url = 'https://public-services.qaicash.com/ago/integration/v2.0/' + merchantId + '/deposit/routing/' + currency + '/methods'
        headers = {'Accept': 'application/json'}
        username = self.request.GET.get('username')
        userId = CustomUser.objects.filter(username=username)
        
        message = bytes(merchantId + '|' + currency, 'utf-8')
        secret = bytes(merchantApiKey, 'utf-8')
        hash = hmac.new(secret, message, hashlib.sha256)
        hash.hexdigest()

        r = requests.get(url, headers=headers, params = {
            'userId' : userId,
            'hmac' : base64.b64encode(hash.digest()),
            'deviceType' : 'PC',
        })
        key = json.loads(r.text)
    

        return HttpResponse(key)


