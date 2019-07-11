import requests, json, logging, random, hmac, struct, hashlib, boto3, xml.etree.ElementTree as ET
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



#get hash code 
def generateHash(key, message):
    hash = hmac.new(key, msg=message, digestmod=hashlib.sha256)
    #hash.hexdigest()
    return hash.hexdigest()

# create money order with astropay card
def create_deposit(request):
    if (request.method == "POST"):
        depositURL = "http://api.besthappylife.biz/MerchantTransfer"
        merchantInfo = "M0130"
        

        return
