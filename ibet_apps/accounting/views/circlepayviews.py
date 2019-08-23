import requests, json, logging, random, hmac, hashlib

from time import sleep, gmtime, strftime
from datetime import datetime

from requests.auth import HTTPBasicAuth
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import parsers, renderers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from users.models import CustomUser
from accounting.models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from accounting.serializers import astroPaymentStatusSerialize
from utils.constants import *

logger = logging.getLogger('django')
userCode = CIRCLEPAY_USERCODE
api_key = CIRCLEPAY_API_KEY
email = CIRCLEPAY_EMAIL


# creates record of deposit request, status set to CREATED
def create_deposit(request):
    if request.method == "GET":
        return HttpResponse("You are at the endpoint for CirclePay reserve payment.")
    
    if request.method == "POST":  # can only allow post requests
        body = json.loads(request.body)
        logger.info(body["trans_id"])
        amount = body["amount"]
        transaction_id = body["trans_id"]

        print(request.user)
        user_id = CustomUser.objects.get(username=request.user.username)
        obj, created = Transaction.objects.get_or_create(
            user_id=user_id,
            transaction_id=transaction_id,
            amount=float(amount),
            method="CirclePay",
            channel=7,  # CirclePay
            currency=8,  # VND
            transaction_type=0,  # DEPOSIT
            status=2,  # CREATED
            request_time=timezone.now(),
            last_updated=timezone.now()
        )

        return JsonResponse({
            "record_created": created,
            "message": "Created new record" if created else "Failed to create new record",
            "user": request.user.username,
            "transaction_id": transaction_id
        })


def confirm_payment(request):
    if request.method == "GET":
        logger.info("Hello GET")
        return HttpResponse("You are at the endpoint for CirclePay confirm payment")
    if request.method == "POST":
        logger.info("Hello POST")
        transaction_data = json.loads(request.body)
        logger.info(transaction_data)
        # query for transaction in ibet db
        try:
            matching_transaction = Transaction.objects.get(
                transaction_id=transaction_data["partner_tran_id"],
                amount=transaction_data["amount"],
            )
            logger.info("Found matching transaction!")
            if transaction_data["status"] == '00':  # deposit successful
                matching_transaction.status = 0
            if transaction_data["status"] == '01' or transaction_data["status"] == '04':  # deposit pending
                matching_transaction.status = 3
            if transaction_data["status"] == '02':  # deposit canceled
                matching_transaction.status = 5
            if transaction_data["status"] == '03':  # deposit failed
                matching_transaction.status = 1

            payment_method = matching_transaction.method + "_" + transaction_data["method"]
            matching_transaction.order_id = transaction_data["tran_id"]
            matching_transaction.method = payment_method
            matching_transaction.arrive_time = timezone.datetime.strptime(transaction_data["time"], '%Y-%m-%d %H:%M:%S')
            matching_transaction.last_updated = timezone.now()
            matching_transaction.save()

            # update transaction record status
            return JsonResponse({"message": "Received confirmation of payment"})
        except ObjectDoesNotExist as e:
            logger.error(e)
            return JsonResponse({"message": "Could not find matching transaction"})


def check_transaction(request):
    if request.method == "POST":

        body = json.loads(request.body)
        trans_id = body["trans_id"]
        url = CIRCLEPAY_CHECK_STATUS_URL + trans_id
        logger.info(trans_id)
        logger.info(url)
        secret = bytes(CIRCLEPAY_API_KEY, 'utf-8')
        msg = bytes(CIRCLEPAY_EMAIL, 'utf-8')
        pw = (hmac.new(secret, msg=msg, digestmod=hashlib.sha256)).hexdigest()
        logger.info(pw)
        response = requests.get(url, auth=HTTPBasicAuth(CIRCLEPAY_EMAIL, pw))

        logger.info(response.status_code)
        logger.info(response.text)
        if response.status_code != 200:
            return HttpResponse("Failed to check transaction status.")
        return JsonResponse(response.json())
