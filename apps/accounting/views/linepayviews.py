from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from djauth.third_party_keys import LINE_CHANNEL_ID, LINE_CHANNEL_SECRET
from django.utils import timezone
from ..models import Transaction
from users.models import CustomUser
import os, requests, json, random, logging, time

logger = logging.getLogger('django')

LINE_PAYMENTS_SANDBOX_URL = "https://sandbox-api-pay.line.me/v2/payments/"

DEPOSIT = 0
THB = 2
LINE_PAY = 1
CREATED = 2


def reserve_payment(request):
    logger(request)

    if request.method == "GET":
        return HttpResponse("You are at the endpoint for LINEpay reserve payment.")
    
    if request.method == "POST": # can only allow post requests
        requestURL = LINE_PAYMENTS_SANDBOX_URL + "request" # prepare headers + request to LINE pay server
        headers = {
            "X-LINE-ChannelId": LINE_CHANNEL_ID,
            "X-LINE-ChannelSecret": LINE_CHANNEL_SECRET
        }

        # parse POST payload
        body = json.loads(request.body)
        amount = float(body.get("amount"))
        if (amount < 200) or (amount > 30000):
            return JsonResponse({"errorMsg": "Amount not within maximum or minimum"})

        # generate unique orderID
        orderId = (timezone.datetime.today().isoformat()+"-"+request.user.username+"-web-payment-"+str(random.randint(0,10000)))
        logger("amount: " + str(amount) + ", order-id: " + orderId)
        payload = {
            "productName": "iBet-Orion-Test",
            "productImageUrl": "https://ddowiki.com/images/Menace_of_the_Underdark_adpack_icon.jpg",
            "amount": amount,
            "currency": "THB",
            "confirmUrl": "http://localhost:3000/deposit/success",
            # "confirmUrl": "http://www.google.com",
            "orderId": orderId,
        }
        for attempt in range(3):
            response = requests.post(requestURL, json=payload, headers=headers)
            responseJSON = response.json()
            if (response.status_code == 200): # if successfully created temp transaction, store temp transaction into db with status of created/pending
                if (responseJSON["returnCode"] == "0000"):
                    userId = CustomUser.objects.get(username=request.user.username)
                    obj, created = Transaction.objects.get_or_create(
                        user_id = userId,
                        transaction_id = responseJSON["info"]["transactionId"],
                        order_id = orderId,
                        amount = float(amount),
                        method = "LINEpay",
                        currency = THB,
                        transaction_type = DEPOSIT,
                        channel = LINE_PAY,
                        status = CREATED,
                        last_updated = timezone.now()
                    )
                    logger(obj, created)
                break
            else:
                time.sleep(5)
        return JsonResponse(responseJSON)
        

def confirm_payment(request):
    logger("In confirm payment API call")
    logger(request)
    if (request.method == "GET"):
        return HttpResponse("You are at the endpoint for LINEpay confirm payment.")
    if (request.method == "POST"):
        headers = {
            "X-LINE-ChannelId": LINE_CHANNEL_ID,
            "X-LINE-ChannelSecret": LINE_CHANNEL_SECRET
        }

        body = json.loads(request.body)

        # find matching transaction
        transactionId = body.get("transactionId")
        logger("matching on transaction ID: " + transactionId)
        matchedTrans = Transaction.objects.get(transaction_id=transactionId)
        matchedTrans.status = 3 # set deposit transaction status to pending
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
                matchedTrans.save()
                break
            else:
                time.sleep(5)
        
        return JsonResponse(response.json())