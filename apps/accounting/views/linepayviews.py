from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from djauth.third_party_keys import LINE_CHANNEL_ID, LINE_CHANNEL_SECRET
from ..models import Transaction
from users.models import CustomUser
import os, requests, datetime, json

LINE_PAYMENTS_SANDBOX_URL = "https://sandbox-api-pay.line.me/v2/payments/"

DEPOSIT = 0
THB = 2
LINE_PAY = 1
CREATED = 2


def reserve_payment(request):
    print(request)
    if request.method == "GET":
        return HttpResponse("You are at the endpoint for LINEpay reserve payment.")
    if request.method == "POST": # can only allow post requests
        # prepare headers + request to LINE pay server
        requestURL = LINE_PAYMENTS_SANDBOX_URL + "request"
        headers = {
            "X-LINE-ChannelId": LINE_CHANNEL_ID,
            "X-LINE-ChannelSecret": LINE_CHANNEL_SECRET
        }

        # parse POST payload
        body = json.loads(request.body)
        amount = body.get("amount")
        
        # generate unique orderID
        orderId = (datetime.date.today().isoformat()+"-orion-web-payment-1")
        # orderId = "test-order"
        print("amount: " + amount + ", order-id: " + orderId)
        payload = {
            "productName": "iBet-Orion-Test",
            "productImageUrl": "https://ddowiki.com/images/Menace_of_the_Underdark_adpack_icon.jpg",
            "amount": amount,
            "currency": "THB",
            "confirmUrl": "http://localhost:3000/deposit/success",
            # "confirmUrl": "http://www.google.com",
            "orderId": orderId,
        }
        
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
                    transaction_type = DEPOSIT, # 0 = deposit
                    channel = LINE_PAY, # 1 = LINEpay
                    status = CREATED, # 2 = created
                    last_updated = datetime.datetime.now()
                )
                print(obj, created)
        return JsonResponse(responseJSON)
        

def confirm_payment(request):
    print("In confirm payment API call")
    print(request)
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
        matchedTrans = Transaction.objects.get(order_id=transactionId)
        matchedTrans.status = 3 # set deposit transaction status to pending
        matchedTrans.last_updated = datetime.datetime.now()
        matchedTrans.save()
        amount = matchedTrans.amount

        requestURL = LINE_PAYMENTS_SANDBOX_URL + transactionId + "/confirm"

        payload = {
            "amount": amount,
            "currency": "THB",
        }

        response = requests.post(requestURL, json=payload, headers=headers)

        if (response.status_code == 200):
            matchedTrans.status = 0
            matchedTrans.last_updated = datetime.datetime.now()
            matchedTrans.save()

        return JsonResponse(response.json())