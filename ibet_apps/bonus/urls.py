from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from bonus.views import *



urlpatterns = [
    path('api/bonuses/', BonusSearchView.as_view(), name='bonus_search'),
    path('api/bonus/<str:name>', csrf_exempt(BonusView.as_view()), name="bonus_name"),
    path('api/ubevent/', csrf_exempt(UserBonusEventView.as_view()), name="user_bonus_event"),
]