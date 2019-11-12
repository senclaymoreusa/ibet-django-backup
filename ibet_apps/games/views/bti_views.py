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
from rest_framework.authtoken.models import Token

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
            userFromToken = (Token.objects.select_related('user').get(token=token)).user
            res = "error_code=0\r\n" # 0 = success
            res += "error_message=success\r\n"
            res += f"cust_id={userFromToken.username}\r\n"
            res += f"balance={str('%.2f' % userFromToken.main_wallet)}\r\n"
            res += "cust_login=orion\r\n"
            res += "city=Sunnyvale\r\n"
            res += "country=USA\r\n"
            res += "currency_code=CNY\r\n"
            return HttpResponse(res, content_type='text/plain')
        except ObjectDoesNotExist as e:
            logger.error(repr(e))
            res = "error_code=-2\r\n"
            res += "error_message=Token not found\r\n"
            res += "cust_id=123456789\r\n"
            res += "balance=999999.99\r\n"
            res += "cust_login=orion\r\n"
            res += "city=Sunnyvale\r\n"
            res += "country=USA\r\n"
            res += "currency_code=CNY\r\n"
            return HttpResponse(res, content_type='text/plain')


class Reserve(View):
    def post(self, request):
        username = request.GET.get("cust_id")
        bet_id = request.GET.get("reserve_id")
        amount = decimal.Decimal(request.GET.get("amount"))
        try:
            with transaction.atomic():
                user = CustomUser.objects.get(username=username)
                user.main_wallet = user.main_wallet - amount

                bet = GameBet(
                    user=user,
                    ref_no=bet_id,
                    amount_wagered=amount
                )
                bet.save()
                user.save()

        except (ObjectDoesNotExist, DatabaseError, IntegrityError) as e:
            return
                
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