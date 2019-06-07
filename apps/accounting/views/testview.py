from django.shortcuts import render
from django.http import HttpResponse
from django.views import View, generic
from django.utils import timezone
from django.db import IntegrityError
from users.models import Game, CustomUser, Category, Config, NoticeMessage
from ..models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement

from rest_framework import status, generics, viewsets, parsers, renderers, status, serializers
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from ..serializers import paypalCreatePaymentSerialize
from django.conf import settings

import requests,json
import logging
logger = logging.getLogger('django')
CHANNEL_CHOICES = (
    (0, 'Alipay'),
    (1, 'Wechat'),
    (2, 'Card'),
    (3, 'Qaicash'),
    (4, 'Asia Pay'),
    (5, 'Paypal')
)
CURRENCY_CHOICES = (
    (0, 'CNY'),
    (1, 'USD'),
    (2, 'PHP'),
    (3, 'IDR'),
)
def test(request):
    # if request.method == "POST":
    print("++++++++++++++++++++++++++++++++++++\nHi testing\n")
    return HttpResponse("Hello, world. You're at the polls index.")

class testSerializer(serializers.HyperlinkedModelSerializer):
    thridParty_name = serializers.IntegerField(min_value=0, max_value=5)
    currency = serializers.IntegerField(min_value=0, max_value=3)
    permission_classes = (AllowAny,)

    class Meta:
        model = DepositChannel
        fields = ('thridParty_name', 'currency')

class testAPI(viewsets.ModelViewSet):
# class testAPI(generics.GenericAPIView):
    queryset = DepositChannel.objects.all()
    serializer_class = testSerializer
    
    def post(self, request, *args, **kwargs):
        print(request, args, kwargs)
        

