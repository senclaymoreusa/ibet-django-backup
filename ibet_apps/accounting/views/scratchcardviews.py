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

from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from users.models import CustomUser
from utils.constants import *
from ..models import Transaction

logger = logging.getLogger('django')


# creates record of deposit request, status set to CREATED
def create_deposit(request):
    if request.method == "GET":
        return HttpResponse("You are at the endpoint for ScratchCard reserve payment.")

    if request.method == "POST":  # can only allow post requests
        body = json.loads(request.body)
        pin = body["pin"]
        serial = body["serial"]
        operator = body["operator"]
        amount = body["amount"]

        message = bytes(SCRATCHCARD_PARTNER_ID+operator+pin+serial+amount, 'utf-8')
        secret = bytes(SCRATCHCARD_CODE, 'utf-8')
        sign = hmac.new(secret, msg=message, digestmod=hashlib.sha256).hexdigest()
        trans_id = request.user.username + "ScratchCard"

        r = requests.get(SCRATCHCARD_URL, params={
            'partner': SCRATCHCARD_PARTNER_ID,
            'pin': pin,
            'serial': serial,
            'operator': operator,
            'amount': amount,
            'sign': sign,
            'partner_tran_id': trans_id
        })

        print(r.url)
        print(r.status_code)
        print(r.json())
        #
        # user_id = CustomUser.objects.get(username=request.user.username)
        # obj, created = Transaction.objects.get_or_create(
        #     user_id=user_id,
        #     transaction_id=transaction_id,
        #     amount=float(amount),
        #     method="ScratchCard",
        #     channel=9,  # ScratchCard
        #     currency=8,  # VND
        #     transaction_type=0,  # DEPOSIT
        #     status=2,  # CREATED
        #     request_time=timezone.now(),
        #     last_updated=timezone.now()
        # )
        return JsonResponse(r.json())
        # return JsonResponse({
        #     "response_msg": r.json(),
        #     "record_created": created,
        #     "message": "Created new record" if created else "Failed to create new record",
        #     "user": request.user.username,
        #     "transaction_id": transaction_id
        # })
