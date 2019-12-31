from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.db import DatabaseError
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from django.db import transaction
from users.views.helper import checkUserBlock
from users.models import CustomUser
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
import json

from rest_framework.authtoken.models import Token
import xmltodict


MERCH_ID = "IBETP"
MERCH_PWD = "2C19AA9A-E3C6-4202-B29D-051E756736DA"


class GPILoginView(View):
    def post(self, request, *kw, **args):

        data = json.loads(request.body)
        username = data["username"]

        user = CustomUser.objects.get(username=username)

        merch_id = MERCH_ID
        merch_pwd = MERCH_PWD

        url = "http://club8api.bet8uat.com/op/createuser?"
        url += "&merch_id" + MERCH_ID
        url += "&merch_pwd=" + MERCH_PWD
        url += "&cust_id=" + username
        url += "&cust_name=" + str(user.pk)
        url += "&currency=" + str(user.currency)

        res = requests.get(url)

        return HttpResponse(res.status_code)


class ValidateUserAPI(View):
    def get(self, request, *kw, **args):
        token = request.GET.get('ticket')
        res = {}

        try:
            user = Token.objects.get(key=token).user

            res["error_code"] = 0
            res["cust_id"] = user.pk
            res["cust_name"] = user.username
            res["currency_code"] = currency_code
            res["language"] = "language"
            res["country"] = "country"
            res["ip"] = ip
            res["date_of_birth"] = date_of_birth
            res["test_cust"] = True
        except ObjectDoesNotExist:
            return "Not a good user"
        except Exception as e:
            return "Error: {}".format(repr(e))
