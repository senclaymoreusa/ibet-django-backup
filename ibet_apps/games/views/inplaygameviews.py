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
import json


logger = logging.getLogger('django')


class InplayLoginAPI(View):
    def get(self, request, *arg, **kwargs):
        user = 'Bobby'
        name = 'too much'
        print(data['Token'])
        return HttpResponse(status=200)


class InplayGetBalanceAPI(View):
    def get(self, request, *arg, **kwargs):
        params = requests
        return HttpResponse(status=200)


# class InplayGetApprovalAPI(View):
#     return HttpResponse(status=200)


# class InplayDeductBalanceAPI(View):
#     return HttpResponse(status=200)


# class InplayUpdateBalanceAPI(View):
#     return HttpResponse(status=200)