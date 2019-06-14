from django.shortcuts import render
from django.http import HttpResponse
from django.views import View, generic
from django.utils import timezone
from django.db import IntegrityError
from users.models import Game, CustomUser, Category, Config, NoticeMessage
from ..models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes


from ..serializers import paypalCreatePaymentSerialize,paypalgetOrderSerialize,paypalExecutePaymentSerialize
from django.conf import settings
import requests,json
import logging
import time
logger = logging.getLogger('django')

# paypalrestsdk.configure({
#   "mode": settings.PAYPAL_MODE, 
#   "client_id": settings.PAYPAL_CLIENT_ID,
#   "client_secret": settings.PAYPAL_CLIENT_SECRET })

username = settings.PAYPAL_CLIENT_ID
password = settings.PAYPAL_CLIENT_SECRET
url = settings.PAYPAL_SANDBOX_URL
host_url = settings.HOST_URL

def getAccessToken():
    client_id = username
    client_secret = password
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en_US',
        'Content-Type':'application/x-www-form-urlencoded',
    }
    body = {
            'grant_type' : 'client_credentials'
    }
    r = requests.post(url + 'v1/oauth2/token', body, headers, auth=(client_id, client_secret))
    rdata = r.json()
    return rdata["access_token"]

class paypalCreatePayment(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = paypalCreatePaymentSerialize
    permission_classes = (AllowAny,)
 
    def post(self, request, *args, **kwargs):
        serializer = paypalCreatePaymentSerialize(self.queryset, many=True)
        #orderId = self.request.POST['order_id']
        amount = self.request.POST.get('amount')
        currency = self.request.POST.get('currency')
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + getAccessToken()
        }
        body = {
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
                },
            "redirect_urls": {
            "return_url": host_url + "deposit/",
            "cancel_url": host_url + "deposit/"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "paypal deposit",
                        "sku": "item",
                        "price": amount,
                        "currency": currency,
                        "quantity": 1}]},
                "amount": {
                    "total": amount,
                    "currency": currency},
                "description": "This is the payment transaction description."
            }]
        }
        success = False
        for x in range(3):
            try:
                r = requests.post(url + 'v1/payments/payment', headers=headers, data = json.dumps(body))
                if r.status_code == 201:
                    success = True
                    break
            except ValueError:
                logger.info('Request failed {} time(s)'.format(x+1))
                logger.debug("wating for %s seconds before retrying again")
                time.sleep(delay) 
        rdata = r.json()
        if r.status_code == 201:
            
            userId = CustomUser.objects.get(username=self.request.POST.get('user'))
            if rdata["state"] == 'created':  
                for x in Transaction._meta.get_field('currency').choices:

                    if currency == x[1]:
                        cur_val = x[0]
            if rdata["state"] == 'created':    
                create = Transaction.objects.get_or_create(
                    user_id=userId,
                    #order_id= rdata["id"],
                    amount=amount,
                    method= rdata["payer"]["payment_method"],
                    currency= cur_val,
                    transaction_type=0, 
                    channel=5,
                    status=2,
                )
                print("Payment[%s] created successfully" % (rdata['id']))
                for link in rdata["links"]:
                   if link["rel"] == "approval_url": 
                       approval_url = str(link["href"])
                       token = approval_url.split("token=")[1]
                       print("Redirect for approval: %s" % (token))

        else:
            logger.error('The request information is nor correct, please try again')
        return Response(rdata)

class paypalGetOrder(APIView):
    queryset = Transaction.objects.all()
    serializer_class = paypalgetOrderSerialize
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        serializer = paypalgetOrderSerialize(self.queryset, many=True)
        order_id = self.request.POST.get('order_id')
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + getAccessToken()
        }
        success = False
        for x in range(3):
            try:
                r = requests.post(url + 'v2/checkout/orders/' + order_id + '/capture', headers=headers)
                if r.status_code == 201:
                    success = True
                    break
            except ValueError:
                logger.info('Request failed {} time(s)'.format(x+1))
                logger.debug("wating for %s seconds before retrying again")
                time.sleep(delay) 
        
        rdata = r.json()
        if r.status_code == 201:
            userId = CustomUser.objects.get(username=self.request.POST.get('user'))
            if rdata["status"] == 'COMPLETED':    
                for x in Transaction._meta.get_field('currency').choices:
                    if rdata["purchase_units"][0]["payments"]["captures"][0]["amount"]["currency_code"] == x[1]:
                        cur_val = x[0]
            if rdata["status"] == 'COMPLETED': 
                create = Transaction.objects.update_or_create(
                    user_id=userId,
                    payer_id=rdata["payer"]["payer_id"],
                    order_id= rdata["id"],
                    request_time= rdata["purchase_units"][0]["payments"]["captures"][0]["create_time"],
                    arrive_time= rdata["purchase_units"][0]["payments"]["captures"][0]["update_time"],
                    amount=rdata["purchase_units"][0]["payments"]["captures"][0]["amount"]["value"],
                    currency= cur_val,
                    transaction_type=0, 
                    channel=5,
                    status=6,
                )
                print("Payment[%s] capture successfully" % (rdata['id']))

        else:
            logger.error('The request information is nor correct, please try again')
        return Response(rdata)

class paypalExecutePayment(APIView):
    queryset = Transaction.objects.all()
    serializer_class = paypalExecutePaymentSerialize
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        serializer = paypalExecutePaymentSerialize(self.queryset, many=True)
        payer_id = self.request.POST.get('payer_id')
        payment_id = self.request.POST.get('payment_id')
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + getAccessToken()
        }
        success = False
        for x in range(3):
            try:
                r = requests.post(url + 'v1/payments/payment/' + payment_id + '/execute', headers=headers, data={
                    'payer_id': payer_id,
                })
                if r.status_code == 201:
                    success = True
                    break
            except ValueError:
                logger.info('Request failed {} time(s)'.format(x+1))
                logger.debug("wating for %s seconds before retrying again")
                time.sleep(delay) 
        rdata = r.json()
        if r.status_code == 201:
            userId = CustomUser.objects.get(username=self.request.POST.get('user'))
            if rdata["state"] == 'approved':    
                for x in Transaction._meta.get_field('currency').choices:
                    if currency == x[1]:
                        cur_val = x[0]
                create = Transaction.objects.update_or_create(
                    user_id=userId,
                    payer_id=payer_id,
                    order_id= rdata["id"],
                    request_time= rdata["create_time"],
                    arrive_time= rdata["update_time"],
                    amount=rdata["transactions"]["total"],
                    method= rdata["payer"]["payment_method"],
                    currency= cur_val,
                    transaction_type=0, 
                    channel=5,
                    status=4,
                )
                print("Payment[%s] execute successfully" % (rdata['id']))

        else:
            logger.error('The request information is nor correct, please try again')
        return Response(rdata)