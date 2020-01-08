from django.shortcuts import render, get_object_or_404
from xadmin.views import CommAdminView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.template.loader import render_to_string

from accounting.models import *
from users.models import CustomUser
from django.core import serializers
from django.utils import timezone
from django.utils.timezone import timedelta
from utils.constants import *

import simplejson as json
import logging
import datetime
import uuid

logger = logging.getLogger("django")

convStatus = {
    'active': 0,
    'disabled': 1
}
convMarket = {
    'ibet-vn': 0,
    'ibet-th': 1,
    'ibet-cn': 2,
    'letou-vn': 3,
    'letou-th': 4,
    'letou-cn': 5
}

class GetPaymentChannels(CommAdminView):
    def get(self, request):
        context = super().get_context()
        title = "Payment Configuration"
        psp_type = request.GET.get('type')
        market = request.GET.get('market')
        status = request.GET.get('status')
        search = request.GET.get('search')
        deposit_psp = []
        withdraw_psp = []
        
        if not psp_type or psp_type == "all":
            deposit_psp = DepositChannel.objects.all().order_by("channel")
            withdraw_psp = WithdrawChannel.objects.all()
        if psp_type == "deposit":
            deposit_psp = DepositChannel.objects.all()
        if psp_type == "withdraw":
            withdraw_psp = WithdrawChannel.objects.all()

        if search:
            methodQ = Q(method__icontains=search)
            channelQ = Q(channel__icontains=search)
            supplierQ = Q(supplier__icontains=search)
            if deposit_psp: 
                deposit_psp = deposit_psp.filter(methodQ | channelQ | supplierQ)
            if withdraw_psp: 
                withdraw_psp = withdraw_psp.filter(methodQ | channelQ | supplierQ)

        if market and market != "all":
            market = convMarket[market]
            marketQ = Q(market=market)
            if withdraw_psp:
                withdraw_psp = withdraw_psp.filter(marketQ)
            if deposit_psp:
                deposit_psp = deposit_psp.filter(marketQ)
        if status and status != "all":
            status = convStatus[status]
            statusQ = Q(status=status)
            if withdraw_psp:
                withdraw_psp = withdraw_psp.filter(statusQ)
            if deposit_psp:
                deposit_psp = deposit_psp.filter(statusQ)
        
        
        context["breadcrumbs"].append({"title": title})
        context["title"] = title
        context["time"] = timezone.now()
        
        context["deposits"] = deposit_psp
        context["withdraws"] = withdraw_psp
        context["days"] = range(1,32)
        context["player_segments"] = ["ALL", "Normal", 1, 2, 3, 4, 5]
        context["risk_levels"] = ["ALL", "Very low", "Low", "Medium", "High", "Very high", "VIP", "Business"]
        context["statuses"] = ["ALL", "Normal", "Suspicious", "Restricted"]
        
        return render(request, "channels.html", context)

class GetPSP(CommAdminView):
    def get(self, request):
        psp_type = request.GET.get('type')
        pk = request.GET.get('pk')
        
        if psp_type == "deposit":
            provider = DepositChannel.objects.filter(pk=pk)
        else:
            provider = WithdrawChannel.objects.filter(pk=pk)
            
        provider = serializers.serialize('json', provider)
        return HttpResponse(provider, content_type='application/json')

class scheduleDowntime(CommAdminView):
    def post(self, request):
        psp_pk = request.POST.get('pk')
        start = request.POST.get('from')
        end = request.POST.get('to')
        psp_type = request.POST.get('psp_type')
        freq = request.POST.get('frequency')
        date = request.POST.get('date')
        if not (start and end):
            return JsonResponse({
                "success": False,
                "error": "1"
            })
        try:
            if psp_type == "deposit": psp = DepositChannel.objects.get(pk=psp_pk)
            else: psp = WithdrawChannel.objects.get(pk=psp_pk)
        except Exception as e:
            logger.error("Attempting to modify unknown PSP")
        try:
            new_downtime = {
                "id": str(uuid.uuid1()),                            
                "start": start,
                "end": end
            }
            if freq == 'monthly' and date:
                new_downtime['date'] = date
            
            # clean out all old downtime entries
            res = cleanDowntime(psp.all_downtime['once'])
            logger.info("Cleaning out old downtime entries...")
            logger.info(res)
            # create new downtime entry
            psp.all_downtime[freq].append(new_downtime)
            psp.save()
            return JsonResponse({
                "success": True,
                "downtime_added": str(start) + " to " + str(end)
            })
        except Exception as e:
            logger.error(repr(e))
            return JsonResponse({
                "success": False,
                "downtime_added": None
            })
class removeDowntime(CommAdminView):
    def post(self, request):
        psp_type = request.POST.get('psp_type')
        downtimeId = request.POST.get('dt_id')
        psp = request.POST.get('psp_id')

        try:
            if psp_type == "deposit": psp = DepositChannel.objects.get(pk=psp)
            else: psp = WithdrawChannel.objects.get(pk=psp)
            res = {}
            for i in range(len(psp.all_downtime['once'])):
                if psp.all_downtime['once'][i]['id'] == downtimeId:
                    res['deleted'] = psp.all_downtime['once'][i]
                    del psp.all_downtime['once'][i]

            for i in range(len(psp.all_downtime['daily'])):
                if psp.all_downtime['daily'][i]['id'] == downtimeId:
                    res['deleted'] = psp.all_downtime['daily'][i]
                    del psp.all_downtime['daily'][i]

            for i in range(len(psp.all_downtime['monthly'])):
                if psp.all_downtime['monthly'][i]['id'] == downtimeId:
                    res['deleted'] = psp.all_downtime['monthly'][i]
                    del psp.all_downtime['monthly'][i]
            psp.save()
            res['success'] = True
            return JsonResponse(res)

        except Exception as e:
            logger.error(repr(e))
            return JsonResponse({
                'success': False,
                'error': repr(e)
            })

def cleanDowntime(downtimeArr):
    res = []
    now = datetime.datetime.now()
    for i, dt in enumerate(downtimeArr):
        endDate = datetime.datetime.strptime(dt['end'], "%d/%m/%y %H:%M%p")
        if now > endDate:
            res.append(dt['id'])
            del downtimeArr[i]
    return {
        'success': True,
        'deleted': res
    }
