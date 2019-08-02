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

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone

from users.models import CustomUser
from utils.constants import *
from ..models import Transaction

load_dotenv()
logger = logging.getLogger('django')


def generate_md5(code):
    res = hashlib.md5(code.encode()).hexdigest()
    return res


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_qr_code(request):
    if request.method =="POST":
        logger.info("Attempting to get QR Code to make deposit via Payzod...")
        body = json.loads(request.body)
        amount = body.get("amount")
        url = PAYZOD_API_URL
        now = datetime.now()
        ref_no = "test-payzod-order-" + request.user.username + str(random.randint(0, 1000))
        ref_date = now.strftime("%Y%m%d%H%M%S")
        if os.getenv("ENV") == "local":
            payload = {
                "merchant_id": PAYZOD_MERCHANT_ID,
                "paytype": "QR",
                "ref_no": ref_no,
                "ref_date": ref_date,
                "passkey": generate_md5(ref_no+ref_date+PAYZOD_PASSKEY),
                "amount": "123.45",
                "merchant_name": "ibet2019"
            }
        else:  # use dev credentials
            payload = {
                "merchant_id": PAYZOD_MERCHANT_ID,
                "paytype": "QR",
                "ref_no": ref_no,
                "ref_date": ref_date,
                "passkey": generate_md5(ref_no + ref_date + PAYZOD_PASSKEY),
                "amount": "123.45",
                "merchant_name": "ibet2019"
            }
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

        matching_transaction = Transaction.objects.get(
            transaction_id=req.get("ref_no"),
            amount=req.get("amount")
        )
        logger.info("Found matching transaction!")

        if req.get("response_code") == "001":
            matching_transaction.status = 0
            matching_transaction.remark = req.get("response_msg")
        else:
            matching_transaction.status = 1
            matching_transaction.remark = req.get("response_msg")

        matching_transaction.order_id = req.get("transaction_no")
        matching_transaction.arrive_time = timezone.now()
        matching_transaction.last_updated = timezone.now()
        matching_transaction.save()
        logger.info("Received confirmation of payment!")

        return JsonResponse({
            "responseCode": req.get("response_code"),
            "responseMesg": req.get("response_msg")
        })

    return HttpResponse("Invalid Request")


def check_trans_status(request):
    if request.method == "POST":
        logger.info("Attempting to check status of transaction...")
        body = json.loads(request.body)
        ref_no = body["ref_no"]
        ref_date = body["ref_date"]
        url = PAYZOD_API_URL + "inquiry.php"
        payload = {
            "merchant_id": PAYZOD_MERCHANT_ID,
            "ref_no": ref_no,
            "ref_date": ref_date,
            "passkey": generate_md5(ref_no + ref_date + PAYZOD_PASSKEY)
        }

        for x in range(3):
            if os.getenv("ENV") == "local":
                r = requests.post(url, params=payload, verify=False)  # verify=False for sandbox
            else:
                r = requests.post(url, params=payload)
            if r.status_code == 200:
                logger.info(r.content)
        return
