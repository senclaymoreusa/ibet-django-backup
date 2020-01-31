from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.db.models import Q

from games.models import GameBet, GameProvider, Category
from users.models import CustomUser
from dateutil.relativedelta import relativedelta

from django.utils import timezone
from datetime import datetime
import pytz
import logging
import collections

logger = logging.getLogger("django")


def getProvidersAndCategories(request):
    if request.method == "GET":
        p = GameProvider.objects.all()
        c = Category.objects.filter(parent_id__isnull=True)

        return JsonResponse({
            "providers": list(p.values()),
            "categories": list(c.values())
        })


def getBetHistory(request):
    # filter by: date range (start/end),
    # provider,
    # category,
    # status (open/closed)

    if request.method == "GET":
        try:
            user_id = request.GET.get("userid")
            if not user_id:
                return HttpResponse(status=404)

            if not request.GET.get("start") and not request.GET.get("end"):
                logger.info("Getting bet history: You have to select start or end date")
                return JsonResponse({
                    'success': False,
                    'results': "You have to select start or end date"
                })

            user = CustomUser.objects.get(pk=user_id)

            all_bets = GameBet.objects.select_related().filter(user=user).order_by('-bet_time')

            # if request.GET.get("status") and request.GET.get("status") == "open":
            #     all_bets = all_bets.filter(resolved_time__isnull=True)
            # if request.GET.get("status") and request.GET.get("status") == "closed":
            #     all_bets = all_bets.filter(resolved_time__isnull=False)

            if request.GET.get("provider"):
                provider = request.GET.get("provider")
                all_bets = all_bets.filter(provider=GameProvider.objects.get(pk=provider))

            if request.GET.get("category"):
                category = request.GET.get("category")
                all_bets = all_bets.filter(category_id=Category.objects.get(pk=category))
            
            if request.GET.get("start"):
                startStr = request.GET.get("start")
                startDate = datetime.strptime(startStr, "%Y/%m/%d")
                all_bets = all_bets.filter(bet_time__gte=pytz.utc.localize(startDate))

            if request.GET.get("end"):
                endStr = request.GET.get("end")
                endDate = datetime.strptime(endStr, "%Y/%m/%d")
                all_bets = all_bets.filter(bet_time__lt=pytz.utc.localize(endDate + relativedelta(days=1)))
            
            # all_bets.group_by = ['ref_no']

            bet_data = collections.defaultdict(lambda: None)
            
            for bet in all_bets:
                data = dict()
                data["amount_wagered"] = bet.amount_wagered
                data["amount_won"] = bet.amount_won
                data["outcome"] = bet.get_outcome_display()
                data["date"] = bet.bet_time
                data["category"] = bet.category.name
                data["provider"] = bet.provider.provider_name
                data["ref_no"] = bet.ref_no
                if bet_data[bet.ref_no]:
                    bet_data[bet.ref_no].append(data)
                else:
                    bet_data[bet.ref_no] = [data]
            
            logger.info("Successfully get bet history")
            return JsonResponse({
                'success': True,
                'results': bet_data,
                'full_raw_data': list(all_bets.values())
            })
        except Exception as e:
            logger.error("(Error) Getting bet history error: ", e)
            return JsonResponse({
                'success': False,
                'message': "There is something wrong"
            })

