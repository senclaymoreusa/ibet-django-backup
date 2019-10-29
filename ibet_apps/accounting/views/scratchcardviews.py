import base64
import random
import hmac
import hashlib
import logging
import requests
import json
import os
from datetime import datetime
from time import sleep

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from users.models import CustomUser
from utils.constants import *
import utils.helpers as helpers
from accounting.models import Transaction
from users.views.helper import *
from django.utils.translation import ugettext_lazy as _
logger = logging.getLogger('django')


# creates record of deposit request, status set to CREATED
def create_deposit(request):
    if request.method == "GET":
        # print(request.META['HTTP_REFERER'])
        return HttpResponse("You are at the endpoint for ScratchCard reserve payment.")

    if request.method == "POST":  # can only allow post requests
        logger.info("Creating Deposit...")
        logger.info(request.body)
        body = json.loads(request.body)
        pin = body["pin"]
        serial = body["serial"]
        operator = body["operator"]
        amount = str(body["amount"])
        # print(request.META['HTTP_REFERER'])
        message = bytes(SCRATCHCARD_PARTNER_ID+operator+pin+serial+amount, 'utf-8')
        secret = bytes(SCRATCHCARD_CODE, 'utf-8')
        sign = hmac.new(secret, msg=message, digestmod=hashlib.sha256).hexdigest()
        trans_id = request.user.username+"-"+timezone.datetime.today().isoformat()+"-"+str(random.randint(0,10000000))
        if checkUserBlock(CustomUser.objects.get(username=request.user.username).pk):
            errorMessage = _('The current user is blocked!')
            data = {
                "errorCode": ERROR_CODE_BLOCK,
                "errorMsg": {
                    "detail": [errorMessage]
                }
            }
            return JsonResponse(data)
        r = requests.get(SCRATCHCARD_URL, params={
            'partner': SCRATCHCARD_PARTNER_ID,
            'pin': pin,
            'serial': serial,
            'operator': operator,
            'amount': amount,
            'sign': sign,
            'partner_tran_id': trans_id
        })
        res_json = r.json()
        # print(r.url)
        # print(r.status_code)
        # print(res_json)
        # print(request.user.username)

        if res_json["status"] == 6:
            user_id = CustomUser.objects.get(username=request.user.username)
            obj, created = Transaction.objects.get_or_create(
                user_id=user_id,
                transaction_id=trans_id,
                order_id=res_json["id"],
                amount=int(amount),
                method="ScratchCard",
                channel=9,  # ScratchCard
                currency=8,  # VND
                transaction_type=0,  # DEPOSIT
                status=2,  # CREATED
                request_time=timezone.now(),
                last_updated=timezone.now()
            )
            return JsonResponse({
                "created": created,
                "status": res_json["status"],
                "msg": {
                    "eng": res_json["message_eng"],
                    "vn": res_json["message"]
                },
                "api_response": res_json,
            })
        elif res_json["status"] == 1:
            user_id = CustomUser.objects.get(username=request.user.username)
            obj, created = Transaction.objects.get_or_create(
                user_id=user_id,
                transaction_id=trans_id,
                order_id=res_json["id"],
                amount=int(amount),
                method="ScratchCard",
                channel=9,  # ScratchCard
                currency=8,  # VND
                transaction_type=0,  # DEPOSIT
                status=0,  # SUCCESS
                request_time=timezone.now(),
                last_updated=timezone.now()
            )
            return JsonResponse({
                "created": created,
                "status": res_json["status"],
                "msg": {
                    "eng": res_json["message_eng"],
                    "vn": res_json["message"]
                },
                "api_response": res_json,
            })
        else:
            return JsonResponse({
                "created": False,
                "status": res_json["status"],
                "msg": {
                    "eng": res_json["message_eng"],
                    "vn": res_json["message"]
                },
                "api_response": res_json,
            })


def confirm_transaction(request):
    if request.method == "POST":
        logger.info("Received callback request from TTT ScratchCard servers")
        # logger.info("Refferer: " + request.META["HTTP_REFERER"])
        # logger.info("Host: " + request.META["REMOTE_HOST"])
        logger.info(request.POST)
        try:
            matching_transaction = Transaction.objects.get(
                transaction_id=request.POST["partner_tran_id"],
                order_id=request.POST["id"]
            )
            logger.info("Found matching transaction:")
            logger.info(matching_transaction)
            matching_transaction.status = 3  # PENDING

            if request.POST["status"] == '4':
                logger.info({'msg': 'Card already used!'})
                matching_transaction.status = 1  # FAILED
                matching_transaction.remark = 'Card already used!'
            if request.POST["status"] == '5':
                logger.info({'msg': 'Wrong PIN'})
                matching_transaction.status = 1  # FAILED
                matching_transaction.remark = 'Wrong PIN'
            if request.POST["status"] == '7':
                logger.info({'msg': 'Wrong Serial'})
                matching_transaction.status = 1  # FAILED
                matching_transaction.remark = 'Wrong Serial'
            if request.POST["status"] == '8':
                logger.info({'msg': 'Wrong Amount'})
                matching_transaction.status = 1  # FAILED
                matching_transaction.remark = 'Wrong Amount'
            if request.POST["status"] == '1':
                logger.info({'msg': 'Confirming Transaction!'})
                matching_transaction.status = 0  # success
                matching_transaction.amount = request.POST["amount"]
                matching_transaction.remark = 'Successfully Deposited!'
                # update user balance after updating matching transaction
                helpers.addOrWithdrawBalance(matching_transaction.user_id, request.POST["amount"], "add")

            matching_transaction.arrive_time = timezone.now()
            matching_transaction.last_updated = timezone.now()
            matching_transaction.save()
            return JsonResponse({"msg": "received response"})
        except ObjectDoesNotExist as e:
            logger.error(e)
            logger.info("matching transaction not found / does not exist")
            return JsonResponse({"message": "Could not find matching transaction"})
