from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from users.models import CustomUser
import simplejson as json
import xmltodict
import decimal
import requests
from utils.constants import *
import random
import hashlib 
import logging
import datetime
from datetime import date
from django.utils import timezone
import uuid
from  games.models import *


logger = logging.getLogger('django')

EA_GAME_HOST_URL = ""
KEY = "" # provide by EA for hash purpose

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
        requestId = dic['request']['element']['@id']
        for i in dic['request']['element']['properties']:
            if i['@name'] == 'userid':
                propertiesUserId = i['#text']
            else:
                propertiesPassword = i['#text']

        print(action, requestId, propertiesUserId, propertiesPassword)

        statusCode = 0
        currencyCode = ""
        errorMessage = "Successfully login"
        try: 
            user = CustomUser.objects.get(username=propertiesUserId)
            if user.check_password(propertiesPassword) is False:
                statusCode = 101
                errorMessage = "Invalid password"

            if user.block is True:
                statusCode = 104
                errorMessage = "User has been block"

            if user.currency == "CNY":
                currencyCode = "156"
            elif user.currency == "THB":
                currencyCode = "764"
            elif user.currency == "VND":
                currencyCode = "704"

        except:
            statusCode = 101
            errorMessage = "Invalid user ID"

        response = {
            "request": {
                "@action": "clogin",
                "element": {
                    "@id": requestId,
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
                            "#text": "null" # will provide by EA
                        },
                        {
                            "@name": "currencyid",
                            "#text": str(currencyCode)
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
#         requestId = dic['request']['element']['@id']
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
                "@id": requestId,
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
                        "#text": "null" # will provide by EA
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

    response = requests.post(url, data=requestData, headers=headers)

    response = xmltodict.parse(response)
    print(response)
    action  = dic['request']['@action']
    print(action)
    requestId = dic['request']['element']['@id']
    print(requestId)

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



#input params
#requestId => deposit request ID
#propertiesStatus => response status
#propertiesPaymentId => payment ID in EA game
def comfirmEADeposit(requestId, propertiesStatus, propertiesPaymentId):

    statusCode = "0"
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
                "@id": requestId,
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

    requestData = xmltodict.unparse(data, pretty=True)
    response = requests.post(url, data=requestData, headers=headers)
    



def requestEAWithdraw(transId, username, amount, currency):

    if currency == CURRENCY_CNY:
        currency = 156
    elif currency == CURRENCY_THB:
        currency = 764
    elif currency == CURRENCY_VND:
        currency = 704
    
    requestId = "W"
    requestId = requestId + "%0.12d" % random.randint(0,999999999999)

    url = EA_GAME_HOST_URL
    headers = {'Content-Type': 'application/xml'}
    data = {
        "request": {
            "@action": "cwithdrawal",
            "element": {
                "@id": requestId,
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
                        "@name": "vendorid",
                        "#text": "null" # will provide by EA
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
    response = requests.post(url, data=requestData, headers=headers)

    response = xmltodict.parse(response)
    print(response)
    action  = dic['request']['@action']
    print(action)
    requestId = dic['request']['element']['@id']
    print(requestId)

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

    errorMessage = "Successfully comfirm deposit"
    if propertiesStatus == "201":
        errorMessage = "Invalid request"
        logger.error(errorMessage + "for EA game")
    elif propertiesStatus == "204":
        errorMessage = "Exceed amount"
        logger.error(errorMessage + "for EA game")
    elif propertiesStatus == "205":
        errorMessage = "Invalid vendor"
        logger.error(errorMessage + "for EA game")
    
    # handle more error response message
    if propertiesStatus == "0":
        print("withdraw successed")
        logger.info("sucessfully withdraw money from EA")
        # update db status from pending to Approve and increase the balance




class CheckEABalance(View):

    def post(self, request, *args, **kwargs):
        
        data = json.loads(request.body)

        userid = data['userId']
        currency = data['currency']
        
        # call getEAwalletBalance function to check the balance
        response = getEAwalletBalance(userid, currency)
        response = json.loads(response)


# get EA live casnio balance
def getEAwalletBalance(userId, currency):

    if currency == CURRENCY_CNY:
        currency = 156
    elif currency == CURRENCY_THB:
        currency = 764
    elif currency == CURRENCY_VND:
        currency = 704
    
    requestId = "C"
    requestId = requestId + "%0.12d" % random.randint(0,999999999999)

    url = EA_GAME_HOST_URL
    headers = {'Content-Type': 'application/xml'}
    data = {
        "request": {
            "@action": "ccheckclient",
            "element": {
                "@id": requestId,
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
                        "@name": "vendorid",
                        "#text": "null" # will provide by EA
                    },
                    {
                        "@name": "currencyid",
                        "#text": str(currency)
                    }
                ]
            }
        } 
    }

    requestData = xmltodict.unparse(data, pretty=True)
    response = requests.post(url, data=requestData, headers=headers)

    response = xmltodict.parse(response)

    action  = dic['request']['@action']
    print(action)
    requestId = dic['request']['element']['@id']
    print(requestId)

    apiRespsonse = {}
    
    try: 
        for i in dic['request']['element']['properties']:
            if i['@name'] == 'status':
                propertiesStatus= i['#text']
            elif i['@name'] == 'errdesc':
                propertiesMessage = i['#text']
                logger.error(propertiesMessage)
                # there are some error occur in check balance request
        
        apiRespsonse['statusCode'] = propertiesStatus
        apiRespsonse['errorMessage'] = propertiesMessage

    except:
        for i in dic['request']['element']['properties']:
            if i['@name'] == 'userid':
                propertiesUserId= i['#text']
            elif i['@name'] == 'balance':
                propertiesBalance = i['#text']
            elif i['@name'] == 'currencyid':
                propertiesCurrency = i['#text']
            elif i['@name'] == 'location':
                propertiesLocation = i['#text']
    
        apiRespsonse['userId'] = propertiesUserId
        apiRespsonse['balance'] = propertiesBalance
        if propertiesCurrency == "156":
            currency = CURRENCY_CNY
        elif propertiesCurrency == "764":
            currency = CURRENCY_THB
        elif currency == "704":
            currency = CURRENCY_VND
        
        apiRespsonse['currency'] = currency
        
        
    return json.dumps(apiRespsonse)



class EASingleLoginValidation(View):

    def post(self, request, *args, **kwargs):

        data = request.body
        # sessionId = request.session.session_key
        # print(data)
        # print(sessionId)
        dic = xmltodict.parse(data)
        # print(dic)
        action  = dic['request']['@action']
        requestId = dic['request']['element']['@id']
        for i in dic['request']['element']['properties']:
            if i['@name'] == 'userid':
                propertiesUserId = i['#text']
            elif i['@name'] == 'uuid':
                propertiesUUID = i['#text']
            elif i['@name'] == 'clientip':
                propertiesIPaddress = i['#text']

        # print(action, requestId, propertiesUserId, propertiesUUID, propertiesIPaddress)

        statusCode = 0
        currencyCode = "156" # change the default
        errorMessage = "Successfully login"
        try: 
            user = CustomUser.objects.get(username=propertiesUserId)

            if user.block is True:
                statusCode = 104
                errorMessage = "User has been block"

            if user.currency == "CNY":
                currencyCode = "156"
            elif user.currency == "THB":
                currencyCode = "764"
            elif user.currency == "VND":
                currencyCode = "704"
        except:
            statusCode = 101
            errorMessage = "Invalid user ID"

        response = {
            "request": {
                "@action": action,
                "element": {
                    "@id": requestId,
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
                            "@name": "uuid",
                            "#text": propertiesUUID
                        },
                        {
                            "@name": "vendorid",
                            "#text": "null"  # will provide by EA
                        },
                        {
                            "@name": "currencyid",
                            "#text": str(currencyCode)
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
        # return HttpResponse("hello")


class TestView(View):

    def post(self, request, *args, **kwargs):
        
        # response = checkEAAffiliateRequest(1)
        data = request.body
        dic = xmltodict.parse(data)
        # response = json.dumps(dic)
        response = xmltodict.unparse(dic, pretty=True)
        return HttpResponse(response, content_type='text/xml')


def checkEAAffiliateRequest(username, startTime, endTime):

    url = EA_GAME_HOST_URL

    requestId = "CF"
    requestId = requestId + "%0.12d" % random.randint(0,999999999999)

    user = CustomUser.objects.get(username=username)

    startDate = "2015-03-15"
    endDate = "2017-03-15"

    headers = {'Content-Type': 'application/xml'}
    data = {
        "request": {
            "@action": "ccheckaffiliate",
            "element": {
                "@id": requestId,
                    "properties": [
                    {
                        "@name": "id",
                        "#text": requestId
                    },
                    {
                        "@name": "vendorid",
                        "#text": "null" # will provide by EA
                    },
                    {
                        "@name": "acode", # affiliate code element
                        "acode": [   # can have mutiple affiliate code 
                            {"#text": "123"},
                            {"#text": "456"} 
                        ]
                    }, 
                    {
                        "@name": "begindate",
                        "#text": startDate
                    }, 
                    {
                        "@name": "enddate",
                        "#text": endDate
                    }
                ]
            }
        } 
    }

    requestData = xmltodict.unparse(data, pretty=True)
    response = requests.post(url, data=requestData, headers=headers)

    dic = xmltodict.parse(response)
    response = json.dumps(dic)

    properties = response["request"]["element"]["properties"]
    startDate = ""
    endDate = ""
    statusCode = ""
    messageStr = ""

    # store response data
    # for i in properties:
    #     if "@name" in i:
    #         if i["@name"] == "datelist"
    #             startDate = i["fromdate"]
    #             endDate = i["todate"]
    #         if i["@name"] == "status"
    #             statusCode = i["text"]    #response status
    #         if i["@name"] == "errdesc"
    #             messageStr = i["text"]    #response message
    #     if "@acode" in i:
    #         for date in i['date']:
        
    return response



class AutoCashierLoginEA(View):

    def post(self, request, *args, **kwargs):
        
        data = request.body
        dic = xmltodict.parse(data)
        # response = json.dumps(dic)
        # print(response)

        action = dic["request"]["@action"]
        requestId = dic["request"]["element"]["@id"]
        properties = dic["request"]["element"]["properties"]
        
        username = ""
        date = ""
        sign = ""

        for i in properties:
            if i["@name"] == "username":
                username = i["#text"]
            elif i["@name"] == "date":
                date = i["#text"]
            elif i["@name"] == "sign":
                sign = i["#text"]

        statusCode = "0"
        today = datetime.date.today()
        today = today.strftime("%Y/%m/%d")
        # print(today)
        signStr = username + today + KEY
        result = hashlib.md5(signStr.encode()) 
        # print(result.hexdigest())
        if sign != result.hexdigest():
            statusCode = "614"
        else:
            try:
                user = CustomUser.objects.get(username__iexact=username)
                if user.block is True:
                    statusCode = "612"
            except:
                statusCode = "611"

        UUID = uuid.uuid4()
        EATicket.objects.create(ticket=UUID)

        data = {
            "request": {
                "@action": action,
                "element": {
                    "@id": requestId,
                        "properties": [
                        {
                            "@name": "id",
                            "#text": requestId
                        },
                        {
                            "@name": "status",
                            "#text": str(statusCode)
                        },
                        {
                            "@name": "username",
                            "#text": username
                        },
                        {
                            "@name": "ticket",
                            "#text": str(UUID)   #generate 15 seconds response ticket
                        }
                    ]
                }
            } 
        }
        
        response = xmltodict.unparse(data, pretty=True)
        return HttpResponse(response, content_type='text/xml')