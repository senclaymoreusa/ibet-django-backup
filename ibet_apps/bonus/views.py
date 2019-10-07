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

    # Returns a dictionary in JSON where the key is the PK of each bonus, and the value is the whole object
    # (containing all the requirements as a list)
    # This will also return bonuses that are NOT active.
    def get(self, request, *args, **kwargs):

        bonuses = {}

        # We iterate through all requirements and find all bonuses that they are attached to
        reqs = Requirement.objects.filter()
        for req in reqs:

            bonus_data = serializers.serialize('json', [req.bonus])
            bonus_data = json.loads(bonus_data)
            req_data = serializers.serialize('json', [req])
            req_data = json.loads(req_data)

            pk = bonus_data[0]['pk']
            if pk in bonuses:
                bonuses[pk]['requirements'].append(req_data)
            else:
                bonuses[pk] = bonus_data[0]['fields']
                bonuses[pk]['requirements'] = [req_data]

        # In rare cases, there could be bonuses that do not have any requirements
        bonus_all = Bonus.objects.filter()
        for bonus in bonus_all:
            if str(bonus.pk) in bonuses.keys():
                continue
            bonus_left = serializers.serialize('json', [bonus])
            bonus_left = json.loads(bonus_left)
            bonuses[bonus_left[0]['pk']] = bonus_left[0]['fields']

        return HttpResponse(json.dumps(bonuses), content_type='application/json')











