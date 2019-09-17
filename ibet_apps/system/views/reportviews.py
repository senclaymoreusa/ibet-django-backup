from django.shortcuts import render
from xadmin.views import CommAdminView
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

from system.models import UserGroup, PermissionGroup, UserToUserGroup, UserPermission

from users.models import CustomUser, UserAction
from accounting.models import Transaction
from utils.constants import *
import simplejson as json
from django.views import View
from django.urls import reverse
from django.core import serializers
from system.models import *
import re
from django.db.models import Q, Sum
from utils.constants import *
import logging
from datetime import datetime, time
from dateutil.relativedelta import *
from django.core import serializers
import pytz
import requests


logger = logging.getLogger('django')


class ReportView(CommAdminView): 

    def get(self, request):
        getType = request.GET.get('type')
        # print(getType) 
        if getType == "generate_report":
            interval = request.GET.get('interval')
            currency = request.GET.get('currency')
            dateRangeFrom = request.GET.get('dateRangeFrom')
            dateRangeTo = request.GET.get('dateRangeTo')
            timePeriod = request.GET.get('timePeriod')
            market = request.GET.get('marketArray')
            device = request.GET.get('deviceArray')
            channel = request.GET.get('channelArray')

            market = json.loads(market)
            device = json.loads(device)
            channel = json.loads(channel)
                
            # print(market, device, channel)

            if interval == "Day":
                interval = relativedelta(days=1)
            elif interval == "Week":
                interval = relativedelta(weeks=1)
            elif interval == "Month":
                interval = relativedelta(months=1)

            # print(dateRangeFrom, dateRangeTo)
            now = timezone.now()
            current_tz = timezone.get_current_timezone()
            now = now.astimezone(current_tz)
            # print(now)

            if dateRangeFrom and dateRangeTo:
                dateRangeFrom = datetime.strptime(dateRangeFrom, '%m/%d/%Y')
                dateRangeTo= datetime.strptime(dateRangeTo, '%m/%d/%Y')
                data = getDateInTimeRange(dateRangeFrom, dateRangeTo, interval, currency, market)

                return HttpResponse(json.dumps(data), content_type='application/json', status=200)

            elif timePeriod:
                dateRangeTo = now
                if timePeriod == "0":
                    dateRangeFrom = now - relativedelta(weeks=1)
                elif timePeriod == "1":
                    dateRangeFrom = now - relativedelta(weeks=2)
                elif timePeriod == "2":
                    dateRangeFrom = now - relativedelta(days=30)
                elif timePeriod == "3":
                    dateRangeFrom = now - relativedelta(days=90)

                data = getDateInTimeRange(dateRangeFrom, dateRangeTo, interval, currency)
                return HttpResponse(json.dumps(data), content_type='application/json', status=200)

            else:
                return HttpResponse("Must be set a time range", content_type='application/json', status=400)

            # UserAction.object.filter(,event_type=EVENT_CHOICES_REGISTER).count()
        
        else:
            context = super().get_context()
            title = _('Group Permission')
            context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
            context['title'] = title
            context['time'] = timezone.now()
            context['imagePath'] = PUBLIC_S3_BUCKET + 'admin_images/'

            markets = {
                'ibetMarket_options': [],
                'letouMarket_options': []
            }

            for countryCode in MARKET_OPTIONS['ibetMarket_options']:
                markets['ibetMarket_options'].append({
                    'code': countryCode,
                    'name': COUNTRY_CODE_TO_IMG_PREFIX[countryCode]
                })
            for countryCode in MARKET_OPTIONS['letouMarket_options']:
                markets['letouMarket_options'].append({
                    'code': countryCode,
                    'name': COUNTRY_CODE_TO_IMG_PREFIX[countryCode]
                })

            context['markets'] = markets

            return render(request, 'performance_report.html', context)


def getDateInTimeRange(dateRangeFrom, dateRangeTo, interval, currency, market):
    marketCode = []
    marketArr = []
    if market:
        for i in market:
            if i == "CNY" and CURRENCY_CNY not in marketCode:
                marketCode.append(CURRENCY_CNY)
                marketArr.append(dict(CURRENCY_CHOICES).get(CURRENCY_CNY))
            elif (i == "DE" or i == "FI" or i == "NL") and CURRENCY_EUR not in marketCode:
                marketCode.append(CURRENCY_EUR)
                marketArr.append(dict(CURRENCY_CHOICES).get(CURRENCY_EUR))
            elif i == "NO" and CURRENCY_NOK not in marketCode:
                marketCode.append(CURRENCY_NOK)
                marketArr.append(dict(CURRENCY_CHOICES).get(CURRENCY_NOK))
            elif i == "UK" and CURRENCY_GBP not in marketCode:
                marketCode.append(CURRENCY_GBP)
                marketArr.append(dict(CURRENCY_CHOICES).get(CURRENCY_GBP))
            elif i == "VN" and CURRENCY_VND not in marketCode:
                marketCode.append(CURRENCY_VND)
                marketArr.append(dict(CURRENCY_CHOICES).get(CURRENCY_VND))
            elif i == "THB" and CURRENCY_THB not in marketCode:
                marketCode.append(CURRENCY_THB)
                marketArr.append(dict(CURRENCY_CHOICES).get(CURRENCY_THB))

    current_tz = timezone.get_current_timezone()
    tz = pytz.timezone(str(current_tz))
    date = dateRangeFrom     
    dataObj = {
        "rangeFrom": dateRangeFrom.strftime("%b %e %Y"),
        "rangeTo": dateRangeTo.strftime("%b %e %Y"),
        "currency": currency,
        "currencyCode": marketArr,
        "data": []
    }

    min_all_date_time = tz.localize(datetime.combine(dateRangeFrom, time.min)) 
    max_all_date_time = tz.localize(datetime.combine(dateRangeTo, time.max))  
    localCurrencies = Transaction.objects.filter(request_time__gt=min_all_date_time, request_time__lt=max_all_date_time).distinct('currency')
    currencyRateMap = {}
    if currency != "Local":
        for i in localCurrencies:
            local = i.currency
            if local == CURRENCY_THB:
                base = "THB"
            elif local == CURRENCY_USD:
                base = "USD"
            elif local == CURRENCY_CNY:
                base = "CNY"
            else:
                base = "USD"

            response = requests.get("https://api.exchangeratesapi.io/latest?", params={
                            "base": base,
                        })
            response = response.json()
            currencyRateMap[local] = float(response["rates"][currency])
        
    data = []
    while date < dateRangeTo:
        min_pub_date_time = tz.localize(datetime.combine(date, time.min)) 
        max_pub_date_time = tz.localize(datetime.combine(date, time.max))
        transactions = Transaction.objects.filter(request_time__gt=min_pub_date_time, request_time__lt=max_pub_date_time)
        deposits = transactions.filter(transaction_type=TRANSACTION_TYPE_DEPOSIT)
        withdraws = transactions.filter(transaction_type=TRANSACTION_TYPE_WITHDRAW)

        dateStr = date.strftime("%b %e %Y")
        dataPerUnit = {
            "date_time": dateStr,    
        }
        for i in marketCode:
            deposit_sum = 0
            withdraw_sum = 0
            register_times = UserAction.objects.filter(user__currency=i, event_type=EVENT_CHOICES_REGISTER, created_time__gt=min_pub_date_time, created_time__lt=max_pub_date_time).count()
            ftd_times = CustomUser.objects.filter(currency=i, ftd_time__gt=min_pub_date_time, ftd_time__lt=max_pub_date_time).count()
            ftd_register_ratio = float(0) if int(register_times) == 0 else float(int(ftd_times)/int(register_times))
            deposits = deposits.filter(currency=i)
            if currency != "Local":
                for deposit in deposits:
                    deposit_sum += currencyRateMap[deposit.currency] * float(deposit.amount)
                withdraws = withdraws.filter(currency=i)
                for withdraw in withdraws:
                    withdraw_sum += currencyRateMap[withdraw.currency] * float(withdraw.amount)
                dataPerUnit[dict(CURRENCY_CHOICES).get(i)] = {
                    "register_times": register_times,
                    "ftd_times": ftd_times,
                    "ftd_register_ratio": ftd_register_ratio,
                    "deposit_amount": round(float(deposit_sum), 2),
                    "withdraw_amount": round(float(withdraw_sum), 2)
                }
            else:
                for deposit in deposits:
                    deposit_sum += float(deposit.amount)
                withdraws = withdraws.filter(currency=i)
                for withdraw in withdraws:
                    withdraw_sum += float(withdraw.amount)
                dataPerUnit[dict(CURRENCY_CHOICES).get(i)] = {
                    "register_times": register_times,
                    "ftd_times": ftd_times,
                    "ftd_register_ratio": ftd_register_ratio,
                    "deposit_amount": round(float(deposit_sum), 2),
                    "withdraw_amount": round(float(withdraw_sum), 2)
                }


        # register_times = UserAction.objects.filter(user__currency__in=marketCode, event_type=EVENT_CHOICES_REGISTER, created_time__gt=min_pub_date_time, created_time__lt=max_pub_date_time).count()
        # transactions = Transaction.objects.filter(request_time__gt=min_pub_date_time, request_time__lt=max_pub_date_time)
        # deposit_sum = 0
        # deposits = transactions.filter(transaction_type=TRANSACTION_TYPE_DEPOSIT)
        # print(deposits)
        # if market:
        #     deposits = deposits.filter(currency__in=marketCode)
        # for deposit in deposits:
        #     deposit_sum += currencyRateMap[deposit.currency] * float(deposit.amount)
        
        # withdraw_sum = 0
        # withdraws = transactions.filter(transaction_type=TRANSACTION_TYPE_WITHDRAW)
        # if market:
        #     withdraws = withdraws.filter(currency__in=marketCode)
        # for withdraw in withdraws:
        #     withdraw_sum += currencyRateMap[withdraw.currency] * float(withdraw.amount)
                
        # ftd_times = CustomUser.objects.filter(currency__in=marketCode, ftd_time__gt=min_pub_date_time, ftd_time__lt=max_pub_date_time).count()
        # ftd_register_ratio = float(0) if int(register_times) == 0 else float(int(ftd_times)/int(register_times))
        # dateStr = date.strftime("%b %e %Y")
        # dataPerUnit = {
        #     "date_time": dateStr,
        #     "register_times": register_times,
        #     "deposit_amount": round(float(deposit_sum), 2),
        #     "withdraw_amount": round(float(withdraw_sum), 2),
        #     "ftd_times": ftd_times,
        #     "ftd_register_ratio": ftd_register_ratio
        # }
    
        data.append(dataPerUnit)
        date += interval
    dataObj["data"] = data    
    return dataObj
    


def getCurrency(currency):
    if currency == "Local":
        currencyRes = requests.get("https://api.ipdata.co/?api-key=test")
        currencyRes = currencyRes.json()
        currency = currencyRes["currency"]["code"]
    return currency
