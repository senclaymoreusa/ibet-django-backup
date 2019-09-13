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
import utils.helpers as helpers

logger = logging.getLogger('django')

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


def verify_user(request):
    """
    This method is called by PaymentIQ to verify that a user is properly authenticated and retrieve user data like
    name, address, birth-date etc. The user data is needed internally by PaymentIQ for various fraud checks and also to
    enrich the data sent to the Payment Provider. Please note that the minimum required response for verify user
    needs to contain Balance (can be zero), BalanceCy, UserId and Success. The other parameter requirements will
    depend on they type of transaction.
    :param request: HTTP Request containing UserId and SessionId
    :return: JSON response containing User KYC info to be sent to Payment Provider
    """
    if request.method == "POST":
        post_data = json.loads(request.body)
        try:
            user = CustomUser.objects.get(username=post_data["userId"])
            result = {
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
                "zip": user.zipcode or "UNKNOWN",
                "country": user.country or "UNKNOWN",
                "email": user.email or "UNKNOWN",
                "dob": user.date_of_birth or "UNKNOWN",
                "mobile": user.phone or "UNKNOWN",
                "balance": user.main_wallet or "UNKNOWN",
                "balanceCy": user.currency or "UNKNOWN",
                # "locale": "en_GB",
                # "attributes": {
                #     "transaction_type": post_data["attributes"]["transactionMethod"]
                # }
            }
            return JsonResponse(result)
        except ObjectDoesNotExist as e:
            logger.error(e)
            result = {
                "success": False,
                "errCode": "000",  # custom error code (used internally by ibet)
                "errMsg": "Transaction failed: UserID does not exist"  # message explaining error
            }
            return JsonResponse(result)


def authorize(request):
    """
    This method is called by PaymentIQ so the Operator Platform can authorize a payment before it is getting processed.
    The Operator Platform should verify that the user is allowed to process and also reserve amount for future debit
    and check that the user account will not be over debited. If the Operator Platform response is success,
    then PaymentIQ will continue with processing of the payment transaction.
    If not, then PaymentIQ will decline the transaction with the status code returned by the Operator Platform.
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
                created = Transaction.objects.create(
                    user_id=user,
                    transaction_id=trans_id,
                    order_id=post_data["txId"],
                    amount=float(post_data["txAmount"]),
                    method=post_data["provider"] + ": " + post_data["txName"],
                    currency=cyConversion[post_data["txAmountCy"]],
                    transaction_type=0,  # 0 = DEPOSIT
                    channel=10,  # 10 = PaymentIQ
                    status=2,  # 2 = CREATED
                    last_updated=timezone.now()
                )
                logger.info("Recording deposit transaction request...")
                logger.info(created)
                return JsonResponse({
                    "userId": post_data["userId"],
                    "success": True,
                    "txId": post_data["txId"],
                    "merchantTxId": trans_id,
                    "authCode": auth_code
                })
            elif "withdraw" in post_data["txName"].lower():
                if float(post_data["txAmount"]) > user.main_wallet:
                    return JsonResponse({
                        "userId": post_data["userId"],
                        "success": False,
                        "txId": post_data["txId"],
                        "merchantTxId": trans_id,
                        "authCode": auth_code,
                        "errCode": "100",
                        "errMsg": "Authorize failed: not enough withdraw balance"
                    })

                created = Transaction.objects.create(
                    user_id=post_data["userId"],
                    transaction_id=trans_id,
                    order_id=post_data["txId"],
                    amount=float(post_data["txAmount"]),
                    method=post_data["provider"] + ": " + post_data["txName"],
                    currency=cyConversion[post_data["txAmountCy"]],
                    transaction_type=1,  # 1 = WITHDRAW
                    channel=10,  # 10 = PaymentIQ
                    status=2,  # 2 = CREATED
                    last_updated=timezone.now()
                )
                logger.info("Recording withdraw transaction request...")
                logger.info(created)
                return JsonResponse({
                    "userId": post_data["userId"],
                    "success": True,
                    "txId": post_data["txId"],
                    "merchantTxId": trans_id,
                    "authCode": auth_code,
                })
        except ObjectDoesNotExist as e:
            logger.info(e)
            return JsonResponse({
                "success": False,
                "errCode": "000",  # custom error code (used internally by ibet)
                "errMsg": "Authorize failed: UserID does not exist"  # message explaining error
            })


def transfer(request):
    """
    This method is called by PaymentIQ after a successfully processed transaction to credit (increase) or debit (decrease)
    a user's account balance. Note: The Operator Platform must always accept a transfer request, even if it results in
    a negative user balance because the payment transaction has already been processed by the payment provider.
    :param request: HTTP request containing user info & transaction data
        Example request:
        {
          "userId": "user_123",
          "txAmount": "100.50",
          "txAmountCy": "SEK",
          "txPspAmount": "12.50",
          "txPspAmountCy": "EUR",
          "fee": "0.50",
          "feeCy": "SEK",
          "txId": "25A0324",
          "txTypeId": "101",
          "txName": "CreditcardDeposit",
          "provider": "Neteller",
          "txRefId": "100019999A26720"
        }
    :return:
    """
    if request.method == "POST":
        post_data = json.loads(request.body)
        user = CustomUser.objects.get(username=post_data["userId"])
        try:
            if "deposit" in post_data["txName"].lower():
                matching_transaction = Transaction.objects.get(
                    user_id=user,
                    order_id=post_data["txId"],
                    amount=float(post_data["txAmount"]),
                    method=post_data["provider"] + ": " + post_data["txName"],
                    currency=cyConversion[post_data["txAmountCy"]],
                    transaction_type=0,  # 0 = DEPOSIT
                    channel=10,  # 10 = PaymentIQ
                )
                if matching_transaction.status != 2:
                    return JsonResponse({
                        "success": False,
                        "errCode": "200",  # custom error code (used internally by ibet)
                        "errMsg": "Transfer failed: duplicate Transfer action"  # message explaining error
                    })
                success = helpers.addOrWithdrawBalance(matching_transaction.user_id, matching_transaction.amount, "add")

                matching_transaction.status = 0
                matching_transaction.arrive_time = timezone.now()
                matching_transaction.last_updated = timezone.now()
                matching_transaction.remark = "Successfully deposited!"
                matching_transaction.save()

                result = {
                    "userId": post_data["userId"],
                    "success": success,
                    "txId": post_data["txId"],
                    "merchantTxId": matching_transaction.transaction_id,
                }
                return JsonResponse(result)

            elif "withdraw" in post_data["txName"].lower():
                matching_transaction = Transaction.objects.get(
                    user_id=user,
                    order_id=post_data["txId"],
                    amount=float(post_data["txAmount"]),
                    method=post_data["provider"] + ": " + post_data["txName"],
                    currency=cyConversion[post_data["txAmountCy"]],
                    transaction_type=0,  # 0 = DEPOSIT
                    channel=10,  # 10 = PaymentIQ
                )
                if matching_transaction.status != 2:
                    return JsonResponse({
                        "success": False,
                        "errCode": "200",  # custom error code (used internally by ibet)
                        "errMsg": "Transfer failed: duplicate Transfer action"  # message explaining error
                    })

                matching_transaction.status = 0
                matching_transaction.arrive_time = timezone.now()
                matching_transaction.last_updated = timezone.now()
                matching_transaction.remark = "Successfully withdrew!"
                matching_transaction.save()

                success = helpers.addOrWithdrawBalance(matching_transaction.user_id, matching_transaction.amount, "withdraw")
                if success:
                    result = {
                        "userId": post_data["userId"],
                        "success": success,
                        "txId": post_data["txId"],
                        "merchantTxId": trans_id,
                    }
                    return JsonResponse(result)
                else:
                    result = {
                        "userId": post_data["userId"],
                        "success": success,
                        "txId": post_data["txId"],
                        "merchantTxId": trans_id,
                        "errCode": "001",
                        "errMsg": "Authorize failed: not enough withdraw balance"
                    }
                    return JsonResponse(result)
        except ObjectDoesNotExist as e:
            logger.info(e)
            return JsonResponse({
                "userId": post_data["userId"],
                "success": False,
                "merchantTxId": trans_id,
                "errCode": "001",  # custom error code (used internally by ibet)
                "errMsg": "Transfer failed: Transaction does not exist"  # message explaining error
            })


def cancel(request):
    if request.method == "POST":
        post_data = json.loads(request.body)
        user = CustomUser.objects.get(username=post_data["userId"])
        try:
            matching_transaction = Transaction.objects.get(
                user_id=user,
                order_id=post_data["txId"],
                amount=float(post_data["txAmount"]),
                method=post_data["provider"] + ": " + post_data["txName"],
                currency=cyConversion[post_data["txAmountCy"]],
                channel=10,  # 10 = PaymentIQ
            )
            matching_transaction.status = 5  # 5 = CANCELED
            matching_transaction.last_updated = timezone.now()
            matching_transaction.remark = "PSP(" + post_data["provider"] + ") rejected this " + post_data["txName"] + " request"
            result = {
                "userId": post_data["userId"],
                "success": True,
            }
            return JsonResponse(result)
        except ObjectDoesNotExist as e:
            logger.info(e)
            return JsonResponse({
                "userId": post_data["userId"],
                "success": False,
                "merchantTxId": trans_id,
                "errCode": "001",  # custom error code (used internally by ibet)
                "errMsg": "Transfer failed: Transaction does not exist"  # message explaining error
            })
