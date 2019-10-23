from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render
from xadmin.views import CommAdminView

import logging
import simplejson as json

from bonus.models import *
from utils.constants import *
from utils.admin_helper import *

logger = logging.getLogger('django')


class VIPView(CommAdminView):
    def get(self, request):
        get_type = request.GET.get("type")

        if get_type is None:
            context = super().get_context()
            context['time'] = timezone.now()
            title = "VIP overview"
            context["breadcrumbs"].append({'title': title})
            context["title"] = title
            return render(request, 'vip/vip_management.html', context)

        elif get_type == "getVIPInfo":
            result = {}
            queryset = CustomUser.objects.all()
            if request.GET.get("system") == 'vip_admin':
                try:
                    draw = int(request.GET.get('draw', 1))
                    length = int(request.GET.get('length', 20))
                    start = int(request.GET.get('start', 0))
                    search_value = request.GET.get('search[value]', None)
                    minDate = request.GET.get('minDate', None)
                    maxDate = request.GET.get('maxDate', None)

                    queryset = filterActiveUser(queryset, minDate, maxDate).order_by('-created_time')

                    #  TOTAL ENTRIES
                    total = queryset.count()

                    #  SEARCH BOX
                    if search_value:
                        queryset = queryset.filter(
                            Q(pk__icontains=search_value) | Q(username__icontains=search_value) | Q(
                                managed_by__username__icontains=search_value))

                    #  TOTAL ENTRIES AFTER FILTERED
                    count = queryset.count()

                    queryset = queryset[start:start + length]

                    result = {
                        'draw': draw,
                        'recordsTotal': total,
                        'recordsFiltered': count,
                    }

                except Exception as e:
                    logger.error("Error getting request from vip admin frontend: ", e)

            vip_list = []
            for vip in queryset:
                deposit_count, deposit_amount = calculateDeposit(vip, minDate, maxDate)
                withdrawal_count, withdrawal_amount = calculateWithdrawal(vip, minDate, maxDate)
                referee = vip.referred_by
                if deposit_count == 0:
                    ave_deposit = 0
                else:
                    ave_deposit = ("%.2f" % (deposit_amount / deposit_count))

                if referee:
                    referee = referee.pk
                else:
                    referee = ''

                vip_dict = {
                    'player_id': vip.pk,
                    'username': vip.username,
                    'status': "",
                    'player_segment': "",
                    'country': vip.country or '',
                    'address': vip.get_user_address(),
                    'phone_number': vip.phone or '',
                    'email_verified': vip.email_verified,
                    'phone_verified': vip.phone_verified,
                    'id_verified': vip.id_verified,
                    'affiliate_id': referee,  # the affiliate who referred this VIP user
                    'ggr': calculateGGR(vip, minDate, maxDate),
                    'turnover': calculateTurnover(vip, minDate, maxDate),
                    'deposit': deposit_amount,
                    'deposit_count': deposit_count,
                    'ave_deposit': ave_deposit,
                    'withdrawal': withdrawal_amount,
                    'withdrawal_count': withdrawal_count,
                    'bonus_cost': calculateBonus(vip, minDate, maxDate),
                    'ngr': calculateNGR(vip, minDate, maxDate),
                }
                vip_list.append(vip_dict)
            result['data'] = vip_list
            return HttpResponse(
                json.dumps(result), content_type="application/json"
            )

