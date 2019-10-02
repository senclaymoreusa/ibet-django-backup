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


class InplayLoginAPI(View):
    def get(self, request, *arg, **kwargs):
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

        # print(action, requestId, propertiesUserId, propertiesPassword)

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


class InplayGetBalanceAPI(View):
    def get(self, request, *arg, **kwargs):
        params = requests
        return HttpResponse(status=200)


class InplayGetApprovalAPI(View):
    return HttpResponse(status=200)


class InplayDeductBalanceAPI(View):
    return HttpResponse(status=200)


class InplayUpdateBalanceAPI(View):
    return HttpResponse(status=200)