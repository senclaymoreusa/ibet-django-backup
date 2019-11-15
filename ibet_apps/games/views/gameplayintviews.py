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


MERCH_ID = ""
MERCH_PWD = ""


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