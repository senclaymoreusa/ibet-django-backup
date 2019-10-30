from django.http import HttpResponse, JsonResponse
from games.models import GameProvider
from django.core import serializers


# Don't use db to generate live casino lobbies. Will be manually generated on front end.
# def getLiveCasinoGames(request):
#     if request.method == "GET":
#         livecas_games = GameProvider.objects.filter(type=2)
#         res_data = serializers.serialize('json', livecas_games, fields=('name', 'category', 'gameURL', 'imageURL'))
#         return HttpResponse(res_data, content_type="application/json") 