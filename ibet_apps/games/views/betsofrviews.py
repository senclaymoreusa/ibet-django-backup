from django.views import View
from django.db import DatabaseError
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.db import transaction
from users.views.helper import checkUserBlock
from users.models import CustomUser
import simplejson as json
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
import xmltodict


class BetSoftAuthenticate(View):

    def get(self, request, *args, **kwargs):
        
        # data = request.body
        # data = json.loads(data)
        token = request.GET.get('Token')
        hash = request.GET.get('Hash')
        # token = data["Token"]
        # hash = data["Hash"]

        # print(str(token), str(hash))

        user = Token.objects.get(key=token).user

        user_id = user.username
        balance = int(user.main_wallet)
        
        # print(user.username)
        if user.currency == CURRENCY_CNY:
            currency = "CNY"
        elif user.currency == CURRENCY_THB:
            currency == "THB"
        elif user.currency == CURRENCY_VND:
            currency == "VND"
        else:
            currency == "CNY"
        
        response = {
            "EXTSYSTEM": {
                "REQUEST": {
                    "TOKEN": str(token),
                    "HASH": str(hash)
                },
                "TIME": "",
                "RESPONSE": {
                    "RESULT": "OK",
                    "USERID": user_id,
                    "USERNAME": "",
                    "FIRSTNAME": "",
                    "LASTNAME": "",
                    "EMAIL": "",
                    "CURRENCY": currency,
                    "BALANCE": balance
                }
            } 
        }
        response = xmltodict.unparse(response, pretty=True)
        print(response)
        # print(user.username, user.main_wallet)

        return HttpResponse(response, content_type='text/xml')
