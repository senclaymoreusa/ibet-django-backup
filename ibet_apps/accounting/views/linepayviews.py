import os, requests, json, random, logging, time, boto3

from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.utils import timezone
from django.conf import settings

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from accounting.models import Transaction
from users.models import CustomUser
from utils.constants import *
from utils.aws_helper import *

from botocore.exceptions import ClientError, NoCredentialsError


logger = logging.getLogger('django')

HOMEPAGE_URL = LOCALHOST if os.getenv("ENV") == "local" else DEV_URL
CONFIRM_URL = "/deposit/success"

DEPOSIT = 0
THB = 2
LINE_PAY = 1
CREATED = 2


config = getThirdPartyKeys(settings.AWS_S3_ADMIN_BUCKET, settings.PATH_TO_KEYS)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reserve_payment(request):
    logger.info(request)
    
    if request.method == "GET":
        return HttpResponse("You are at the endpoint for LINEpay reserve payment.")
    
    if request.method == "POST": # can only allow post requests
        requestURL = LINE_PAYMENTS_SANDBOX_URL + "request" # prepare headers + request to LINE pay server
        headers = {
            "X-LINE-ChannelId": config["LINE"]["CHANNEL_ID"],
            "X-LINE-ChannelSecret": config["LINE"]["CHANNEL_SECRET"]
        }

        # parse POST payload
        body = json.loads(request.body)
        amount = float(body.get("amount"))
        if (amount < 200) or (amount > 30000):
            return JsonResponse({"errorMsg": "Amount not within maximum or minimum"})

        # generate unique orderID
        trans_id = (timezone.datetime.today().isoformat()+"-"+request.user.username+"line-web-payment-"+str(random.randint(0,10000)))
        logger.info("amount: " + str(amount) + ", order-id: " + trans_id)
        payload = {
            "productName": "iBet-Orion-Test",
            "productImageUrl": PRODUCT_IMG_URL,
            "amount": amount,
            "currency": "THB",
            "confirmUrl": HOMEPAGE_URL + CONFIRM_URL,
            "orderId": trans_id,
        }
        for attempt in range(3):
            response = requests.post(requestURL, json=payload, headers=headers)
            res_json = response.json()
            if response.status_code == 200: # store temp transaction into db with status of created/pending
                if res_json["returnCode"] == "0000":
                    userId = CustomUser.objects.get(username=request.user.username)
                    obj, created = Transaction.objects.get_or_create(
                        user_id=userId,
                        transaction_id=trans_id,
                        order_id=res_json["info"]["transactionId"],
                        amount=float(amount),
                        method="LINEpay",
                        currency=THB,
                        transaction_type=DEPOSIT,
                        channel=LINE_PAY,
                        status=CREATED,
                        last_updated=timezone.now()
                    )
                    logger.info("created?: " + str(created))
                    logger.info("transaction data: " + str(obj))

                break
            else:
                time.sleep(5)
        return JsonResponse(res_json)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment(request):
    logger.info("In confirm payment API call")
    logger.info(request)
    if (request.method == "GET"):
        return HttpResponse("You are at the endpoint for LINEpay confirm payment.")
    if (request.method == "POST"):
        if not config:
            return JsonResponse({"Error": "Missing LINEPay API keys"})
        headers = {
            "X-LINE-ChannelId": config["LINE_CHANNEL_ID"],
            "X-LINE-ChannelSecret": config["LINE_CHANNEL_SECRET"]
        }

        body = json.loads(request.body)

        # find matching transaction
        transactionId = body.get("transactionId")
        logger.info("matching on transaction ID: " + transactionId)
        matchedTrans = Transaction.objects.get(transaction_id=transactionId)
        matchedTrans.status = 3  # set deposit transaction status to pending
        matchedTrans.last_updated = timezone.now()
        matchedTrans.save()
        amount = matchedTrans.amount

        requestURL = LINE_PAYMENTS_SANDBOX_URL + transactionId + "/confirm"
        
        payload = {
            "amount": amount,
            "currency": "THB",
        }
        for attempt in range(3):
            response = requests.post(requestURL, json=payload, headers=headers)
            if (response.status_code == 200):
                matchedTrans.status = 0
                matchedTrans.last_updated = timezone.now()
                matchedTrans.arrive_time = timezone.now()
                matchedTrans.save()
                break
            else:
                time.sleep(5)

        return JsonResponse(response.json())