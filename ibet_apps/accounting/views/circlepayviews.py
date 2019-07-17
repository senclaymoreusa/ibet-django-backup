import requests, json, logging, random, hmac, struct, hashlib, xml.etree.ElementTree as ET
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone

from rest_framework import parsers, renderers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes

from users.models import CustomUser
from ..models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from ..serializers import astroPaymentStatusSerialize
from utils.constants import *
from time import sleep, gmtime, strftime


def create_deposit(request):
    if request.method == "GET":
        return HttpResponse("You are at the endpoint for LINEpay reserve payment.")
    
    if request.method == "POST": # can only allow post requests
        userCode = ""
        transId = ""
        amount = ""
        depositURL = "https://gateway.seasolutions.ph/payment/" + userCode + "/?partner_tran_id=" + transId + "&amount=" + amount

        payload = {
            "email": "",
            "api_key": ""
        }
        # response = requests.post(depositURL, json=payload, headers=headers)

        return JsonResponse({"message": "hi"})