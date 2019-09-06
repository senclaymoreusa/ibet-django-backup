import base64
import random
import hashlib
import logging
import requests
import json
import os
from datetime import datetime
from time import sleep
from dotenv import load_dotenv

from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from users.models import CustomUser
from utils.constants import *
from accounting.models import Transaction


# This method is called by PaymentIQ to verify that a user is properly authenticated and retrieve user data like
# name, address, birth-date etc. The user data is needed internally by PaymentIQ for various fraud checks and also to
# enrich the data sent to the Payment Provider. Please note that the minimum required response for verify user
# needs to contain Balance (can be zero), BalanceCy, UserId and Success. The other parameter requirements will
# depend on they type of transaction.
def verify_user(request):
    if request.method == "POST":
        print("received post for verify/user")
        post_data = json.loads(request.body)
        print("POST request payload:")
        print(post_data)
        try:
            # user = CustomUser.objects.get(username=post_data["userId"])
            return JsonResponse({
                "userId": str(user),
                "success": True,
                "userCat": "VIP_SE",  # ?
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
    if request.method == "POST":
        print("received post for authorize")
        return JsonResponse({"msg": "hi"})


def transfer(request):
    if request.method == "POST":
        print("received post for transfer")
        return JsonResponse({"msg": "hi"})


def cancel(request):
    if request.method == "POST":
        print("received post for cancel")
        return JsonResponse({"msg": "hi"})
