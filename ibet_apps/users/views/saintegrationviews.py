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

        s = str(request.body, 'utf-8')

        b_s = urllib.parse.unquote(s)

        str_de = des_decrypt(b_s)

        str_de = str_de.decode("utf-8")

        dic = { query.split('=')[0]: query.split('=')[1] for query in str_de.split('&') }

        Status = status.HTTP_200_OK

        response_data = '''<?xml version="1.0" encoding="utf-8"?><RequestResponse><username>{}</username><currency>{}</currency><amount>{}</amount><error>{}</error></RequestResponse>'''.format('1','2','3','4')

        return Response(response_data, status=Status)
        
        
