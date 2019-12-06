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
            deposit_psp = DepositChannel.objects.all()
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
        print(provider)
        return HttpResponse(provider, content_type='application/json')