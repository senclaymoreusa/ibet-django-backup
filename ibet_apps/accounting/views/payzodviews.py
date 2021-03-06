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
from users.views.helper import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from users.models import CustomUser
from accounting.models import Transaction
from utils.constants import *
import utils.helpers as helpers
from rest_framework.response import Response
load_dotenv()
logger = logging.getLogger('django')


def generate_md5(code):
    res = hashlib.md5(code.encode()).hexdigest()
    return res


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_qr_code(request):
    if request.method == "POST":
        logger.info("Attempting to get QR Code to make deposit via Payzod...")
        body = json.loads(request.body)
        amount = body.get("amount")
        url = PAYZOD_API_URL
        now = timezone.datetime.today()
        ref_no = request.user.username+"-"+timezone.datetime.today().isoformat()+"-"+str(random.randint(0, 10000000))
        ref_date = now.strftime("%Y%m%d%H%M%S")
        payload = {
            "merchant_id": PAYZOD_MERCHANT_ID,
            "paytype": "QR",
            "ref_no": ref_no,
            "ref_date": ref_date,
            "passkey": generate_md5(ref_no + ref_date + PAYZOD_PASSKEY),
            "amount": amount,
            "merchant_name": PAYZOD_MERCHANT_NAME
        }
        if checkUserBlock(CustomUser.objects.get(username=request.user.username)):
            errorMessage = _('The current user is blocked!')
            data = {
                "errorCode": ERROR_CODE_BLOCK,
                "errorMsg": {
                    "detail": [errorMessage]
                }
            }
            return Response(data)

        logger.info(payload)
        for x in range(3):
            if os.getenv("ENV") == "local":
                r = requests.post(url, params=payload, verify=False)  # verify=False for sandbox
            else:
                r = requests.post(url, params=payload)
            # logger.info(r.content)
            if r.status_code == 200:
                if r.headers["content-type"] == "image/png":
                    userId = CustomUser.objects.get(username=request.user.username)
                    obj, created = Transaction.objects.get_or_create(
                        user_id=userId,
                        transaction_id=ref_no,
                        amount=float(amount),
                        method="Payzod QR Code",
                        currency=2,    # 2 = THB
                        transaction_type=0,    # 0 = DEPOSIT
                        channel=6,     # 6 = PAYZOD
                        status=2,    # 2 = CREATED
                        last_updated=timezone.now()
                    )
                    print("created?: " + str(created))
                    print("transaction data: " + str(obj))
                    logger.info("created?: " + str(created))
                    logger.info("transaction data: " + str(obj))

                    response = HttpResponse(content=base64.b64encode(r.content), content_type="image/png")
                    # response = HttpResponse()
                    return response
                else:
                    return HttpResponse(r.text)
            elif r.status_code == 400:
                return HttpResponse(r.text)
            elif r.status_code == 500:
                sleep(5)
            logger.warning("Warning::Payzod::Failed to reach Payzod servers")
            return HttpResponse("Failed to reach Payzod servers")


def confirm_payment(request):
    if request.method == "GET":
        logger.info(request.GET)
        logger.info("Hello, GET request received on payzod confirm_payment()")
        return HttpResponse("You are at the endpoint for Payzod confirm payment")
        # query for transaction in ibet db
        # update transaction record status
    if request.method == "POST":
        logger.info("Hello, POST request received on payzod confirm_payment()")
        logger.info(request.POST)
        req = request.POST
        try:
            matching_transaction = Transaction.objects.get(
                transaction_id=req.get("ref_no"),
                amount=req.get("amount")
            )
            logger.info("Found matching transaction!")
            if matching_transaction.order_id != '0':
                return JsonResponse({
                    "responseCode": "202",
                    "responseMesg": "Transaction already exists"
                })

            # success
            if req.get("response_code") == "001":
                matching_transaction.status = 0
                matching_transaction.remark = req.get("response_msg")
                matching_transaction.order_id = req.get("transaction_no")
                matching_transaction.arrive_time = timezone.now()
                matching_transaction.last_updated = timezone.now()
                matching_transaction.save()
                logger.info("Finished updating transaction in DB!")

                logger.info("Updating user balance...")
                helpers.addOrWithdrawBalance(matching_transaction.user_id, req.get("amount"), "add")

                return JsonResponse({
                    "responseCode": "000",
                    "responseMesg": req.get("response_msg")
                })
            else:  # failure
                matching_transaction.status = 1
                matching_transaction.remark = req.get("response_msg")
                matching_transaction.order_id = req.get("transaction_no")
                matching_transaction.arrive_time = timezone.now()
                matching_transaction.last_updated = timezone.now()
                matching_transaction.save()
                logger.info("Finished updating transaction in DB!")

                return JsonResponse({
                    "responseCode": "888",
                    "responseMesg": req.get("response_msg")
                })


        except ObjectDoesNotExist as e:
            logger.critical("FATAL__ERROR::Payzod::Payment confirmation failed", exc_info=1, stack_info=1)
            return JsonResponse({"message": "Could not find matching transaction"})

    return HttpResponse("Invalid Request")
