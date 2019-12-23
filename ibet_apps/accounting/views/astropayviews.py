import requests, json, logging, random, hmac, struct, hashlib, xml.etree.ElementTree as ET
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from rest_framework import parsers, renderers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from users.views.helper import *
from users.models import CustomUser
from accounting.models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from accounting.serializers import astroPaymentStatusSerialize
from utils.constants import *
from time import sleep, gmtime, strftime
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
import asyncio
from accounting.views.sqs_message import send_message_sqs 
from django.contrib.auth.hashers import make_password, check_password

logger = logging.getLogger('django')
secretkey = ASTROPAY_SECRET
currencyConversion = {
    0: "CNY",
    1: "USD",
    2: "THB",
    3: "IDR",
    7: "VND",
    10: "EUR",
}

#get hash code 
def generateHash(key, message):
    hash = hmac.new(key, msg=message, digestmod=hashlib.sha256)
    #hash.hexdigest()
    return hash.hexdigest()

# generate SHA1 control message
def generateControl(message):
    encodeStr = ASTROPAY_SECRET + message
    x_control = hashlib.sha1(encodeStr.encode()).hexdigest()
    return x_control

#new invoice api which will return an url for users to rediract
@api_view(['POST'])
@permission_classes((AllowAny,))
def astroNewInvoice(request):
    url = ASTROPAY_URL
    invoice = request.data.get('transaction_id')
    amount = request.data.get('amount')
    iduser = request.data.get('user_id')
    user = CustomUser.objects.get(pk=iduser)
    bank = request.data.get('bank')
    cpf = request.data.get('cpf')
    email = request.data.get('email')
    name = request.data.get('name')
    country = request.data.get('country')
    zip = ''
    address = ''
    city = ''
    state = ''
    bdate = ''
    message = bytes(str(invoice) + 'V' + str(amount) + 'I' + str(iduser) + '2' + str(bank) + '1' + str(cpf) + 'H' + str(bdate) + 'G' + str(email) + 'Y' + str(zip) + 'A' + str(address) + 'P' + str(city) + 'S' + str(state) + 'P', 'utf-8')
    secret = bytes(secretkey, 'utf-8')
    my_hmac = generateHash(secret, message)
    params = {
        "x_login":ASTROPAY_X_LOGIN,
        "x_trans_key":ASTROPAY_X_TRANS_KEY,
        "x_invoice":invoice,
        "x_amount":amount,
        "x_bank":bank,
        "x_country":country,
        "x_iduser":iduser,
        "x_cpf":cpf,
        "x_name":name,
        "x_email":email,
        "control":my_hmac,
    }

    if checkUserBlock(user):
        errorMessage = _('The current user is blocked!')
        data = {
            "errorCode": ERROR_CODE_BLOCK,
            "errorMsg": {
                "detail": [errorMessage]
            }
        }
        return Response(data)
    for x in range(3):   
        r = requests.post(url, data=params)
        rdata = r.text
        logger.info(rdata)
        tree = ET.fromstring(rdata)
        redirect_url = tree.find('link').text
        if r.status_code == 200:
            break
        elif r.status_code == 500:
            logger.info("Request failed {} time(s)'.format(x+1)")
            logger.info("Waiting for %s seconds before retrying again")
            sleep(delay)
        elif r.status_code == 400:
            # Handle error
            logger.info("There was something wrong with the result")
            logger.info(rdata)
            return Response(rdata) 
    create = Transaction.objects.get_or_create(
        order_id=invoice,
        amount=amount,
        user_id=CustomUser.objects.get(pk=iduser),
        currency= 1,
        transaction_type=0, 
        channel=2,
        status=2,
    )
    return Response({'Status': '0','Redirect url': redirect_url}) 

#payment status
@api_view(['POST'])
@permission_classes((AllowAny,))
def astroPaymentStatus(request):
    statusConversion = {
        "6": 1,
        "7": 2,
        "8": 4,
        "9": 0
    }
    url = ASTROPAY_WPS 
    invoice = request.data.get('order_id')
    params = {
            "x_login":ASTROPAY_WP_LOGIN,
            "x_trans_key":ASTROPAY_WP_TRANS_KEY,
            "x_invoice":invoice,
        }
    for x in range(3):   
        r = requests.post(url, data=params)
        rdata = r.text
        data = rdata.split('|')
        logger.info(data)
        if r.status_code == 200:
            break
        elif r.status_code == 500:
            logger.info("Request failed {} time(s)'.format(x+1)")
            logger.info("Waiting for %s seconds before retrying again")
            sleep(delay)
        elif r.status_code == 400:
            # Handle error
            logger.info("There was something wrong with the result")
            logger.info(rdata)
            return Response(rdata)
    depositData = {
        "order_id": invoice, 
        "amount": data[3],
        "user_id":  data[1],
        "bank": data[7],
        "currency": currencyConversion[data[10]],
        "channel": 2,
        "status": statusConversion[data[0]]
    }
    serializer = astroPaymentStatusSerialize(data=depositData)
    #logger.info(serializer)
    if (serializer.is_valid()):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#withdraw
@api_view(['POST'])
@permission_classes((AllowAny,))
def sendCardToMobile(request):
    amount = request.data.get('amount')
    currency = request.data.get('currency')
    mobile = request.data.get('mobile')
    userid = request.data.get('userid')
    withdraw_password = request.data.get("withdrawPassword")
    doc_id = request.data.get('doc_id')
    
    
    try:
        user = CustomUser.objects.get(pk=userid)

        user_fn = user.first_name
        user_ln = user.last_name
        name = user_fn + " " + user_ln
        
        country = user.country
        if country == 'China':
            country = 'CH'
        elif country == 'Thailand':
            country = 'TH'
        elif country == 'Vietnam':
            country = 'VN'
        else:
            country = 'BR'
        
        message =  str(amount) + str(currency) + str(mobile)
        # my_hmac = hashlib.sha1(message.encode()).hexdigest()
        OrderID =  user.username+"-"+timezone.datetime.today().isoformat()+"-"+str(random.randint(0, 10000000))
        
        params = {
            "x_login":ASTROPAY_X_LOGIN,
            "x_trans_key":ASTROPAY_X_TRANS_KEY,
            "x_amount":amount,
            "x_currency": currency,
            "x_mobile_number":mobile,
            "x_name":name,
            "x_document":doc_id,
            "x_country":country,
            "x_control":generateControl(message),
            "x_reference": OrderID,
            "notification_url": ASTROPAY_CONFIRM_URL,
        }
    
        url = ASTROPAY_URL
        
        if user.withdraw_password and check_password(withdraw_password, user.withdraw_password):
            
            for x in range(3):
                r = requests.post(url + '/cashOut/sendCardToMobile', data=params)
                rdata = r.json()
                logger.info(rdata)
                print(r.status_code)
                if r.status_code == 200:
                    print(rdata)
                    break
                elif r.status_code == 500:
                    logger.info("Request failed {} time(s)'.format(x+1)")
                    logger.info("Waiting for %s seconds before retrying again")
                    sleep(5)
                else:
                    logger.info("There was something wrong with the result")
                    logger.info(rdata)
                    return Response(rdata)
        else:
            logger.error("withdraw password is not correct.")    
            return Response({
                'status_code': ERROR_CODE_INVALID_INFO,
                'message': 'Withdraw password is not correct.'
            })
        if rdata["response"] == "SUCCESS":
            create = Transaction.objects.create(
                        order_id=OrderID,
                        transaction_id=rdata["id_cashout"],
                        amount=rdata["amount"],
                        user_id=user,
                        currency= currencyConversion[rdata["currency"]],
                        transaction_type=1, 
                        channel=2,
                        status=0,
                        method="AstroPay Cashout Card",
                    )
            return Response(rdata)
        else:
            logger.info("There was something wrong with the result")
            return JsonResponse({
                    'status_code': ERROR_CODE_FAIL,
                    'message': 'There was something wrong with the result, please try again.'
                })
    except ObjectDoesNotExist as e:
        logger.error(repr(e))
        return HttpResponse(status=500)


@api_view(['POST'])
@permission_classes((AllowAny,))
def checkUser(request):
    url = ASTROPAY_URL
    customer_id = request.data.get('customer_id')
    message = str(secretkey) + str(customer_id)
    my_hmac = hashlib.sha1(message.encode()).hexdigest()
    logger.info(my_hmac)
    params = {
        "x_login": ASTROPAY_X_LOGIN,
        "x_trans_key": ASTROPAY_X_TRANS_KEY,
        "x_astropaycard_customer_id": customer_id,
        "x_control": my_hmac,
    }
    for x in range(3):
        r = requests.post(url + 'cashOut/checkUser', data=params)
        rdata = r.json()
        logger.info(rdata)
        if r.status_code == 200:
            break
        elif r.status_code == 500:
            logger.info("Request failed {} time(s)'.format(x+1)")
            logger.info("Waiting for %s seconds before retrying again")
            sleep(5)
        else:
            logger.info("There was something wrong with the result")
            logger.info(rdata)
            return Response(rdata)
    return Response(rdata)
#withdraw
@api_view(['POST'])
@permission_classes((AllowAny,))
def sendCardToMobileWithAppId(request):
    amount = request.data.get('amount')
    customer_id = request.data.get('customer_id')
    userid = request.data.get('userid')
    withdraw_password = request.data.get("withdrawPassword")
    doc_id = request.data.get('doc_id')
    try:
        user = CustomUser.objects.get(pk=userid)
        currency = user.currency
        user_fn = user.first_name
        user_ln = user.last_name
        name = user_fn + " " + user_ln
        

        country = user.country
        if country == 'China':
            country = 'CH'
        elif country == 'Thailand':
            country = 'TH'
        elif country == 'Vietnam':
            country = 'VN'
        else:
            country = 'BR'
        
        message =   str(customer_id)
        # my_hmac = hashlib.sha1(message.encode()).hexdigest()
        # logger.info(my_hmac)
        print(generateControl(message))
        OrderID =  user.username+"-"+timezone.datetime.today().isoformat()+"-"+str(random.randint(0, 10000000))
        params = {
            "x_login":ASTROPAY_X_LOGIN,
            "x_trans_key":ASTROPAY_X_TRANS_KEY,
            "x_amount":amount,
            "x_currency": currencyConversion[currency],
            "x_astropaycard_customer_id":customer_id,
            "x_name":name,
            "x_document":doc_id,
            "x_country":country,
            "x_control":generateControl(message),
            "x_reference": OrderID,
            "notification_url": ASTROPAY_CONFIRM_URL,
        }
        
        url = ASTROPAY_URL
        if check_password(withdraw_password, user.withdraw_password):
            for x in range(3):
                r = requests.post(url + '/cashOut/sendCardToMobile', data=params)
                rdata = r.json()
                logger.info(rdata)
                print(rdata)
                if r.status_code == 200:
                    if rdata["response"] == 'SUCCESS':
                        create = Transaction.objects.create(
                            order_id=OrderID,
                            transaction_id=rdata["id_cashout"],
                            amount=rdata["amount"],
                            user_id=user,
                            currency= currency,
                            transaction_type=1, 
                            channel=2,
                            status=0,
                            method="AstroPay Cashout Card",
                        )
                        
                    return Response(rdata)
                    break
                elif r.status_code == 500:
                    logger.info("Request failed {} time(s)'.format(x+1)")
                    logger.info("Waiting for %s seconds before retrying again")
                    sleep(5)
                else:
                    logger.info("There was something wrong with the result")
                    logger.info(rdata)
                    return Response(rdata)
        else:
            logger.error("withdraw password is not correct.")    
            return JsonResponse({
                'status_code': ERROR_CODE_INVALID_INFO,
                'message': 'Withdraw password is not correct.'
            })
    except ObjectDoesNotExist as e:
        logger.error(repr(e))
        return HttpResponse(status=500)
        
def notification(request):
    if request.method == "POST":
        status = request.POST.get("status")
        id_cashout_card = request.POST.get("id_cashout_card")
        x_reference = request.POST.get("x_reference")
        return JsonResponse({
            'status': status,
            'message': 'Success'
        })

@api_view(['POST'])
@permission_classes((AllowAny,))
def verif_transtatus(request):
    invoice_num = request.data.get("invoice_num")
    params = {
        "x_login":ASTROPAY_X_LOGIN,
        "x_trans_key":ASTROPAY_X_TRANS_KEY,
        "x_invoice_num":invoice_num,
    }
    url = ASTROPAY_URL
    logger.info(url)
    for x in range(3):
        r = requests.post(url + 'verif/transtatus', data=params)
        rdata = r.text
        logger.info(rdata)
        if r.status_code == 200:
            break
        elif r.status_code == 500:
            logger.info("Request failed {} time(s)'.format(x+1)")
            logger.info("Waiting for %s seconds before retrying again")
            sleep(5)
        else:
            logger.info("There was something wrong with the result")
            logger.info(rdata)
            return Response(rdata)
    return Response(rdata)

def cancel_cashout_card(request):
    if (request.method == "POST"):
        astroPayEndpoint = ASTROPAY_URL + "/cancelCashoutCard"
        requestBody = json.loads(request.body)

        cashoutId = requestBody.get("id_cashout")
        controlStr = generateControl(cashoutId)

        params = {
            "x_login": ASTROPAY_X_LOGIN,
            "x_trans_key": ASTROPAY_X_TRANS_KEY,
            "id_cashout": cashoutId,
            "x_control": controlStr
        }

        for attempt in range(3):
            response = requests.post(requestURL, json=params)
            # responseJSON = response.json()
            logger.info(response)
            if (response.status_code == 200): # if successfully created temp transaction, store temp transaction into db with status of created/pending
                logger.info("created?: " + str(created))
                logger.info("transaction data: " + str(obj))
                break
            else:
                sleep(5)
        return JsonResponse(responseJSON)

# create money order with astropay card
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def capture_transaction(request):
    if (request.method == "POST"):
        
        requestURL = ASTROPAY_URL + "/verif/validator"
        
        # need to parse card num, code, exp date, amount, and currency from POST body
        body = json.loads(request.body)
        userid = request.user.username
        
        if checkUserBlock(CustomUser.objects.get(username=userid)):
            errorMessage = _('The current user is blocked!')
            data = {
                "errorCode": ERROR_CODE_BLOCK,
                "errorMsg": {
                    "detail": [errorMessage]
                }
            }
            return Response(data)

        # etc.
        card_num = body.get("card_num")
        card_code = body.get("card_code")
        exp_date = body.get("exp_date")
        amount = body.get("amount")
        currency = "BRL"

        orderId = user.username+"-"+timezone.datetime.today().isoformat()+"-"+str(random.randint(0,10000000))

        params = {
            "x_login": ASTROPAY_X_LOGIN,
            "x_trans_key": ASTROPAY_X_TRANS_KEY,
            "x_type": "AUTH_CAPTURE",
            "x_card_num": card_num,
            "x_card_code": card_code,
            "x_exp_date": exp_date,
            "x_amount": amount,
            "x_currency": currency,  # we are only using this API for thailand
            "x_unique_id": request.user.username,
            "x_invoice_num": orderId,
        }

        r = requests.post(requestURL, data=params)

        responseData = r.text.split("|")
        logger.info(responseData)
        if (r.status_code == 200) and (r.text[0:5] == "1|1|1"):  # create transaction record when successfully approved
            logger.info("contact AstroPay servers success and deposit success!")
            
            tranDict = {
                'order_id':(orderId)[0:20],
                'transaction_id':userid,
                'amount':amount,
                'user_id':CustomUser.objects.get(username=userid),
                'currency':2,
                'transaction_type':0,
                'channel':2,
                'status':0,
                'method':"AstroPay",
                'arrive_time': timezone.now(),
                'product': "None",
            }
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)            
            loop.run_until_complete(createDeposit(**tranDict))
        
        return JsonResponse({"request_body": body, "response_msg": r.text, "data": responseData})


async def createDeposit(**tranDict):
    task1 = asyncio.ensure_future(
        addTransToDB(**tranDict)
    )
    task2 = asyncio.ensure_future(
        send_message_sqs(**tranDict)
    )
    await task1
    await task2


async def addTransToDB(**tranDict):
    create = Transaction.objects.create(
        order_id=tranDict['order_id'],
        transaction_id=tranDict['user_id'],
        amount=tranDict['amount'],
        user_id=CustomUser.objects.get(username=tranDict['user_id']),
        currency=tranDict['currency'],
        transaction_type=tranDict['transaction_type'], 
        channel=tranDict['channel'], 
        status=tranDict['status'], 
        method=tranDict['method'],
        arrive_time=tranDict['arrive_time'],
    )
