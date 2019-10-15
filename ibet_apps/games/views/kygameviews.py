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
import time


logger = logging.getLogger('django')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class KaiyuanLogin(View):
    def get(self, request, *args, **kwargs):
        data = request.body
        api = "https://kyapi.ky206.com:189/channelHandle"
        agent = "71452"
        timestamp = lambda: int(round(time.time() * 1000))
        print(timestamp())

        param = ''
        s = '0'
        account = 'Bobby'
        money = '0'
        now = timezone.now()
        order_time = now.strftime("%Y%m%d%H%M%S")
        orderid = str(agent + order_time + account)
        print(orderid)
        key = '0'
        ip = get_client_ip(request)
        print(ip)
        linecode = "00001"
        kind_id = '0' # game lobby
        param = "(s=" + s + "&account=" + account +"&money=" + money + "&orderid=" + orderid + "&ip=" + ip + "&lineCode=" + linecode + "&KindID=" + kind_id + ")"
        print(param)
        # ky_login_api = "https://kyapi.ky206.com:189/channelHandle" + "?agent=" + agent + "&timestamp=" + timestamp + "&"
        return HttpResponse(status=200)