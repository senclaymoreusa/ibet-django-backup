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

CIRCLEPAY_DEPOSIT_URL = "https://gateway.circlepay.ph/payment/"
userCode = CIRCLEPAY_USERCODE
api_key = CIRCLEPAY_API_KEY
email = CIRCLEPAY_EMAIL


def create_deposit(request):
    if request.method == "GET":
        return HttpResponse("You are at the endpoint for CirclePay reserve payment.")
    
    if request.method == "POST":  # can only allow post requests
        body = json.loads(request.body)
        trans_id = "testOrder"+str(random.randint(0, 1241241))
        amount = body["amount"]
        # print(amount)
        encrypt_msg = email + trans_id + amount

        message = bytes(encrypt_msg, "utf-8")
        token = hmac.new(bytes(api_key, "utf-8"), msg=message, digestmod=hashlib.sha256).hexdigest()

        url = CIRCLEPAY_DEPOSIT_URL + userCode + "/?partner_tran_id=" + trans_id + "&amount=" + amount + "&token=" + token
        # print(url)
        response = requests.post(url)

        return JsonResponse({
            "url": response.url
        })

def confirm_payment(request):
    if request.method == "GET":
        print("Hello GET")
        return HttpResponse("You are at the endpoint for CirclePay confirm payment")
    if request.method == "POST":
        print("Hello POST")
        print(request.POST)
        print(request.body)
        transaction_data = json.loads(request.body)
        # query for transaction in ibet db

        # matching_transaction = Transaction.objects.get(transaction_id=transactionId)

        # update transaction record status
        print(transaction_data)
        return

def check_transaction(request):
    if request.method == "POST":
        trans_id = "test-order-123" # request.POST.data
        url = "https://api.circlepay.ph/transaction/" + trans_id

        response = requests.get(url)
        print(response.status_code)
        print(response.text)
    
        return JsonResponse(response.json())
