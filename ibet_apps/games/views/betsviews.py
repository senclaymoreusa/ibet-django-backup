from django.http import JsonResponse
from django.core import serializers

from games.models import GameBet
from users.models import CustomUser


def getBetHistory(request):
    print(request)
    if request.method == "GET":
        user = CustomUser.objects.get(username=request.GET["userid"])
        all_bets = GameBet.objects.select_related().filter(username=user).order_by('-bet_time')
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
        print('hi')
        return JsonResponse({
            'results': bet_data
        })