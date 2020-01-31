from django.shortcuts import render
from xadmin.views import CommAdminView
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from django.views import View

from users.models import CustomUser, UserAction
from accounting.models import Transaction
from utils.constants import *
import simplejson as json

from system.models import *
from django.db.models import Q, Sum
from utils.constants import *
import logging
from datetime import datetime, time
from django.core.serializers.json import DjangoJSONEncoder
from dateutil.relativedelta import *
import pytz
import requests


logger = logging.getLogger('django')
# print(settings.redshift_cursor)

class PerformanceReportView(CommAdminView): 

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

                data = getDateInTimeRange(dateRangeFrom, dateRangeTo, interval, currency, market)
                return HttpResponse(json.dumps(data), content_type='application/json', status=200)

            else:
                return HttpResponse("Must be set a time range", content_type='application/json', status=400)

            # UserAction.object.filter(,event_type=EVENT_CHOICES_REGISTER).count()
        
        else:
            context = super().get_context()
            title = _('Performance reports')
            context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
            context['title'] = title
            context['time'] = timezone.now()
            context['imagePath'] = PUBLIC_S3_BUCKET + 'admin_images/'

            markets = getMarketOpt()
            # markets = {
            #     'ibetMarket_options': [],
            #     'letouMarket_options': []
            # }

            # for countryCode in MARKET_OPTIONS['ibetMarket_options']:
            #     markets['ibetMarket_options'].append({
            #         'code': countryCode,
            #         'name': COUNTRY_CODE_TO_IMG_PREFIX[countryCode]
            #     })
            # for countryCode in MARKET_OPTIONS['letouMarket_options']:
            #     markets['letouMarket_options'].append({
            #         'code': countryCode,
            #         'name': COUNTRY_CODE_TO_IMG_PREFIX[countryCode]
            #     })

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
        deposits = transactions.filter(transaction_type=TRANSACTION_DEPOSIT, status=TRAN_SUCCESS_TYPE)
        withdraws = transactions.filter(transaction_type=TRANSACTION_WITHDRAWAL, status=TRAN_SUCCESS_TYPE)

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
        # deposits = transactions.filter(transaction_type=TRANSACTION_DEPOSIT)
        # print(deposits)
        # if market:
        #     deposits = deposits.filter(currency__in=marketCode)
        # for deposit in deposits:
        #     deposit_sum += currencyRateMap[deposit.currency] * float(deposit.amount)
        
        # withdraw_sum = 0
        # withdraws = transactions.filter(transaction_type=TRANSACTION_WITHDRAWAL)
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





class MembersReportView(CommAdminView):


    def get(self, request):
        getType = request.GET.get('type')
        if getType == "get_member_number":
            members = request.GET.get('members')
            # print(members)
            members = json.loads(members)
            data = {
                "members": [],
                "memberNumber": 0
            }
            memberArr = []
            for member in members:
                if CustomUser.objects.filter(username__iexact=member).exists():
                    memberArr.append(member)
                else:
                   pass
                
            data["members"] = memberArr
            data["memberNumber"] = len(memberArr)
            return HttpResponse(json.dumps(data), status=200, content_type='application/json')
        
        elif getType == "generate_member_report":
            marketArray = request.GET.get('marketArray')
            marketArray = json.loads(marketArray)
            members = request.GET.get('members')
            members = json.loads(members)
            affiliatesCheckBox = request.GET.get('affiliatesCheckBox')
            dataPerProductCheckBox = request.GET.get('dataPerProductCheckBox')
            lastDateRangeFrom = request.GET.get('lastDateRangeFrom')
            lastDateRangeTo = request.GET.get('lastDateRangeTo')
            registrationFrom = request.GET.get('registrationFrom')
            registrationTo = request.GET.get('registrationTo')
            # print(marketArray)
            # print(members)
            # print(affiliatesCheckBox, dataPerProductCheckBox, lastDateRangeFrom, lastDateRangeTo, registrationFrom, registrationTo)

            current_tz = timezone.get_current_timezone()
            tz = pytz.timezone(str(current_tz))

            dataObj = {
                "lastActiveDateFrom": "",
                "lastActiveDateTo": "",
                "registrationFrom": "",
                "registrationTo": "",
                "status": "",
                "affiliate": ""
            }
            
            userActionFilter = Q()
            
            if len(members) > 0:
                # print("members length greater than 0")
                for member in members:
                    userActionFilter &= Q(user__username__iexact=member)

            if lastDateRangeFrom and lastDateRangeTo:
                lastDateRangeFrom = datetime.strptime(lastDateRangeFrom, '%m/%d/%Y')
                lastDateRangeTo= datetime.strptime(lastDateRangeTo, '%m/%d/%Y')
                lastDateRangeFromTime = tz.localize(datetime.combine(lastDateRangeFrom, time.min)) 
                lastDateRangeToTime = tz.localize(datetime.combine(lastDateRangeTo, time.min))
                # UserAction.objects.filter(user__username__in=memberArr)
                userActionFilter &= (Q(created_time__gt=lastDateRangeFromTime) & Q(created_time__lt=lastDateRangeToTime) & Q(event_type=EVENT_CHOICES_LOGIN))
                dataObj["lastActiveDateFrom"] = lastDateRangeFrom.strftime("%b %e %Y")
                dataObj["lastActiveDateTo"] = lastDateRangeTo.strftime("%b %e %Y")

            
            userArr = []
            users = UserAction.objects.filter(userActionFilter).distinct('user')
            for i in users:
                userArr.append(i.user.username)

            # print(userArr)

            userfilter = Q(username__in=userArr)
            
            if registrationFrom and registrationTo:
                registrationFrom = datetime.strptime(registrationFrom, '%m/%d/%Y')
                registrationTo = datetime.strptime(registrationTo, '%m/%d/%Y')
                registrationFromTime = tz.localize(datetime.combine(registrationFrom, time.min)) 
                registrationToTime = tz.localize(datetime.combine(registrationTo, time.min))
                userfilter &= Q(time_of_registration__gt=registrationFromTime, time_of_registration__lt=registrationToTime)
                dataObj["registrationFrom"] = registrationFrom.strftime("%b %e %Y")
                dataObj["registrationTo"] = registrationTo.strftime("%b %e %Y")

            users = CustomUser.objects.filter(userfilter)
            
            data = []
            for i in users:
                user = CustomUser.objects.get(username=i.username)
                lastDeposit = Transaction.objects.filter(user_id=user, transaction_type=TRANSACTION_DEPOSIT).order_by('request_time').first()
                requestTime = ""
                lastActive = ""
                current_tz = timezone.get_current_timezone()
                if lastDeposit:
                    requestTime = lastDeposit.request_time.astimezone(current_tz)
                    lastActive = i.last_login_time.astimezone(current_tz)
                    requestTime = requestTime.strftime("%b %e %Y")
                    lastActive = lastActive.strftime("%b %e %Y")
                dataPerUser = {
                    'userId': i.pk,
                    'username': i.username,
                    'status': i.get_member_status_display(),
                    'vipLevel': 'Normal',
                    'channel': 'Desktop',
                    'product': 'Sports',
                    'country': i.country,
                    'address': i.street_address_1 + " " + i.street_address_2 + " " + i.city,
                    'phone': i.phone,
                    'verified': "No",
                    'ftd_date': i.ftd_time,
                    'affiiateId': i.pk,
                    'lastActiveDate': str(lastActive),
                    'lastDepositDate': str(requestTime)
                }
                data.append(dataPerUser)
            # print(data)
            dataObj["data"] = data
            return HttpResponse(json.dumps(dataObj, cls=DjangoJSONEncoder), status=200, content_type='application/json')

        elif getType == "generate_member_report_with_member_list":
            
            dataObj = {
                "lastActiveDateFrom": "",
                "lastActiveDateTo": "",
                "registrationFrom": "",
                "registrationTo": "",
                "status": "",
                "affiliate": ""
            }
            return HttpResponse(json.dumps(dataObj, cls=DjangoJSONEncoder), status=200, content_type='application/json')

        else:
            context = super().get_context()
            title = _('Members reports')
            context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
            context['title'] = title
            context['time'] = timezone.now()
            context['imagePath'] = PUBLIC_S3_BUCKET + 'admin_images/'
            markets = getMarketOpt()
            context['markets'] = markets


            return render(request, 'member_report.html', context)


def getMarketOpt():

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

    return markets


class FinanceReportView(CommAdminView): 

    def get(self, request):

        context = super().get_context()
        title = _('Finance reports')
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context['title'] = title
        context['time'] = timezone.now()
        context['imagePath'] = PUBLIC_S3_BUCKET + 'admin_images/'

        markets = getMarketOpt()
        context['markets'] = markets

        return render(request, 'finance_report.html', context)



# This is the class containing all APIs built on top of Redshift
class UserEventReportView (CommAdminView):

    def get(self, request):

        # This is only a template
        settings.redshift_cursor.execute("SELECT * FROM accounting_transaction_detailed;")
        rows = settings.redshift_cursor.fetchall()
        for row in rows:
            # do your reporting here
            print (row)

        return




class UserGameBetHistory(View):

    def get(self, request):

        history_type = request.GET.get('type')
        username =  request.GET.get('username')

        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')

        start_time = datetime.strptime(start_time, '%Y-%m-%d')
        end_time= datetime.strptime(end_time, '%Y-%m-%d')

        current_tz = timezone.get_current_timezone()
        tz = pytz.timezone(str(current_tz))

        start_time = tz.localize(datetime.combine(start_time, time.min)) 
        end_time = tz.localize(datetime.combine(end_time, time.max))

        # if history_type == "deposit":
        #     sum = 0
        #     result = {}
        #     data, sum = getDataFromRange(username, start_time, end_time, history_type, sum)
        #     result['overall'] = sum
        #     result['data'] = data
            
        # elif history_type == "turnover":

        #     start_time = request.GET.get('start_time')
        #     end_time = request.GET.get('end_time')

            

        # else:
        #     pass
        sum = 0
        result = {}
        data, sum = getDataFromRange(username, start_time, end_time, history_type, sum)

        result['overall_deposit'] = sum if history_type == 'deposit' else getAmount(username, start_time, end_time, 'deposit')
        result['overall_turnover'] = sum if history_type == 'turnover' else getAmount(username, start_time, end_time, 'turnover')
        result['overall_withdraw'] = getAmount(username, start_time, end_time, 'withdraw')
        result['overall_bet_casino'] = getBet(username, start_time, end_time, 'casino')
        result['overall_bet_sport'] = getBet(username, start_time, end_time, 'sport')
        result['overall_bet_games'] = getBet(username, start_time, end_time, 'games')
        result['data'] = data
        

        return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder))



def getDataFromRange(username, time_from, time_to, type, sum):

    current_tz = timezone.get_current_timezone()
    tz = pytz.timezone(str(current_tz))

    data = []
    interval = relativedelta(days=1)
    if type == 'deposit':
        date = time_from
        while date <= time_to:
            time_start = tz.localize(datetime.combine(date, time.min)) 
            time_end = tz.localize(datetime.combine(date, time.max))

            query = "SELECT CAST(SUM(amount) as DECIMAL) FROM accounting_transaction_detailed WHERE transaction_type='Deposit' and user_name='" + username + "' and request_time between '" + str(time_start) +  "' and '" + str(time_end) + "';"
            settings.REDSHIFT_CURSOR.execute(query)
            rows = settings.REDSHIFT_CURSOR.fetchone() 
            sum += rows[0] if rows[0] else 0
            row_data = {
                "data": date.strftime("%Y-%m-%d"),
                "amount": rows[0] if rows[0] else "0"
            }
            data.append(row_data)
            date += interval

        return data, sum

    elif type == 'turnover':

        date = time_from
        while date <= time_to:
            time_start = tz.localize(datetime.combine(date, time.min)) 
            time_end = tz.localize(datetime.combine(date, time.max))

            query = "SELECT SUM(amount_wagered) FROM games_gamebet_detailed WHERE user_name='" + username + "' and bet_time between '" + str(time_start) +  "' and '" + str(time_end) + "';"
            settings.REDSHIFT_CURSOR.execute(query)
            rows = settings.REDSHIFT_CURSOR.fetchone()
            sum += rows[0] if rows[0] else 0
            row_data = {
                "data": date.strftime("%Y-%m-%d"),
                "bet_amount": rows[0] if rows[0] else "0"
            }
            data.append(row_data)
            date += interval

        return data, sum

def getAmount(username, time_from, time_to, type):

    if type == "deposit":
        query = "SELECT SUM(amount) FROM accounting_transaction_detailed WHERE transaction_type='Deposit' and user_name='" + username + "' and request_time between '" + str(time_from) +  "' and '" + str(time_to) + "';"
    elif type == 'withdraw':
        query = "SELECT SUM(amount) FROM accounting_transaction_detailed WHERE transaction_type='Withdraw' and user_name='" + username + "' and request_time between '" + str(time_from) +  "' and '" + str(time_to) + "';"
    elif type == "turnover":
        query = "SELECT SUM(amount_wagered) FROM games_gamebet_detailed WHERE user_name='" + username + "' and bet_time between '" + str(time_from) +  "' and '" + str(time_to) + "';"

    settings.REDSHIFT_CURSOR.execute(query)
    rows = settings.REDSHIFT_CURSOR.fetchone() 
    return rows[0] if rows[0] else 0


def getBet(username, time_from, time_to, type):

    if type == "sport":
        query = "SELECT SUM(CAST(amount_won as DECIMAL)) FROM games_gamebet_detailed WHERE category_name='Sports' and user_name='" + username + "' and bet_time between '" + str(time_from) +  "' and '" + str(time_to) + "';"
        settings.REDSHIFT_CURSOR.execute(query)
        rows = settings.REDSHIFT_CURSOR.fetchone() 
        won = rows[0] if rows[0] else 0

        query = "SELECT SUM(CAST(amount_wagered as DECIMAL)) FROM games_gamebet_detailed WHERE category_name='Sports' and user_name='" + username + "' and bet_time between '" + str(time_from) +  "' and '" + str(time_to) + "';"
        settings.REDSHIFT_CURSOR.execute(query)
        rows = settings.REDSHIFT_CURSOR.fetchone() 
        bet = rows[0] if rows[0] else 0

    elif type == 'casino':

        query = "SELECT SUM(CAST(amount_won as DECIMAL)) FROM games_gamebet_detailed WHERE category_name='Live Casino' and user_name='" + username + "' and bet_time between '" + str(time_from) +  "' and '" + str(time_to) + "';"
        settings.REDSHIFT_CURSOR.execute(query)
        rows = settings.REDSHIFT_CURSOR.fetchone() 
        won = rows[0] if rows[0] else 0

        query = "SELECT SUM(CAST(amount_wagered as DECIMAL)) FROM games_gamebet_detailed WHERE category_name='Live Casino' and user_name='" + username + "' and bet_time between '" + str(time_from) +  "' and '" + str(time_to) + "';"
        settings.REDSHIFT_CURSOR.execute(query)
        rows = settings.REDSHIFT_CURSOR.fetchone() 
        bet = rows[0] if rows[0] else 0

    elif type == 'games':


        query = "SELECT SUM(CAST(amount_won as DECIMAL)) FROM games_gamebet_detailed WHERE category_name='Games' and user_name='" + username + "' and bet_time between '" + str(time_from) +  "' and '" + str(time_to) + "';"
        settings.REDSHIFT_CURSOR.execute(query)
        rows = settings.REDSHIFT_CURSOR.fetchone() 
        won = rows[0] if rows[0] else 0

        query = "SELECT SUM(CAST(amount_wagered as DECIMAL)) FROM games_gamebet_detailed WHERE category_name='Games' and user_name='" + username + "' and bet_time between '" + str(time_from) +  "' and '" + str(time_to) + "';"
        settings.REDSHIFT_CURSOR.execute(query)
        rows = settings.REDSHIFT_CURSOR.fetchone() 
        bet = rows[0] if rows[0] else 0

    return won - bet
