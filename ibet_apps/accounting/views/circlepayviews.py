import requests, json, logging, random, hmac, struct, hashlib, xml.etree.ElementTree as ET
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone

from rest_framework import parsers, renderers, status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes

from users.models import CustomUser
from ..models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from ..serializers import astroPaymentStatusSerialize
from utils.constants import *
from time import sleep, gmtime, strftime

userCode = CIRCLEPAY_USERCODE
api_key = CIRCLEPAY_API_KEY
email = CIRCLEPAY_EMAIL

def create_deposit(request):
    if request.method == "GET":
        return HttpResponse("You are at the endpoint for LINEpay reserve payment.")
    
    if request.method == "POST": # can only allow post requests
        transId = "test-order-123"
        amount = "123"

        message = bytes(email + transId + amount, "utf-8")
        token = hmac.new(bytes(api_key, "utf-8"), msg=message, digestmod=hashlib.sha256).hexdigest()
        print(token)
        url = "https://gateway.seasolutions.ph/payment/" + userCode + "/?partner_tran_id=" + transId + "&amount=" + amount + "&token=" + token

        response = requests.get(url)
        print(response.status_code)
        print(response.text)

        return JsonResponse({"message": "hi"})

def check_transaction(request):
    if request.method == "POST":
        transId = "test-order-123" # request.POST.data
        url = "https://api.seasolutions.ph/transaction/" + transId

        response = requests.get(url)
        print(response.status_code)
        print(response.text)
    
        return JsonResponse(response.json())