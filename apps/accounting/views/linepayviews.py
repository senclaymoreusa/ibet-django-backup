from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from djauth.third_party_keys import LINE_CHANNEL_ID, LINE_CHANNEL_SECRET

import requests

LINE_PAYMENTS_SANDBOX_URL = "https://sandbox-api-pay.line.me/v2/payments/"

def reservePayment(request):
    if(request.method == "POST"): # can only allow post requests
        # prepare request to LINE pay server
        requestURL = LINE_PAYMENTS_SANDBOX_URL + "request"
        headers = {
            "X-LINE-ChannelId": LINE_CHANNEL_ID,
            "X-LINE-ChannelSecret": LINE_CHANNEL_SECRET
        }
        # orderId = #generate orderId to be unique 
        payload = {
            "productName": "iBet-Orion-Test",
            "productImageUrl": "https://ddowiki.com/images/Menace_of_the_Underdark_adpack_icon.jpg",
            "amount": 123.12,
            "currency": "THB",
            "confirmUrl": "www.ibet.com/line-transfer-confirm",
            "orderId": "1a2b3c" 
        }
        
        response = requests.post(requestURL, json=payload, headers=headers)
        return JsonResponse(response.json())