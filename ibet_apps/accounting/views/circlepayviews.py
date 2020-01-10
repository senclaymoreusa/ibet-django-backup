import requests, json, logging, random, hmac, hashlib, datetime

from time import sleep, gmtime, strftime


from requests.auth import HTTPBasicAuth
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import parsers, renderers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.utils.translation import ugettext_lazy as _
from users.models import CustomUser
from accounting.models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from accounting.serializers import astroPaymentStatusSerialize
from utils.constants import *
import utils.helpers as helpers
from users.views.helper import *
logger = logging.getLogger('django')
userCode = CIRCLEPAY_USERCODE
api_key = CIRCLEPAY_API_KEY
email = CIRCLEPAY_EMAIL


# creates record of deposit request, status set to CREATED
def create_deposit(request):
    if request.method == "GET":
        return HttpResponse("You are at the endpoint for CirclePay reserve payment.")
    
    if request.method == "POST":  # can only allow post requests
        try:
            user_id = CustomUser.objects.get(username=request.user.username)
            if checkUserBlock(user_id):
                    errorMessage = _('The current user is blocked!')
                    data = {
                        "errorCode": ERROR_CODE_BLOCK,
                        "errorMsg": {
                            "detail": [errorMessage]
                        }
                    }
                    return JsonResponse(data)
            body = json.loads(request.body)
            logger.info(body["trans_id"])
            amount = body["amount"]
            transaction_id = body["trans_id"]
            
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
                "success": True,
                "record_created": created,
                "message": "Created new record" if created else "Did not create new record",
                "user": request.user.username,
                "transaction_id": transaction_id
            })
        except Exception as e:
            logger.critical("FATAL__ERROR::CirclePay::Unable to create deposit", exc_info=True, stack_info=1)
            return JsonResponse({
                "success": False,
                "message": "Exception occured"
            })



def confirm_payment(request):
    if request.method == "GET":
        logger.info("Hello GET")
        return HttpResponse(status=404)
    if request.method == "POST":
        logger.info("[" + str(datetime.datetime.now()) + "] Received confirm_payment() callback from CirclePay")
        transaction_data = json.loads(request.body)
        logger.info(transaction_data)
        # query for transaction in ibet db
        try:
            matching_transaction = Transaction.objects.get(
                transaction_id=transaction_data["partner_tran_id"],
                amount=transaction_data["amount"],
            )
            logger.info("Found matching transaction!")
            if matching_transaction.order_id != '0':
                return JsonResponse({"code": "888", "message": "Callback rejected: Transaction already processed"})

            if transaction_data["status"] == '00':  # deposit successful
                matching_transaction.status = 0
                matching_transaction.remark = "Deposit successful!"
                helpers.addOrWithdrawBalance(matching_transaction.user_id, transaction_data["amount"], "add")

            if transaction_data["status"] == '01' or transaction_data["status"] == '04':  # deposit pending
                matching_transaction.status = 3
                matching_transaction.remark = "Deposit pending!"
            if transaction_data["status"] == '02':  # deposit canceled
                matching_transaction.status = 5
                matching_transaction.remark = "Deposit canceled!"
            if transaction_data["status"] == '03':  # deposit failed
                matching_transaction.status = 1
                matching_transaction.remark = "Deposit failed!"

            payment_method = matching_transaction.method + "_" + transaction_data["method"]
            matching_transaction.order_id = transaction_data["tran_id"]
            matching_transaction.method = payment_method
            matching_transaction.arrive_time = timezone.datetime.strptime(transaction_data["time"], '%Y-%m-%d %H:%M:%S')
            matching_transaction.last_updated = timezone.now()
            matching_transaction.save()

            # update transaction record status
            return JsonResponse({
                "success": True,
                "message": "Received confirmation of payment"
            })
        except ObjectDoesNotExist as e:
            logger.critical("FATAL__ERROR::CirclePay::Unable to confirm payment", exc_info=1, stack_info=1)
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
