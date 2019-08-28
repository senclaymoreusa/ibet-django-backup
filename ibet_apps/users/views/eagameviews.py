from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from users.models import CustomUser
import simplejson as json
import xmltodict
import decimal
import requests
from utils.constants import *
import random

EA_GAME_HOST_URL = ""

EA_RESPONSE_ERROR = {
    "0": "SUCCESS",
    "003": "ERR_SYSTEM_OPR",
    "105": "ERROR_INVALID_CURRENCY",
    "201": "ERR_INVALID_REQ",
    "202": "ERR_DB_OPEATION",
    "204": "ERR_EXCEED_AMOUNT",
    "205": "ERR_INVALID_VENDOR",
    "211": "ERR_CLIENT_IN_GAME",
    "401": "ERR_DUPLICATE_REFNO",
    "402": "ERR_INVALID_PREFIX|ERR_INVALID_IP",
    "403": "ERR_INVALD_AMOUNT",
    "404": "ERR_ILLEGAL_DECIMAL"
}


class EALiveCasinoClientLoginView(View):

    def post(self, request, *args, **kwargs):

        # data = str(request.body, 'utf-8')
        data = request.body
        # print(data)
        dic = xmltodict.parse(data)
        # print(dic)

        action  = dic['request']['@action']
        elementId = dic['request']['element']['@id']
        for i in dic['request']['element']['properties']:
            if i['@name'] == 'userid':
                propertiesUserId = i['#text']
            else:
                propertiesPassword = i['#text']

        print(action, elementId, propertiesUserId, propertiesPassword)

        statusCode = 0
        errorMessage = "Successfully login"
        try: 
            user = CustomUser.objects.get(username=propertiesUserId)
            if user.check_password(propertiesPassword) is False:
                statusCode = 101
                errorMessage = "Invalid password"

            if user.block is True:
                statusCode = 104
                errorMessage = "User has been block"
        except:
            statusCode = 101
            errorMessage = "Invalid user ID"

        response = {
            "request": {
                "@action": "clogin",
                "element": {
                    "@id": elementId,
                     "properties": [
                        {
                            "@name": "userid",
                            "#text": propertiesUserId
                        },
                        {
                            "@name": "username",
                            "#text": propertiesUserId
                        },
                        {
                            "@name": "acode",
                            "#text": "null"
                        },
                        {
                            "@name": "vendorid",
                            "#text": "null"
                        },
                        {
                            "@name": "currencyid",
                            "#text": "156"
                        }, 
                        {
                            "@name": "status",
                            "#text": str(statusCode)

                        },
                        {
                            "@name": "errdesc",
                            "#text": str(errorMessage)
                            
                        }
                    ]
                }
            } 
        }
        response = xmltodict.unparse(response, pretty=True)
        return HttpResponse(response, content_type='text/xml')

        

# class EALiveCasinoDepositView(View):

#     def post(self, request, *args, **kwargs):

#         data = request.body
#         dic = xmltodict.parse(data)

#         action  = dic['request']['@action']
#         elementId = dic['request']['element']['@id']
#         for i in dic['request']['element']['properties']:
#             if i['@name'] == 'userid':
#                 propertiesUserId = i['#text']
#             else:
#                 propertiesPassword = i['#text']
        

#         response = xmltodict.unparse(response, pretty=True)
#         return HttpResponse(response, content_type='text/xml')


def requestEADeposit(transId, username, amount, currency):

    if currency == CURRENCY_CNY:
        currency = 156
    elif currency == CURRENCY_THB:
        currency = 764
    elif currency == CURRENCY_VND:
        currency = 704
    
    requestId = "D"
    requestId = requestId + "%0.12d" % random.randint(0,999999999999)

    url = EA_GAME_HOST_URL
    headers = {'Content-Type': 'application/xml'}
    data = {
        "request": {
            "@action": "cdeposit",
            "element": {
                "@id": elementId,
                    "properties": [
                    {
                        "@name": "id",
                        "#text": requestId
                    },
                    {
                        "@name": "userid",
                        "#text": username
                    },
                    {
                        "@name": "acode",
                        "#text": "null"
                    },
                    {
                        "@name": "vendorid",
                        "#text": "null"
                    },
                    {
                        "@name": "currencyid",
                        "#text": str(currency)
                    }, 
                    {
                        "@name": "amount",
                        "#text": str(amount)

                    },
                    {
                        "@name": "refno",
                        "#text": transId
                    }
                ]
            }
        } 
    }
    requestData = xmltodict.unparse(data, pretty=True)

    reponse = requests.post(url, data=requestData, headers=headers)

    reponse = xmltodict.parse(reponse)
    print(response)
    action  = dic['request']['@action']
    print(action)
    elementId = dic['request']['element']['@id']
    print(elementId)

    for i in dic['request']['element']['properties']:
        if i['@name'] == 'acode':
            propertiesAcode= i['#text']
        elif i['@name'] == 'status':
            propertiesStatus = i['#text']
        elif i['@name'] == 'refno':
            propertiesRefno = i['#text']
        elif i['@name'] == 'paymentid':
            propertiesPaymentId = i['#text']
        elif i['@name'] == 'errdesc':
            propertiesError = i['#text']
        
    # if got propertiesStatus == 0 => success
    # update transaction database status
    # after update transction status send request to EA Server using comfirmEADeposit function






def comfirmEADeposit(requestId, propertiesStatus, propertiesPaymentId):

    statusCode = ""
    errorMessage = "Successfully comfirm deposit"

    if propertiesStatus == "003":
        statusCode = propertiesStatus
        errorMessage = "ERR_SYSTEM_OPR"
    elif propertiesStatus == "201":
        statusCode = propertiesStatus
        errorMessage = "invalid request"
    elif propertiesStatus == "202":
        statusCode = propertiesStatus
        errorMessage = "invalid request"
        

    url = EA_GAME_HOST_URL
    headers = {'Content-Type': 'application/xml'}
    data = {
        "request": {
            "@action": "cdeposit-confirm",
            "element": {
                "@id": elementId,
                    "properties": [
                    {
                        "@name": "id",
                        "#text": requestId
                    },
                    {
                        "@name": "acode",
                        "#text": "null"
                    },
                    {
                        "@name": "status",
                        "#text": str(statusCode)
                    },
                    {
                        "@name": "paymentid",
                        "#text": str(propertiesPaymentId)
                    },
                    {
                        "@name": "errdesc",
                        "#text": str(errorMessage)
                    }
                ]
            }
        } 
    }
    





