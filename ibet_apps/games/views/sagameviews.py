from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import CustomUser
from django.utils import timezone
import decimal
import xmltodict
import base64
import urllib.parse
from pyDes import des, CBC, PAD_PKCS5
from games.helper import des_decrypt
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from  games.models import *
import hashlib,logging,hmac,requests,xmltodict,random,string
import xml.etree.ElementTree as ET
from time import gmtime, strftime, strptime
from rest_framework.authtoken.models import Token
from games.helper import *
from django.core.exceptions import  ObjectDoesNotExist


logger = logging.getLogger('django')

def des_decrypt(s):
    encrypt_key = 'g9G16nTs'
    iv = encrypt_key
    k = des(encrypt_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(base64.b64decode(s), padmode=PAD_PKCS5)
    return de

class SAGetUserBalance(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):

        string = str(request.body, 'utf-8')

        bytes_string = urllib.parse.unquote(string)

        str_de = des_decrypt(bytes_string)

        str_de = str_de.decode("utf-8")

        dic = { query.split('=')[0]: query.split('=')[1] for query in str_de.split('&') }

        username = dic['username']
        currency = dic['currency']


        

        try:

            user = CustomUser.objects.filter(username = username)
            balance = user[0].main_wallet
            error_code = 0

            Status = status.HTTP_200_OK

        except:

            error_code = 1000
            Status = status.HTTP_400_BAD_REQUEST


        response_data = '''<?xml version="1.0" encoding="utf-8"?><RequestResponse><username>{}</username><currency>{}</currency><amount>{}</amount><error>{}</error></RequestResponse>'''.format(username, currency, balance, error_code)

        return Response(response_data, status=Status)
        
        
class SAPlaceBet(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):

        string = str(request.body, 'utf-8')

        bytes_string = urllib.parse.unquote(string)

        str_de = des_decrypt(bytes_string)

        str_de = str_de.decode("utf-8")

        dic = { query.split('=')[0]: query.split('=')[1] for query in str_de.split('&') }

        username = dic['username']
        currency = dic['currency']
        amount   = dic['amount']
        txnid    = dic['txnid']
        gametype = dic['gametype']
        platform = dic['platform']
        gamecode = dic['gamecode']
        hostid   = dic['hostid']
        gameid   = dic['gameid']

        # GameRequestsModel.objects.create(
        #     MemberID        = username,
        #     currency        = currency,
        #     amount          = amount,
        #     txnid           = txnid,
        #     gametype        = gametype,
        #     platformType    = platform,
        #     gameCode        = gamecode,
        #     hostid          = hostid,
        #     gameId          = gameid    
        # )

        try:

            user = CustomUser.objects.filter(username = username)
            balance = user[0].main_wallet

            if balance >= decimal.Decimal(amount):

                balance -= decimal.Decimal(amount)
                user.update(main_wallet=balance, modified_time=timezone.now())

                error_code = 0
            
            else:
                error_code = 1002
                
            Status = status.HTTP_200_OK

        except:

            error_code = 1000
            Status = status.HTTP_400_BAD_REQUEST

        response_data = '''<?xml version="1.0" encoding="utf-8"?><RequestResponse><username>{}</username><currency>{}</currency><amount>{}</amount><error>{}</error></RequestResponse>'''.format(username, currency, balance, error_code)

        return Response(response_data, status=Status)


class SAPlayerWin(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):

        string = str(request.body, 'utf-8')

        bytes_string = urllib.parse.unquote(string)

        str_de = des_decrypt(bytes_string)

        str_de = str_de.decode("utf-8")

        dic = { query.split('=')[0]: query.split('=')[1] for query in str_de.split('&') }

        username   = dic['username']
        currency   = dic['currency']
        amount     = dic['amount']
        txnid      = dic['txnid']
        gametype   = dic['gametype']
        gamecode   = dic['gamecode']
        Payouttime = dic['Payouttime']
        hostid     = dic['hostid']
        gameid     = dic['gameid']

        # GameRequestsModel.objects.create(
        #     MemberID        = username,
        #     currency        = currency,
        #     amount          = amount,
        #     txnid           = txnid,
        #     gametype        = gametype,
        #     gameCode        = gamecode,
        #     time            = Payouttime,
        #     hostid          = hostid,
        #     gameId          = gameid    
        # )

        try:

            user = CustomUser.objects.filter(username = username)
            balance = user[0].main_wallet

            balance += decimal.Decimal(amount)
            user.update(main_wallet=balance, modified_time=timezone.now())

            error_code = 0
            
            Status = status.HTTP_200_OK

        except:

            error_code = 1000
            Status = status.HTTP_400_BAD_REQUEST

        response_data = '''<?xml version="1.0" encoding="utf-8"?><RequestResponse><username>{}</username><currency>{}</currency><amount>{}</amount><error>{}</error></RequestResponse>'''.format(username, currency, balance, error_code)

        return Response(response_data, status=Status)



class SAPlayerLost(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):

        string = str(request.body, 'utf-8')

        bytes_string = urllib.parse.unquote(string)

        str_de = des_decrypt(bytes_string)

        str_de = str_de.decode("utf-8")

        dic = { query.split('=')[0]: query.split('=')[1] for query in str_de.split('&') }

        username = dic['username']
        currency = dic['currency']
        txnid    = dic['txnid']
        gametype = dic['gametype']
        gamecode = dic['gamecode']
        Payouttime = dic['Payouttime']
        hostid   = dic['hostid']
        gameid   = dic['gameid']

        # GameRequestsModel.objects.create(
        #     MemberID        = username,
        #     currency        = currency,
        #     txnid           = txnid,
        #     gametype        = gametype,
        #     gameCode        = gamecode,
        #     time            = Payouttime,
        #     hostid          = hostid,
        #     gameId          = gameid    
        # )

        try:

            user = CustomUser.objects.filter(username = username)
            balance = user[0].main_wallet

            error_code = 0
            
            Status = status.HTTP_200_OK

        except:

            error_code = 1000
            Status = status.HTTP_400_BAD_REQUEST

        response_data = '''<?xml version="1.0" encoding="utf-8"?><RequestResponse><username>{}</username><currency>{}</currency><amount>{}</amount><error>{}</error></RequestResponse>'''.format(username, currency, balance, error_code)

        return Response(response_data, status=Status)


        
class SAPlaceBetCancel(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):

        string = str(request.body, 'utf-8')

        bytes_string = urllib.parse.unquote(string)

        str_de = des_decrypt(bytes_string)

        str_de = str_de.decode("utf-8")

        dic = { query.split('=')[0]: query.split('=')[1] for query in str_de.split('&') }

        username       = dic['username']
        amount         = dic['amount']
        currency       = dic['currency']
        txnid          = dic['txnid']
        gametype       = dic['gametype']
        gamecode       = dic['gamecode']
        Payouttime     = dic['Payouttime']
        hostid         = dic['hostid']
        gameid         = dic['gameid']
        txn_reverse_id = dic['txn_reverse_id']

        

        try:

            user = CustomUser.objects.filter(username = username)
            balance = user[0].main_wallet

            balance += decimal.Decimal(amount)
            user.update(main_wallet=balance, modified_time=timezone.now())

            error_code = 0
            
            Status = status.HTTP_200_OK

        except:

            error_code = 1000
            Status = status.HTTP_400_BAD_REQUEST

        response_data = '''<?xml version="1.0" encoding="utf-8"?><RequestResponse><username>{}</username><currency>{}</currency><amount>{}</amount><error>{}</error></RequestResponse>'''.format(username, currency, balance, error_code)

        return Response(response_data, status=Status)




convertCurrency = {
    1:'USD',
    2:'THB',
    10:'EUR',
    0:'CNY',
    3:'IDR',
    7:'VND',
}

def des_encrypt(s):
    encrypt_key = 'g9G16nTs'
    iv = encrypt_key
    k = des(encrypt_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return base64.b64encode(en)

def des_decrypt(s):
    encrypt_key = 'g9G16nTs'
    iv = encrypt_key
    k = des(encrypt_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(base64.b64decode(s), padmode=PAD_PKCS5)
    return de

class RegUserInfo(APIView):
    permission_classes = (AllowAny, )
    def post(self, request, *args, **kwargs):
        method = "RegUserInfo"
        username = request.POST['username']
        try:
            user = CustomUser.objects.get(username=username)
            currency = convertCurrency[user.currency]
            time = strftime("%Y%m%d%H%M%S", gmtime())

            string = "method=" + method + "&Key=" + SA_SECRET_KEY + "&Time=" + time + "&Username=" + username + "&CurrencyType=" + currency
            #string = "method=RegUserInfo&Key=F0E5C6E337F84A13960D57B06C4E361F&Time=20191030004110&Username=angela&CurrencyType=CNY"
            
            q = des_encrypt(string)
            
            s_string = string + SA_MD5KEY + time + SA_SECRET_KEY
            s = MD5(s_string)
            
            delay = kwargs.get("delay", 5)
            success = False
            for x in range(3):
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                r = requests.post(SA_API_URL, headers=headers, data={
                    "q": q,
                    "s": s,
                })
                rdata = r.text
                if r.status_code == 200:
                    success = True
                    break
                elif r.status_code == 400:
                    success = True
                    # Handle error
                    logger.error("Failed to complete a request for RegUserInfo...")
                    logger.error(rdata)
                    return Response(rdata)
                elif r.status_code == 500:
                    logger.info("Request failed {} time(s)'.format(x+1)")
                    logger.info("Waiting for %s seconds before retrying again")
                    sleep(delay)
            if not success:
                return Response(rdata)
            
            tree = ET.fromstring(rdata)
            code = tree.find('ErrorMsgId').text
            ErrorMsg = tree.find('ErrorMsg').text
            return Response({"ErrorMsgId": code,  "Message": ErrorMsg})
        except ObjectDoesNotExist as e:
            logger.error(e)

class LoginRequest(APIView):
    permission_classes = (AllowAny, )
    def post(self, request, *args, **kwargs):
        method = "LoginRequest"
        username = request.POST['username']
        try:
            user = CustomUser.objects.get(username=username)
            currency = convertCurrency[user.currency]
            time = strftime("%Y%m%d%H%M%S", gmtime())

            string = "method=" + method + "&Key=" + SA_SECRET_KEY + "&Time=" + time + "&Username=" + username + "&CurrencyType=" + currency
            q = des_encrypt(string)
            
            s_string = string + SA_MD5KEY + time + SA_SECRET_KEY
            s = MD5(s_string)
            
            delay = kwargs.get("delay", 5)
            success = False
            for x in range(3):
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                r = requests.post(SA_API_URL, headers=headers, data={
                    "q": q,
                    "s": s,
                })
                rdata = r.text
                if r.status_code == 200:
                    success = True
                    break
                elif r.status_code == 400:
                    success = True
                    # Handle error
                    logger.error("Failed to complete a request for RegUserInfo...")
                    logger.error(rdata)
                    return Response(rdata)
                elif r.status_code == 500:
                    logger.info("Request failed {} time(s)'.format(x+1)")
                    logger.info("Waiting for %s seconds before retrying again")
                    sleep(delay)
            if not success:
                return Response(rdata)
            
            tree = ET.fromstring(rdata)
            Token = tree.find('Token').text
            DisplayName = tree.find('DisplayName').text
            code = tree.find('ErrorMsgId').text
            ErrorMsg = tree.find('ErrorMsg').text
            return Response({"Token": Token,"DisplayName": DisplayName, "ErrorMsgId": code,  "Message": ErrorMsg})
        except ObjectDoesNotExist as e:
            logger.error(e)
        
        

