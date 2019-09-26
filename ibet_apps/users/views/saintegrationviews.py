from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import CustomUser, GameRequestsModel
from django.utils import timezone
import decimal
import xmltodict
import base64
import urllib.parse
from pyDes import des, CBC, PAD_PKCS5

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


        GameRequestsModel.objects.create(
            MemberID        = username,
            currency        = currency
        )

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

        GameRequestsModel.objects.create(
            MemberID        = username,
            currency        = currency,
            amount          = amount,
            txnid           = txnid,
            gametype        = gametype,
            platformType    = platform,
            gameCode        = gamecode,
            hostid          = hostid,
            gameId          = gameid    
        )

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

        GameRequestsModel.objects.create(
            MemberID        = username,
            currency        = currency,
            amount          = amount,
            txnid           = txnid,
            gametype        = gametype,
            gameCode        = gamecode,
            time            = Payouttime
            hostid          = hostid,
            gameId          = gameid    
        )

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

        GameRequestsModel.objects.create(
            MemberID        = username,
            currency        = currency,
            txnid           = txnid,
            gametype        = gametype,
            gameCode        = gamecode,
            time            = Payouttime
            hostid          = hostid,
            gameId          = gameid    
        )

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
        




