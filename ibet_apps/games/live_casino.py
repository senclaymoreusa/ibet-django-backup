from django.http import HttpResponse, JsonResponse
from games.models import Game
from django.core import serializers

def getLiveCasinoGames(request):
    if request.method == "GET":
        livecas_games = Game.objects.filter(category="live_casino")
        res_data = serializers.serialize('json', livecas_games, fields=('name', 'category', 'gameURL', 'imageURL'))
        return HttpResponse(res_data, content_type="application/json")