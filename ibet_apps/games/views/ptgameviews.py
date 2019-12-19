from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from users.models import  CustomUser
from django.core.serializers.json import DjangoJSONEncoder
import simplejson as json
from games.models import FGSession, Game, GameBet, GameProvider, Category
from django.db import transaction
import xmltodict
import decimal,re, math
import requests,json
import logging
import random
from utils.constants import *
import datetime
from datetime import date
from django.utils import timezone

logger = logging.getLogger("django")

class PTtest(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
        headers = {
            'Pragma': '',
            'Keep-Alive': 'timeout=5, max=100',
            'X_ENTITY_KEY': '19969fca479e990e5eec11bc1db6cd5f711132a52eb99df9a02587c11ee2d9472a2cf1b3ad437d1d2f147b8923a200e70e670c1c06920c12280c9603f70e9fe2'

        }
        rr = requests.get("https://kioskpublicapi.luckydragon88.com/entity/list", headers=headers)
        
        if rr.status_code == 200 :    
               
            rrdata = rr.json()
            data = {
                "test" : None
            }
           
        return HttpResponse(json.dumps(rrdata),content_type='application/json',status=200)