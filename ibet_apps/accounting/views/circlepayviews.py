import requests, json, logging, random, hmac, hashlib

from time import sleep, gmtime, strftime
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone

from rest_framework import parsers, renderers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from users.models import CustomUser
from ..models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from ..serializers import astroPaymentStatusSerialize
from utils.constants import *


userCode = CIRCLEPAY_USERCODE
api_key = CIRCLEPAY_API_KEY
email = CIRCLEPAY_EMAIL

def create_deposit(request):
    if request.method == "GET":
        return HttpResponse("You are at the endpoint for CirclePay reserve payment.")
    
    if request.method == "POST":  # can only allow post requests
        transId = "testOrder"+str(random.randint(0, 1241241))
        amount = "999999"
        encrypt_msg = email + transId + amount
        print(encrypt_msg)
        message = bytes(encrypt_msg, "utf-8")
        token = hmac.new(bytes(api_key, "utf-8"), msg=message, digestmod=hashlib.sha256).hexdigest()
        print(token)
        url = "https://gateway.circlepay.ph/payment/" + userCode + "/?partner_tran_id=" + transId + "&amount=" + amount + "&token=" + token
        print(url)
        response = requests.post(url)
        print(response.status_code)

        return HttpResponse(response.content)


def confirm_payment(request):
    if request.method == "POST":
        transaction_data = json.loads(request.body)
        # matching_transaction = Transaction.objects.get(transaction_id=transactionId)
        print(transaction_data)
        return

def check_transaction(request):
    if request.method == "POST":
        transId = "test-order-123" # request.POST.data
        url = "https://api.circlepay.ph/transaction/" + transId

        response = requests.get(url)
        print(response.status_code)
        print(response.text)
    
        return JsonResponse(response.json())
