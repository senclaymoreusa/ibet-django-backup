from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.db.models import Q

from games.models import GameBet, GameProvider, Category
from users.models import CustomUser

from django.utils import timezone
from datetime import datetime
import pytz


def getProvidersAndCategories(request):
    if request.method == "GET":
        p = GameProvider.objects.all()
        c = Category.objects.all()

        return JsonResponse({
            "providers": list(p.values()),
            "categories": list(c.values())
        })

def getBetHistory(request):
    print(request)
    # date range (start/end)
    # provider
    # category
    # status (open/closed)
    if request.method == "GET":
        username = request.GET.get("userid")
        if not username:
            return HttpResponse(status=404)

        user = CustomUser.objects.get(username=username)

        all_bets = GameBet.objects.select_related().filter(user=user).order_by('-bet_time')

        if request.GET.get("status") and request.GET.get("status") == "open":
            all_bets = all_bets.filter(resolved_time__isnull=True)
        if request.GET.get("status") and request.GET.get("status") == "closed":
            all_bets = all_bets.filter(resolved_time__isnull=False)

        if request.GET.get("provider"):
            provider = request.GET.get("provider")
            all_bets = all_bets.filter(provider=provider)
        
        if request.GET.get("start"):
            startStr = request.GET.get("start")
            startDate = datetime.strptime(startStr, "%Y-%m-%d")

            all_bets = all_bets.filter(bet_time__gte=pytz.utc.localize(startDate))

        if request.GET.get("end"):
            endStr = request.GET.get("end")
            endDate = datetime.strptime(endStr, "%Y-%m-%d")
            all_bets = all_bets.filter(bet_time__lte=pytz.utc.localize(endDate))

        bet_data = []
        for bet in all_bets:
            data = dict()
            data["amount_wagered"] = bet.amount_wagered
            data["amount_won"] = bet.amount_won
            data["outcome"] = bet.get_outcome_display()
            data["date"] = bet.bet_time
            data["category"] = bet.category.name
            data["provider"] = bet.provider.provider_name
            bet_data.append(data)

        return JsonResponse({
            'results': bet_data,
            'full_raw_data': list(all_bets.values())
        })