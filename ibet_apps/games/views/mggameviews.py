from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from users.models import  CustomUser
from django.core.serializers.json import DjangoJSONEncoder
import simplejson as json
from games.models import FGSession
import xmltodict
import decimal
import requests,json
import logging
from utils.constants import *

logger = logging.getLogger("django")

MG_RESPONSE_ERROR = {
    "6001" : "The player token is invalid.",
    "6002" : "The player token expired.",
    "6101" : "Login validation failed. Login name or password is incorrect.",
    "6102" : "Account is locked.",
    "6103" : "Account does not exist."
   
}

class MGLogin(APIView):

    permission_classes = (AllowAny, )
    def get(self, request, *args, **kwargs):
        data = request.body
        print(data)
        dd = xmltodict.parse(data)

        name = dd['pkt']['methodcall']['@name']
        timestamp = dd['pkt']['methodcall']['@timestamp']
        loginname = dd['pkt']['methodcall']['auth']['@login']
        seq = dd['pkt']['methodcall']['call']['@seq']
        token = dd['pkt']['methodcall']['call']['@token']
        print(name)
        response = {
            "pkt" : {
                "methodresponse" : {
                    "@name" : name,
                    "@timestamp" : timestamp,
                    "result" : {
                        "@seq" : seq,
                        "@token" : token,
                        "@loginname" : loginname,
                        "@currency" : "USD",
                        "@country" : "USA",
                        "@city" : "NY",
                        "@balance" : "0",
                        "@bonusbalance" : "0",
                        "@wallet" : "vanguard",
                        "extinfo" : {}
                    },
                    
                }
            }
        }
        res = xmltodict.unparse(response, pretty=True)
        return HttpResponse(res, content_type='text/xml')

class GetBalance(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):   
        data = request.body
        print(data)
        dd = xmltodict.parse(data)

        name = dd['pkt']['methodcall']['@name']
        timestamp = dd['pkt']['methodcall']['@timestamp']
        loginname = dd['pkt']['methodcall']['auth']['@login']
        seq = dd['pkt']['methodcall']['call']['@seq']
        token = dd['pkt']['methodcall']['call']['@token']
        response = {
            "pkt" : {
                "methodresponse" : {
                    "@name" : name,
                    "@timestamp" : timestamp,
                    "result" : {
                        "@seq" : seq,
                        "@token" : token,
                        "@balance" : "0",
                        "@bonusbalance" : "0",
                        "extinfo" : {}
                    },
                    
                }
            }
        }
        res = xmltodict.unparse(response, pretty=True)
        return HttpResponse(res, content_type='text/xml')