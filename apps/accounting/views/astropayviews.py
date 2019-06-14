from django.shortcuts import render
from django.http import HttpResponse
from django.views import View, generic
from users.models import CustomUser
from ..models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from utils.constants import *

from ..serializers import astroPaymentStatusSerialize
from django.conf import settings
import requests,json
import logging
import time
import hmac
import struct
import hashlib 
import xml.etree.ElementTree as ET
from time import sleep

logger = logging.getLogger('django')
secretkey = ASTROPAY_SECREATE
currencyConversion = {
    "CNY": 0,
    "USD": 1,
    "PHP": 2,
    "IDR": 3
}
#get hash code 
def generateHash(key, message):
    hash = hmac.new(key, msg=message, digestmod=hashlib.sha256)
    #hash.hexdigest()
    return hash.hexdigest().upper()

#new invoice api which will return an url for users to rediract
@api_view(['POST'])
@permission_classes((AllowAny,))
def astroNewInvoice(request):
    url = ASTROPAY_URL
    invoice = request.data.get('transaction_id')
    amount = request.data.get('amount')
    iduser = request.data.get('user_id')
    bank = request.data.get('bank')
    cpf = request.data.get('cpf')
    email = request.data.get('email')
    name = request.data.get('name')
    country = request.data.get('country')
    zip = ''
    address = ''
    city = ''
    state = ''
    bdate = ''
    message = bytes(str(invoice) + 'V' + str(amount) + 'I' + str(iduser) + '2' + str(bank) + '1' + str(cpf) + 'H' + str(bdate) + 'G' + str(email) + 'Y' + str(zip) + 'A' + str(address) + 'P' + str(city) + 'S' + str(state) + 'P', 'utf-8')
    secret = bytes(secretkey, 'utf-8')
    my_hmac = generateHash(secret, message)
    params = {
        "x_login":ASTROPAY_X_LOGIN,
        "x_trans_key":ASTROPAY_X_TRANS_KEY,
        "x_invoice":invoice,
        "x_amount":amount,
        "x_bank":bank,
        "x_country":country,
        "x_iduser":iduser,
        "x_cpf":cpf,
        "x_name":name,
        "x_email":email,
        "control":my_hmac,
    }
    for x in range(3):   
        r = requests.post(url, data=params)
        rdata = r.text
        print(rdata)
        tree = ET.fromstring(rdata)
        redirect_url = tree.find('link').text
        if r.status_code == 200:
            break
        elif r.status_code == 500:
            print("Request failed {} time(s)'.format(x+1)")
            print("Waiting for %s seconds before retrying again")
            sleep(delay)
        elif r.status_code == 400:
            # Handle error
            print("There was something wrong with the result")
            print(rdata)
            return Response(rdata) 
    create = Transaction.objects.get_or_create(
        order_id=invoice,
        amount=amount,
        user_id=CustomUser.objects.get(pk=iduser),
        currency= 1,
        transaction_type=0, 
        channel=2,
        status=2,
    )
    return Response({'Status': '0','Redirect url': redirect_url}) 

#payment status
@api_view(['POST'])
@permission_classes((AllowAny,))
def astroPaymentStatus(request):
    statusConversion = {
        "6": 1,
        "7": 2,
        "8": 4,
        "9": 0
    }
    url = ASTROPAY_WPS 
    invoice = request.data.get('order_id')
    params = {
            "x_login":ASTROPAY_WP_LOGIN,
            "x_trans_key":ASTROPAY_WP_TRANS_KEY,
            "x_invoice":invoice,
        }
    for x in range(3):   
        r = requests.post(url, data=params)
        rdata = r.text
        data = rdata.split('|')
        print(data)
        if r.status_code == 200:
            break
        elif r.status_code == 500:
            print("Request failed {} time(s)'.format(x+1)")
            print("Waiting for %s seconds before retrying again")
            sleep(delay)
        elif r.status_code == 400:
            # Handle error
            print("There was something wrong with the result")
            print(rdata)
            return Response(rdata)
    depositData = {
        "order_id": invoice, 
        "amount": data[3],
        "user_id":  data[1],
        "bank": data[7],
        "currency": currencyConversion[data[10]],
        "channel": 2,
        "status": statusConversion[data[0]]
    }
    serializer = astroPaymentStatusSerialize(data=depositData)
    print(serializer)
    if (serializer.is_valid()):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
