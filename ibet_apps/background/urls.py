from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers

import background.tasks as tasks

urlpatterns = [
    path('api/gamebet_copy', csrf_exempt(tasks.gamebet_copy), name = 'gamebet_copy'),
    path('api/transaction_copy', csrf_exempt(tasks.transaction_copy), name = 'transaction_copy'),
    path('api/user_action_copy', csrf_exempt(tasks.user_action_copy), name = 'user_action_copy'),
]



