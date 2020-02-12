from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from xadmin.views import CommAdminView

import logging
import csv
import simplejson as json

from users.models import Segmentation, UserActivity
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
            context["segment_list"] = Segmentation.objects.values_list('level', flat=True)
            context["managers"] = getManagerList("VIP")
            context["empty_manager_group"] = "Please create VIP Manager group in System Admin. "

            return render(request, 'vip/vip_management.html', context)

        elif get_type == "getVIPInfo":
            result = {}
            queryset = CustomUser.objects.filter(vip_level__isnull=False).order_by('-created_time')

            if request.GET.get("system") == 'vip_admin':
                try:
                    draw = int(request.GET.get('draw', 1))
                    length = int(request.GET.get('length', 20))
                    start = int(request.GET.get('start', 0))
                    search_value = request.GET.get('search', None)
                    segment = request.GET.get('segment', None)
                    min_date = request.GET.get('minDate', None)
                    max_date = request.GET.get('maxDate', None)

                    #  TOTAL ENTRIES
                    total = queryset.count()

                    if min_date and max_date:
                        queryset = filterActiveUser(queryset, dateToDatetime(min_date),
                                                    dateToDatetime(max_date), True, None).order_by('-created_time')

                    query_filter = None
                    #  SEARCH BOX
                    if search_value:
                        query_filter = Q(pk__contains=search_value) | Q(username__icontains=search_value)

                    if segment != '-1':
                        if query_filter:
                            query_filter = query_filter & Q(vip_level__level=segment)
                        else:
                            query_filter = Q(vip_level__level=segment)

                    if query_filter:
                        queryset = queryset.filter(query_filter)

                    #  TOTAL ENTRIES AFTER FILTERED
                    count = queryset.count()

                    queryset = queryset[start:start + length]

                    result = {
                        'draw': draw,
                        'recordsTotal': total,
                        'recordsFiltered': count,
                    }

                except Exception as e:
                    logger.error("Error getting request from vip admin frontend: {}".format(str(e)))

            result['data'] = getVIPData(queryset, min_date, max_date, "list")

            return HttpResponse(json.dumps(result), content_type='application/json')

        elif get_type == 'getVIPDetailInfo':
            user_id = request.GET.get('userId')

            response = {}

            try:
                user = CustomUser.objects.get(pk=user_id)
                response = {
                    'pk': user.pk,
                    'username': user.username,
                    'segment': '',
                    'manager': '',
                    'name': str(user.first_name) + ' ' + str(user.last_name),
                    'id_number': "SL67988C",
                    'email': user.email or '',
                    'phone': user.phone or '',
                    'birthday': user.date_of_birth or '',
                    'preferred_product': "Casino",
                    'preferred_contact': "SMS",
                    'email_verified': user.email_verified,
                    'phone_verified': user.phone_verified,
                }
                if user.vip_managed_by:
                    response['manager'] = user.vip_managed_by.username
                if user.vip_level:
                    response['segment'] = user.vip_level.level
            except Exception as e:
                logger.error("Error getting VIP user: " + str(e))

            return HttpResponse(json.dumps(response), content_type="application/json")

    def post(self, request):
        post_type = request.POST.get("type")

        if post_type == "editVIPDetail":
            user_id = request.POST.get('userId')
            segment = request.POST.get('segment')
            manager = request.POST.get('manager')
            admin_user = request.POST.get('admin_user')
            change_reason = request.POST.get('changeReason')

            try:
                with transaction.atomic():
                    user = CustomUser.objects.get(pk=user_id)

                    if segment:
                        segment = Segmentation.objects.get(level=int(segment))
                        user.vip_level = segment

                    if manager is not "Select manager":
                        manager = CustomUser.objects.get(username=manager)
                        user.vip_managed_by = manager

                    user.save()

                    admin_user = CustomUser.objects.get(username=admin_user)
                    vip_change = UserActivity(
                        user=user,
                        admin=admin_user,
                        message=change_reason,
                        activity_type=ACTIVITY_REMARK
                    )
                    vip_change.save()
                    logger.info("Successfully update the information of VIP user " + str(user.username))

            except ObjectDoesNotExist:
                logger.info("Error getting vip user, manager, admin user or VIP segmentation ")

            except Exception as e:
                logger.info("Error updating vip user info: " + str(e))

            return HttpResponse(status=200)


# get data for vip admin table

def getVIPData(queryset, start_time, end_time, type):
    vip_arr = []
    for vip in queryset:
        deposit_count, deposit_amount = getTransactionAmount(vip, start_time, end_time, TRANSACTION_DEPOSIT, None)
        withdrawal_count, withdrawal_amount = getTransactionAmount(vip, start_time, end_time, TRANSACTION_WITHDRAWAL, None)
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
            'player_segment': str(vip.vip_level) or '',
            'country': vip.country or '',
            'address': vip.get_user_address(),
            'phone_number': vip.phone or '',
            'email_verified': vip.email_verified,
            'phone_verified': vip.phone_verified,
            'id_verified': vip.id_verified,
            'affiliate_id': referee,  # the affiliate who referred this VIP user
            'ggr': calculateGGR(vip, start_time, end_time, None),
            'turnover': calculateTurnover(vip, start_time, end_time, None),
            'deposit': deposit_amount,
            'deposit_count': deposit_count,
            'ave_deposit': ave_deposit,
            'withdrawal': withdrawal_amount,
            'withdrawal_count': withdrawal_count,
            'bonus_cost': getTransactionAmount(vip, start_time, end_time, TRANSACTION_BONUS, None)[1],
            'ngr': calculateNGR(vip, start_time, end_time, None),
        }
        if type == "list":
            vip_arr.append(vip_dict)
        elif type == "export":
            vip_arr.append(list(vip_dict.values()))
    return vip_arr


def exportVIP(request):
    export_title = json.loads(request.GET.get('tableHead'))
    queryset = CustomUser.objects.filter(vip_level__isnull=False).order_by('-created_time')

    vip_list = getVIPData(queryset, None, None, "export")
    vip_list.insert(0, export_title)
    return streamingExport(vip_list, 'VIP')


