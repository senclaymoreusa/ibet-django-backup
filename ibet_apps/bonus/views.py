from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from django.views import View
from bonus.models import *
#from users.models import Game as oldGame
#from users.serializers import GameSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
# Create your views here.
import logging
from django.core import serializers
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.http import HttpResponseRedirect, HttpResponse
import simplejson as json
from django.db.models import Q, F
from utils.constants import *

logger = logging.getLogger('django')

# Create your views here.

class BonusSearchView(View):

    def get(self, request, *args, **kwargs):








        data = Bonus.objects.all()
        data = serializers.serialize('json', data)
        data = json.loads(data)
        return HttpRespnse(json.dumps(data), content_type='application/json')











