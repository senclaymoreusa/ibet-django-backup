from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.utils import timezone
from django.db.models import Q

import datetime

from accounting.models import Transaction, DepositChannel, WithdrawChannel
from users.models import CustomUser, WithdrawAccounts
from utils.admin_helper import utcToLocalDatetime
from utils.constants import *
import json
import pytz
import random
import logging



def checkAvailable(txn_type, market):
    if txn_type == 'deposit':
        channels = DepositChannel.objects.filter(market=market)
    else:
        channels = WithdrawChannel.objects.filter(market=market)
    now = datetime.datetime.now()
    for psp in channels:
        downtime = False # set current PSP's downtime flag to False
        for dt in psp.all_downtime["once"]:
            start = datetime.datetime.strptime(dt["start"], "%Y/%m/%d %I:%M%p")
            end = datetime.datetime.strptime(dt["end"], "%Y/%m/%d %I:%M%p")
            if now >= start and now <= end: # PSP currently has downtime
                psp.status = 1
                downtime = True
                psp.save()
                break
            # else:
            #     del psp.all_downtime["once"]
        for dt in psp.all_downtime["daily"]:
            start_hour = getHour(dt["start"])
            start_min = getMinute(dt["start"])
            end_hour = getHour(dt["end"])
            end_min = getMinute(dt["end"])
            if now.hour >= start_hour and now.minute >= start_min and now.minute <= end_min and now.hour <= end_hour:
                psp.status = 1
                downtime = True
                psp.save()
                break
        for dt in psp.all_downtime["monthly"]:
            if now.day == int(dt["date"]):
                start_hour = getHour(dt["start"])
                start_min = getMinute(dt["start"])
                end_hour = getHour(dt["end"])
                end_min = getMinute(dt["end"])
                if now.hour >= start_hour and now.minute >= start_min and now.minute <= end_min and now.hour <= end_hour:
                    psp.status = 1
                    downtime = True
                    psp.save()
                    break
        psp.status = 1 if downtime else 0
        psp.save()
    channels = channels.filter(status=0)
    return channels

def getActivePSP(request):
    txn_type = request.GET.get("txn_type")
    market = request.GET.get("market_code")
    available = checkAvailable(txn_type, market)
    
    return HttpResponse(serializers.serialize('json', available), content_type='application/json')



def getHour(time):
    hour = int(time[:2]) if len(time) == 7 else int(time[:1])
    if time[-2:] == "pm":
        hour+=12
    return hour

def getMinute(time):
    minute = int(time[3:5]) if len(time) == 7 else int(time[2:4])
    return minute