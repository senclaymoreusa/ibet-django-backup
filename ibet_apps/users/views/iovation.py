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
from ipware import get_client_ip
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
        
        ip, is_routable = get_client_ip(request)
        if ip is None:
            # Unable to get the client's IP address
            logger.error("Unable to get the client's IP address")

        # else:
        #     # We got the client's IP address
        #     if is_routable:
        #         # The client's IP address is publicly routable on the Internet
        #         print("test1")
              
        #     else:
        #         # The client's IP address is private
        #         print("test2")
               
        authcode = IOVATION_SUBSCRIBERID + "/" + IOVATION_ACCOUNT + ":" + IOVATION_PASSWORD
        enc = base64.encodestring(bytes(authcode, encoding='ascii'))
      
        encc = str(enc)[2:len(str(enc)) - 3]
       
       
        headers = {
            'Content-Type': 'application/json',
            'Authorization' : 'Basic ' + encc 
            }

        #give a default value first if cannot get the statedIp..
        # statedIp = "192.168.86.121"
        # print(socket.gethostbyname(socket.getfqdn()))
        # try: 
        #     statedIp = socket.gethostbyname(socket.gethostname())
        # except socket.gaierror as e: 
        #     try: 
        #         statedIp = socket.gethostbyname(socket.gethostname() + '.local')
        #     except: 
        #         pass
        # except: 
        #     pass
        data = {
            "statedIp": ip,
            "accountCode": "device" + str(datetime.datetime.now()),
            "blackbox": blackbox,
            "type": "login"
        }


        r = requests.post(IOVATION_URL, data=json.dumps(data), headers=headers)
        rr = r.text

        return HttpResponse(rr,content_type='application/json',status=200)
