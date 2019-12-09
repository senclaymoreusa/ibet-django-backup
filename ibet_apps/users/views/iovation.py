from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from users.models import  CustomUser
from django.core.serializers.json import DjangoJSONEncoder
import simplejson as json
from django.db import transaction
import requests,json
import logging
from utils.constants import *
from ipware.ip import get_real_ip
import base64, datetime
import socket
from utils.aws_helper import getThirdPartyKeys

class LoginDeviceInfo(APIView):
    permission_classes = (AllowAny, )
    def get(self, request, *args, **kwargs):
        try:
            blackbox = request.GET['bb']
        except Exception as e:
            logger.error("cannot get blackbox", e)
           
        # bucket = 'ibet-admin-apdev'
        # if 'ENV' in os.environ and os.environ["ENV"] == 'approd':
        #     bucket = 'ibet-admin-approd'
        # third_party_keys = getThirdPartyKeys(bucket, "config/thirdPartyKeys.json")

        authcode = IOVATION_SUBSCRIBERID + "/" + IOVATION_ACCOUNT + ":" + IOVATION_PASSWORD
        enc = base64.encodestring(bytes(authcode, encoding='ascii'))
      
        encc = str(enc)[2:len(str(enc)) - 3]
       
        # print(socket.gethostname())
        # print(socket.gethostbyname(socket.getfqdn()))
        # print(encc)
        # ip = get_real_ip(request)
    
        # print(ip)
        headers = {
            'Content-Type': 'application/json',
            'Authorization' : 'Basic ' + encc 
            }
        data = {
            "statedIp": socket.gethostbyname(socket.getfqdn()),
            "accountCode": "device" + str(datetime.datetime.now()),
            "blackbox": blackbox,
            "type": "login"
            }

        r = requests.post(IOVATION_URL, data=json.dumps(data), headers=headers)
        rr = r.text

        return HttpResponse(rr,content_type='application/json',status=200)
