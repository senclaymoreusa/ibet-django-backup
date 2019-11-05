from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.db import DatabaseError
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from django.db import transaction
from users.views.helper import checkUserBlock
from users.models import CustomUser
import simplejson as json
import xmltodict
from decimal import Decimal
import requests
from utils.constants import *
import random
import hashlib 
import logging
import datetime
from datetime import date
from django.utils import timezone
import uuid
from games.models import *
from accounting.models import * 
from utils.constants import *



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
        dic = xmltodict.parse(data)
        # print(dic)

        action  = dic['request']['@action']
        request_id = dic['request']['element']['@id']
        for i in dic['request']['element']['properties']:
            if i['@name'] == 'userid':
                properties_user_id = i['#text']
            else:
                properties_password = i['#text']

        # print(action, request_id, properties_user_id, properties_password)

        status_code = 0
        currency_code = ""
        error_message = "Successfully login"
        try: 
            user = CustomUser.objects.get(username=properties_user_id)
            if user.check_password(properties_password) is False:
                status_code = 101
                error_message = "Invalid password"

            if user.block is True:
                status_code = 104
                error_message = "User has been block"

            if user.currency == CURRENCY_CNY:
                currency = 156
                vendor = 3
            elif user.currency == CURRENCY_THB:
                currency = 764
                vendor = 4
            elif user.currency == CURRENCY_VND:
                currency = 704
                vendor = 5
            elif user.currency == CURRENCY_TTC:
                currency = 1111
                vendor = 2

        except:
            status_code = 101
            error_message = "Invalid user ID"

        response = {
            "request": {
                "@action": "clogin",
                "element": {
                    "@id": request_id,
                     "properties": [
                        {
                            "@name": "userid",
                            "#text": properties_user_id
                        },
                        {
                            "@name": "username",
                            "#text": properties_user_id
                        },
                        {
                            "@name": "acode",
                            "#text": "null"
                        },
                        {
                            "@name": "vendorid",
                            "#text": str(vendor) # will provide by EA
                        },
                        {
                            "@name": "currencyid",
                            "#text": str(currency_code)
                        }, 
                        {
                            "@name": "status",
                            "#text": str(status_code)

                        },
                        {
                            "@name": "errdesc",
                            "#text": str(error_message)
                            
                        }
                    ]
                }
            } 
        }
        logger.info("user success login to EA game: {}".format(str(properties_user_id)))
        response = xmltodict.unparse(response, pretty=True)
        # print(response)
        return HttpResponse(response, content_type='text/xml')



class DepositEAView(View):

    def post(self, request, *args, **kwargs):
        
        try:
            data = json.loads(request.body)
            username = data["username"]
            amount = data["amount"]
            user = CustomUser.objects.get(username=username)
            if requestEADeposit(user, amount) == ERROR_CODE_FAIL:
                return HttpResponse("Fail deposit money to EA")

            return HttpResponse("Finished deposit money to EA")
        except Exception as e:
            logger.error("Error deposit money to EA wallet", e)
            return HttpResponse(status=400)


        

def requestEADeposit(user, amount, from_wallet):

    trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
    print(trans_id)
    # print(user.currency)
    user_currency = int(user.currency)
    currency = 156
    # add transaction history
    try:
        trans = Transaction.objects.create(
                    transaction_id=trans_id,
                    user_id=user,
                    order_id=trans_id,
                    amount=amount,
                    currency=user_currency,
                    transfer_from=from_wallet,
                    transfer_to="EA",
                    product=2,
                    transaction_type=TRANSACTION_TRANSFER,
                    status=TRAN_PENDING_TYPE
                )
        
        if user_currency == CURRENCY_CNY:
            currency = 156
            vendor = 3
        elif user_currency == CURRENCY_THB:
            currency = 764
            vendor = 4
        elif user_currency == CURRENCY_VND:
            currency = 704
            vendor = 5
        elif user_currency == CURRENCY_TTC:
            currency = 1111
            vendor = 2


        request_id = "D"
        request_id = request_id + "%0.12d" % random.randint(0,999999999999)
        # print(request_id)
        url = "https://testmis.ea2-mission.com/configs/external/deposit/wkpibet/server.php"

        headers = {'Content-Type': 'application/xml'}
        data = {
            "request": {
                "@action": "cdeposit",
                "element": {
                    "@id": request_id,
                        "properties": [
                        {
                            "@name": "userid",
                            "#text": str(user.username)
                        },
                        {
                            "@name": "acode",
                            "#text": "null"
                        },
                        {
                            "@name": "vendorid",
                            "#text": str(vendor) # will provide by EA
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
                            "#text": str(trans_id)
                        }
                    ]
                }
            } 
        }
        requestData = xmltodict.unparse(data, pretty=True)
        # print(requestData)
        response = requests.post(url, data=requestData, headers=headers)
        response = response.text.strip()
        # print(response)
        response = xmltodict.parse(response)
        action  = response['request']['@action']
        request_id = response['request']['element']['@id']

        properties_payment_id = ""
        properties_acode = ""
        properties_status = ""
        properties_refno = ""
        properties_error = ""

        for i in response['request']['element']['properties']:
            if i['@name'] == 'acode' and "#text" in i:
                properties_acode= i["#text"]
            elif i['@name'] == 'status' and "#text" in i:
                properties_status = i["#text"]
            elif i['@name'] == 'refno' and "#text" in i:
                properties_refno = i["#text"]
            elif i['@name'] == 'paymentid' and "#text" in i:
                properties_payment_id = i["#text"]
            elif i['@name'] == 'errdesc' and "#text" in i:
                properties_error = i["#text"]

        # print(properties_payment_id, properties_acode, properties_status, properties_refno, properties_error)

        # if got properties_status == 0 => success
        # update transaction database status
        # after update transaction status send request to EA Server using comfirmEADeposit function
        if properties_status == "0" and properties_payment_id:
            status_code = "0"
            with transaction.atomic():
                trans.status = TRAN_APPROVED_TYPE
                trans.save()
            
            if comfirmEADeposit(request_id, properties_payment_id, status_code):
                # print("success")
                return CODE_SUCCESS
            else:
                # print("fail")
                return ERROR_CODE_FAIL

                # user.ea_wallet = user.ea_wallet + Decimal(float(amount))
                # user.save()

        elif properties_status == "105":
            logger.error("Invalid currency for user: {} play EA game".format(user.username))
            return ERROR_CODE_FAIL

        elif properties_status == "205":
            logger.error("Invalid vendor for user: {} play EA game".format(user.username))
            return ERROR_CODE_FAIL

    except Exception as e:
        logger.error("request deposit from EA: ", e)
        return ERROR_CODE_FAIL
    

    
           


#input params
#request_id => deposit request ID
#properties_status => response status
#properties_payment_id => payment ID in EA game
def comfirmEADeposit(request_id, properties_payment_id, status_code):
    try:

        if status_code == "0":
            error_message = "SUCCESS"
        elif status_code == "003":
            error_message = "ERR_SYSTEM_OPR"
        elif status_code == "201":
            error_message = "ERR_INVALID_REQ"

        url = "https://testmis.ea2-mission.com/configs/external/deposit/wkpibet/server.php"
        headers = {'Content-Type': 'application/xml'}
        data = {
            "request": {
                "@action": "cdeposit-confirm",
                "element": {
                    "@id": request_id,
                        "properties": [
                        {
                            "@name": "id",
                            "#text": request_id
                        },
                        {
                            "@name": "acode",
                            "#text": "null"
                        },
                        {
                            "@name": "status",
                            "#text": str(status_code)
                        },
                        {
                            "@name": "paymentid",
                            "#text": str(properties_payment_id)
                        },
                        {
                            "@name": "errdesc",
                            "#text": str(error_message)
                        }
                    ]
                }
            } 
        }
        request_data = xmltodict.unparse(data, pretty=True)
        # print(request_data)
        response = requests.post(url, data=request_data, headers=headers)
        if response.status_code == 200:
            # print(response.status_code)
            return True
            logger.info("Finished deposit money to EA")
        else:
            # print(response.status_code)
            return False
            logger.error("The transaction is not comfirmed by EA")

    except Exception as e:
        return False
        logger.error("There is something wrong when comfirm deposit request")



class WithdrawEAView(View):

    def post(self, request, *args, **kwargs):
        
        try:
            data = json.loads(request.body)
            username = data["username"]
            amount = data["amount"]
            user = CustomUser.objects.get(username=username)
            obj = requestEAWithdraw(user, amount)
            
            return HttpResponse(obj, content_type="application/json")
        
        except Exception as e:
            logger.error("Error withdraw money from EA wallet", e)
            return HttpResponse(status=400)



def requestEAWithdraw(user, amount, to_wallet):

    trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
    user_currency = user.currency

    try: 
        trans = Transaction.objects.create(
                    transaction_id=trans_id,
                    user_id=user,
                    order_id=trans_id,
                    amount=amount,
                    currency=user_currency,
                    transfer_from="EA",
                    transfer_to=to_wallet,
                    product=2,
                    transaction_type=TRANSACTION_TRANSFER,
                    status=TRAN_PENDING_TYPE
                )

        if user_currency == CURRENCY_CNY:
            currency = 156
            vendor = 3
        elif user_currency == CURRENCY_THB:
            currency = 764
            vendor = 4
        elif user_currency == CURRENCY_VND:
            currency = 704
            vendor = 5
        elif user_currency == CURRENCY_TTC:
            currency = 1111
            vendor = 2

        request_id = "W"
        request_id = request_id + "%0.12d" % random.randint(0,999999999999)
        
        url = "https://testmis.ea2-mission.com/configs/external/withdrawal/wkpibet/server.php"
        headers = {'Content-Type': 'application/xml'}
        data = {
            "request": {
                "@action": "cwithdrawal",
                "element": {
                    "@id": request_id,
                        "properties": [
                        {
                            "@name": "userid",
                            "#text": user.username
                        },
                        {
                            "@name": "vendorid",
                            "#text": str(vendor) # will provide by EA
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
                            "#text": trans_id
                        }
                    ]
                }
            } 
        }

        requestData = xmltodict.unparse(data, pretty=True)
        print(requestData)
        response = requests.post(url, data=requestData, headers=headers)
        response = response.text.strip()
        print(response)
        response = xmltodict.parse(response)
        action  = response['request']['@action']
        # print(action)
        request_id = response['request']['element']['@id']
        # print(request_id)

        for i in response['request']['element']['properties']:
            if i['@name'] == 'acode' and "#text" in i:
                properties_acode= i['#text']
            elif i['@name'] == 'status' and "#text" in i:
                properties_status = i['#text']
            elif i['@name'] == 'refno' and "#text" in i:
                properties_refno = i['#text']
            elif i['@name'] == 'paymentid' and "#text" in i:
                properties_payment_id = i['#text']
            elif i['@name'] == 'errdesc' and "#text" in i:
                properties_error = i['#text']

        # api_response = {
        #     "error_message": "Successfully comfirm withdraw",
        #     "status_code": CODE_SUCCESS
        # }
        # error_message = ""
        if properties_status == "0":
            error_message = "Successfully comfirm withdraw"
            with transaction.atomic():
                trans.status = TRAN_APPROVED_TYPE
                trans.save()

                # user.ea_wallet = user.ea_wallet - Decimal(float(amount))
                # user.save()

            logger.info("Finished withdraw from EA")
            return CODE_SUCCESS
            
        elif properties_status == "204":
            # error_message = "Exceed amount"
            # api_response["error_message"] = error_message
            # api_response["status_code"] = ERROR_CODE_MAX_EXCEED
            logger.info("Exceed amount from EA withdraw")
            return ERROR_CODE_FAIL
        elif properties_status == "205":
            # error_message = "Invalid vendor"
            # api_response["error_message"] = error_message
            # api_response["status_code"] = ERROR_CODE_INVAILD_INFO
            logger.error("Invalid vendor for user: {} play EA game".format(user.username))
            return ERROR_CODE_FAIL

    except Exception as e:
        logger.error("request withdraw from EA: ", e)
        # api_response = {}
        return ERROR_CODE_FAIL



class GetEABalance(View):

    def get(self, request, *args, **kwargs):
        
        user_id = request.GET.get('user_id')
        user = CustomUser.objects.get(pk=user_id)
        # call getEAWalletBalance function to check the balance
        current_balance = getEAWalletBalance(user)
        current_balance = json.loads(current_balance)
        if "balance" in current_balance:
            response = {
                "current_balance": current_balance["balance"],
                "status_code": CODE_SUCCESS
            }
        else:
            response = {
                "current_balance": 0,
                "status_code": ERROR_CODE_NOT_FOUND
            }

        return HttpResponse(json.dumps(response), content_type="application/json")




# get EA live casnio balance
def getEAWalletBalance(user):

    user_currency = user.currency
    if user_currency == CURRENCY_CNY:
        currency = 156
        vendor = 3
    elif user_currency == CURRENCY_THB:
        currency = 764
        vendor = 4
    elif user_currency == CURRENCY_VND:
        currency = 704
        vendor = 5
    elif user_currency == CURRENCY_TTC:
        currency = 1111
        vendor = 2
    
    request_id = "C"
    request_id = request_id + "%0.12d" % random.randint(0,999999999999)

    url = "https://testmis.ea2-mission.com/configs/external/checkclient/wkpibet/server.php"
    headers = {'Content-Type': 'application/xml'}
    data = {
        "request": {
            "@action": "ccheckclient",
            "element": {
                "@id": request_id,
                    "properties": [
                    {
                        "@name": "userid",
                        "#text": str(user.username)
                    },
                    {
                        "@name": "vendorid",
                        "#text": str(vendor) # will provide by EA
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
    response = response.text.strip()
    response = xmltodict.parse(response)

    action  = response['request']['@action']
    # print(action)
    request_id = response['request']['element']['@id']
    # print(request_id)

    api_response = {}
    
    try: 
        for i in response['request']['element']['properties']:
            if i['@name'] == 'status' and "#text" in i:
                properties_status= i['#text']
            elif i['@name'] == 'errdesc' and "#text" in i:
                propertiesMessage = i['#text']
                logger.error("Error occur when get EA balance: {}".format(propertiesMessage))
        
        api_response['status_code'] = properties_status
        api_response['error_message'] = propertiesMessage

    except:
        for i in response['request']['element']['properties']:
            if i['@name'] == 'userid':
                properties_user_id= i['#text']
            elif i['@name'] == 'balance':
                propertiesBalance = i['#text']
            elif i['@name'] == 'currencyid':
                propertiesCurrency = i['#text']
            elif i['@name'] == 'location':
                propertiesLocation = i['#text']
    
        api_response['userId'] = properties_user_id
        api_response['balance'] = propertiesBalance
        if propertiesCurrency == "156":
            currency = CURRENCY_CNY
        elif propertiesCurrency == "764":
            currency = CURRENCY_THB
        elif currency == "704":
            currency = CURRENCY_VND
        
        api_response['currency'] = currency
    
    logger.info("Successfully get the balance from EA and amount is: " + propertiesBalance)
    return json.dumps(api_response)



class EASingleLoginValidation(View):


    def post(self, request, *args, **kwargs):

        data = request.body
        # print(data)
        dic = xmltodict.parse(data)
        action  = dic['request']['@action']
        request_id = dic['request']['element']['@id']

        properties_user_id = ""
        properties_UUID = ""
        properties_ip_address= ""

        for i in dic['request']['element']['properties']:
            if i['@name'] == 'userid':
                properties_user_id = i['#text']
            elif i['@name'] == 'uuid':
                properties_UUID = i['#text']
            elif i['@name'] == 'clientip':
                properties_ip_address = i['#text']

        # print(action, request_id, properties_user_id, properties_UUID, properties_ip_address)

        status_code = 0
        currency = "156" # change the default
        vendor = 2
        error_message = "Successfully login"
        try: 
            user = CustomUser.objects.get(username=properties_user_id)
            user_currency = user.currency
            if user.block is True:
                status_code = 104
                error_message = "User has been block"

            if user_currency == CURRENCY_CNY:
                currency = 156
                vendor = 3
            elif user_currency == CURRENCY_THB:
                currency = 764
                vendor = 4
            elif user_currency == CURRENCY_VND:
                currency = 704
                vendor = 5
            elif user_currency == CURRENCY_TTC:
                currency = 1111
                vendor = 2


        except:
            status_code = 101
            error_message = "Invalid user ID"

        finally:
            response = {
                "response": {
                    "@action": action,
                    "element": {
                        "@id": request_id,
                        "properties": [
                            {
                                "@name": "userid",
                                "#text": str(properties_user_id)
                            },
                            {
                                "@name": "username",
                                "#text": str(properties_user_id)
                            },
                            {
                                "@name": "uuid",
                                "#text": str(properties_UUID)
                            },
                            {
                                "@name": "vendorid",
                                "#text": str(vendor)  # will provide by EA
                            },
                            {
                                "@name": "clientip",
                                "#text": str(properties_ip_address)
                            },
                            {
                                "@name": "currencyid",
                                "#text": str(currency)
                            }, 
                            {
                                "@name": "acode",
                                "#text": "null"
                            }, 
                            {
                                "@name": "errdesc",
                                "#text": str(error_message)
                                
                            },
                            {
                                "@name": "status",
                                "#text": str(status_code)

                            }
                        ]
                    }
                } 
            }
            response = xmltodict.unparse(response, pretty=True)
            # print(response)
            return HttpResponse(response, content_type='text/xml')


# def checkEAAffiliateRequest(username, startTime, endTime):

#     url = EA_GAME_HOST_URL

#     request_id = "CF"
#     request_id = request_id + "%0.12d" % random.randint(0,999999999999)

#     user = CustomUser.objects.get(username=username)

#     startDate = "2015-03-15"
#     endDate = "2017-03-15"

#     headers = {'Content-Type': 'application/xml'}
#     data = {
#         "request": {
#             "@action": "ccheckaffiliate",
#             "element": {
#                 "@id": request_id,
#                     "properties": [
#                     {
#                         "@name": "vendorid",
#                         "#text": "null" # will provide by EA
#                     },
#                     {
#                         "@name": "acode", # affiliate code element
#                         "acode": [   # can have mutiple affiliate code 
#                             {"#text": "123"},
#                             {"#text": "456"} 
#                         ]
#                     }, 
#                     {
#                         "@name": "begindate",
#                         "#text": startDate
#                     }, 
#                     {
#                         "@name": "enddate",
#                         "#text": endDate
#                     }
#                 ]
#             }
#         } 
#     }

#     requestData = xmltodict.unparse(data, pretty=True)
#     response = requests.post(url, data=requestData, headers=headers)

#     dic = xmltodict.parse(response)
#     response = json.dumps(dic)

#     properties = response["request"]["element"]["properties"]
#     startDate = ""
#     endDate = ""
#     status_code = ""
#     messageStr = ""

#     # store response data
#     # for i in properties:
#     #     if "@name" in i:
#     #         if i["@name"] == "datelist"
#     #             startDate = i["fromdate"]
#     #             endDate = i["todate"]
#     #         if i["@name"] == "status"
#     #             status_code = i["text"]    #response status
#     #         if i["@name"] == "errdesc"
#     #             messageStr = i["text"]    #response message
#     #     if "@acode" in i:
#     #         for date in i['date']:
        
#     return response



class AutoCashierLoginEA(View):

    def post(self, request, *args, **kwargs):
        
        data = request.body
        dic = xmltodict.parse(data)
        response = json.dumps(dic)
        # print(response)

        action = dic["request"]["@action"]
        request_id = dic["request"]["element"]["@id"]
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

        status_code = "0"
        today = datetime.date.today()
        today = today.strftime("%Y/%m/%d")
        # print(today)
        signStr = username + today + EA_KEY
        key_hash_result = hashlib.md5(signStr.encode()) 
        # print(result.hexdigest())
        if sign != key_hash_result.hexdigest():
            status_code = "614"
        else:
            try:
                user = CustomUser.objects.get(username__iexact=username)
                if checkUserBlock(user.pk):
                    status_code = "612"
            except:
                status_code = "611"

        UUID = uuid.uuid4()
        EATicket.objects.create(ticket=UUID)

        data = {
            "request": {
                "@action": action,
                "element": {
                    "@id": request_id,
                        "properties": [
                        {
                            "@name": "status",
                            "#text": str(status_code)
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