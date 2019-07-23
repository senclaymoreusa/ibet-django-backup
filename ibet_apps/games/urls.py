from django.urls import path, include
from rest_framework import routers

from .views import *

urlpatterns = [
    path('api/games/', GamesSearchView.as_view(), name = 'games_search'),
    path('api/providers/', ProvidersSearchView.as_view(), name = 'provider_search'),
    path('api/oldsearch/', GameAPIListView.as_view(), name='old_game_search'),
    path('api/filter/', FilterAPI.as_view(), name='get_filter')
]
