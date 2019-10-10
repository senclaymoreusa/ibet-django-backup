from django.urls import path, include
from rest_framework import routers
from django.views.decorators.csrf import csrf_exempt
from bonus.views import *



urlpatterns = [

    path('api/bonus/', BonusSearchView.as_view(), name='bonus_search'),
    path('api/bonus/<str:pk>', BonusView.as_view(), name="bonus_id"),

]
