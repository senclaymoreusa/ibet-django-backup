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

class LoginDeviceInfo(APIView):
    permission_classes = (AllowAny, )
    def get(self, request, *args, **kwargs):
        blackbox = request.GET['bb']
        print(IOVATION_SUBSCRIBERID)
        authcode = IOVATION_SUBSCRIBERID + "/" + ACCOUNT + ":" + PASSWORD
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

        r = requests.post(IOVATION_CHECK, data=json.dumps(data), headers=headers)
        rr = r.text

        return HttpResponse(rr,content_type='application/json',status=200)
