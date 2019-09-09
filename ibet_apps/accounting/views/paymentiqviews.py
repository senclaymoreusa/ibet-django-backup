import base64
import random
import hashlib
import logging
import requests
import json
import os
from uuid import uuid1
from datetime import datetime
from time import sleep
from dotenv import load_dotenv

from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from accounting.models import Transaction
from users.models import CustomUser
from utils.constants import *


cyConversion = {
    'CNY': 0,
    'USD': 1,
    'THB': 2,
    'IDR': 3,
    'HKD': 4,
    'AUD': 5,
    'MYR': 6,
    'VND': 7,
    'MMK': 8,
    'XBT': 9,
    'NOK': 10,
    'SEK': 11,
    'GBP': 12,
    'EUR': 13
}


# This method is called by PaymentIQ to verify that a user is properly authenticated and retrieve user data like
# name, address, birth-date etc. The user data is needed internally by PaymentIQ for various fraud checks and also to
# enrich the data sent to the Payment Provider. Please note that the minimum required response for verify user
# needs to contain Balance (can be zero), BalanceCy, UserId and Success. The other parameter requirements will
# depend on they type of transaction.
def verify_user(request):
    """
    Function called by PIQ for
    :param request:
    :return:
    """
    if request.method == "POST":
        print("received post for verify/user")
        post_data = json.loads(request.body)
        print("POST request payload:")
        print(post_data)
        try:
            user = CustomUser.objects.get(username=post_data["userId"])
            return JsonResponse({
                "userId": str(user),
                "success": True,
                "userCat": user.member_status,  # ?
                "kycStatus": "Approved",  # ?
                "sex": user.gender or "UNKNOWN",
                "firstName": user.first_name or "UNKNOWN",
                "lastName": user.last_name or "UNKNOWN",
                "street": (user.street_address_1 + user.street_address_2) or "UNKNOWN",
                "city": user.city or "UNKNOWN",
                "state": user.state or "UNKNOWN",
                "zip": username.zipcode or "UNKNOWN",
                "country": username.country or "UNKNOWN",
                "email": user.email or "UNKNOWN",
                "dob": user.date_of_birth or "UNKNOWN",
                "mobile": user.phone or "UNKNOWN",
                "balance": user.main_wallet or "UNKNOWN",
                "balanceCy": user.currency or "UNKNOWN"
                # "locale": "en_GB",
                # "attributes": {
                #     "allow_manual_payout": "true"
                # }
            })
        except ObjectDoesNotExist as e:
            logger.error(e)
            return JsonResponse({
                "success": False,
                "errCode": "001",  # custom error code (used internally by ibet)
                "errMsg": "Transaction failed: UserID does not exist"  # message explaining error
            })


# This method is called by PaymentIQ so the Operator Platform can authorize a payment before it is getting processed.
# The Operator Platform should verify that the user is allowed to process and also reserve amount for future debit
# and check that the user account will not be over debited. If the Operator Platform response is success,
# then PaymentIQ will continue with processing of the payment transaction.
# If not, then PaymentIQ will decline the transaction with the status code returned by the Operator Platform.
def authorize(request):
    """
    :param request: dictionary object containing user info and deposit/withdraw amount
        Example request:
        {
          "userId": "user_123",
          "txAmount": "100.50",
          "txAmountCy": "SEK",
          "txId": "12345",
          "txTypeId": 108,
          "txName": "CreditcardDeposit",
          "provider": "BamboraGa"
        }
    :return JsonResponse: either successfully authorize transaction or fail to authorize
    """
    if request.method == "POST":
        post_data = json.loads(request.body)
        auth_code = str(uuid1())
        try:
            user = CustomUser.objects.get(username=post_data["userId"])
            trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(
                random.randint(0, 10000000))
            if "deposit" in post_data["txName"].lower():
                print("Authorizing deposit request for user " + post_data["userId"] + "...")

                Transaction.objects.create(
                    user_id=post_data["userId"],
                    transaction_id=trans_id,
                    amount=float(post_data["txAmount"]),
                    method=post_data["provider"] + ": " + post_data["txName"],
                    currency=cyConversion[post_data["txAmountCy"]],
                    transaction_type=0,  # 0 = DEPOSIT
                    channel=10,  # 10 = PaymentIQ
                    status=2,  # 2 = CREATED
                    last_updated=timezone.now()
                )

                return JsonResponse({
                    "userId": post_data["userId"],
                    "success": True,
                    "txId": post_data["txId"],
                    "merchantTxId": trans_id,
                    "authCode": auth_code
                })
            elif "withdraw" in post_data["txName"].lower():
                print("Authorizing withdraw request for user " + post_data["userId"] + "...")

                Transaction.objects.create(
                    user_id=post_data["userId"],
                    transaction_id=trans_id,
                    amount=float(post_data["txAmount"]),
                    method=post_data["provider"] + ": " + post_data["txName"],
                    currency=cyConversion[post_data["txAmountCy"]],
                    transaction_type=1,  # 0 = DEPOSIT
                    channel=10,  # 10 = PaymentIQ
                    status=2,  # 2 = CREATED
                    last_updated=timezone.now()
                )
                return JsonResponse({
                    "userId": post_data["userId"],
                    "success": False,
                    "txId": post_data["txId"],
                    "merchantTxId": trans_id,
                    "authCode": auth_code,
                    "errCode": "001",
                    "errMsg": "Authorize failed: not enough withdraw balance"
                })
        except ObjectDoesNotExist as e:
            logger.info(e)
            return JsonResponse({
                "success": False,
                "errCode": "001",  # custom error code (used internally by ibet)
                "errMsg": "Authorize failed: UserID does not exist"  # message explaining error
            })


def transfer(request):
    """
    This method is called by PaymentIQ after a successfully processed transaction to credit (increase) or debit (decrease)
    a user's account balance. Note: The Operator Platform must always accept a transfer request, even if it results in
    a negative user balance because the payment transaction has already been processed by the payment provider.
    :param request:
    :return:
    """
    if request.method == "POST":
        print("received post for transfer")
        return JsonResponse({"msg": "hi"})


def cancel(request):
    if request.method == "POST":
        print("received post for cancel")
        return JsonResponse({"msg": "hi"})
