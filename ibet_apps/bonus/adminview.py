from django.http import HttpResponse
from django.shortcuts import render
from xadmin.views import CommAdminView

from bonus.models import *
from utils.constants import *
from utils.admin_helper import *


def get_bonus_list(bonuses):
    try:
        bonuses_list = []
        for bonus in bonuses:
            #  Bonus records table data
            related_user_event = UserBonusEvent.objects.filter(bonus=bonus)
            bonuses_issued_count = related_user_event.filter(status=BONUS_ISSUED).count()
            bonuses_redeemed_count = related_user_event.filter(status=BONUS_REDEEMED).count()
            bonus_dict = {
                'name': bonus.name,
                'campaign': bonus.campaign.name or '',
                'type': bonus.get_type_display(),
                'start_date': bonus.start_time.strftime('%b %d %Y'),
                'end_date': bonus.end_time.strftime('%b %d %Y'),
                'status': bonus.get_status_display(),
                'amount_issued': bonuses_issued_count * (bonus.amount or 0),
                'quantity_issued': bonuses_issued_count,
                'amount_redeemed': bonuses_redeemed_count * (bonus.amount or 0),
                'quantity_redeemed': bonuses_redeemed_count,
            }
            bonuses_list.append(bonus_dict)
    except Exception as e:
        logger.error("Error getting Bonus object: ", e)

    return bonuses_list


class BonusRecordsView(CommAdminView):

    def get(self, request):
        get_type = request.GET.get("type")
        if get_type == 'getBonusList':
            result = {}
            try:
                draw = int(request.GET.get('draw', 1))
                length = int(request.GET.get('length', 20))
                start = int(request.GET.get('start', 0))
                search_value = request.GET.get('search[value]', None)
                order_column = int(request.GET.get('order[0][column]', 0))
                order = request.GET.get('order[0][dir]', None)
                bonus_type = int(request.GET.get('bonus_type', -1))
                bonus_status = int(request.GET.get('bonus_status', -1))

                queryset = Bonus.objects.all()

                # BONUS TYPE AND STATUS FILTER
                if bonus_type != -1 and bonus_status != -1:
                    queryset = queryset.filter(Q(status=bonus_status) & Q(type=bonus_type))
                elif bonus_type != -1:
                    queryset = queryset.filter(type=bonus_type)
                elif bonus_status != -1:
                    queryset = queryset.filter(status=bonus_status)

                queryset = queryset.order_by('start_time')

                #  TOTAL ENTRIES
                total = queryset.count()

                #  SEARCH BOX
                if search_value:
                    queryset = queryset.filter(
                        Q(name__icontains=search_value) | Q(campaign__name__icontains=search_value))

                # START TIME SORTING
                count = queryset.count()
                if order_column == 7:
                    if order == 'desc':
                        queryset = queryset.order_by('-start_time')[start:start + length]
                    else:
                        queryset = queryset.order_by('start_time')[start:start + length]
                else:
                    queryset = queryset[start:start + length]

                result = {
                    'data': get_bonus_list(queryset),
                    'draw': draw,
                    'recordsTotal': total,
                    'recordsFiltered': count,
                }

            except Exception as e:
                logger.error("Error getting Bonus List Table: ", e)

            return HttpResponse(json.dumps(result), content_type='application/json')

        else:
            context = super().get_context()
            context["breadcrumbs"].append("Bonuses / Bonus records")
            context['time'] = timezone.now()
            context['bonuses_types'] = BONUS_TYPE_CHOICES
            context['bonuses_status'] = BONUS_STATUS_CHOICES
            return render(request, "bonus_records.html", context)
