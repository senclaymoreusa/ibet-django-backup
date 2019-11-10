import datetime
import decimal
import hashlib 
import logging
import requests
import random
import simplejson as json
import uuid

from django.views import View
from django.db import DatabaseError, IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone

from users.views.helper import checkUserBlock
from users.models import CustomUser
from games.models import *
from accounting.models import *

from utils.constants import *


logger = logging.getLogger('django')


class ValidateToken(View):
    def get(self, request):
        token = request.GET.get("auth_token")
        try:
            res = "error_code=0\r\n" # 0 = success
            res += "error_msg=Token not found\r\n"
            res += "cust_id=123456789\r\n"
            res += "balance=999999\r\n"
            res += "cust_login=orion\r\n"
            res += "city=Sunnyvale\r\n"
            res += "country=USA\r\n"
            res += "extSessionId=a1b2c3d4e5\r\n"
            return HttpResponse(res)

        except ObjectDoesNotExist as e:
            logger.error(repr(e))
            res = "error_code=-2\r\n"
            res += "error_msg=Token not found\r\n"
            res += "cust_id=123456789\r\n"
            res += "balance=999999\r\n"
            res += "cust_login=orion\r\n"
            res += "city=Sunnyvale\r\n"
            res += "country=USA\r\n"
            res += "extSessionId=a1b2c3d4e5\r\n"
            return HttpResponse(res)
        
    

class Reserve(View):
    def get(self, request):
        return HttpResponse("Test test test")
    def post(self, request):
        return HttpResponse("Post Reserve")

class DebitReserve(View):
    def get(self, request):
        return HttpResponse("Test test test")
    def post(self, request):
        return HttpResponse("Post Debit Reserve")

class CommitReserve(View):
    def get(self, request):
        return HttpResponse("Test test test")
    def post(self, request):
        return HttpResponse("Post Commit Reserve")

class CancelReserve(View):
    def get(self, request):
        return HttpResponse("Test test test")
    def post(self, request):
        return HttpResponse("Post validate Token")