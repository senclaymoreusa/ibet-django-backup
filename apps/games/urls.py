from django.urls import path, include
from rest_framework import routers

from .views import *

urlpatterns = [
    path('api/search/', GameSearchView.as_view(), name = 'game_search'),
    path('api/oldsearch/', GameAPIListView.as_view(), name='old_game_search')
]
