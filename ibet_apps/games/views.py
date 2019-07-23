from django.shortcuts import render
from rest_framework.views import APIView
from django.views import View
from .models import *
from users.models import Game as oldGame
from users.serializers import GameSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
# Create your views here.
import logging
from django.core import serializers
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.http import HttpResponseRedirect, HttpResponse
import simplejson as json
from django.db.models import Q
from utils.constants import GAME_PROVIDERS
from .util import *

logger = logging.getLogger('django')


class GameAPIListView(ListAPIView):
    serializer_class = GameSerializer
    def get_queryset(self):
        term = self.request.GET['term']
        # print("term:" + term)
        data = oldGame.objects.filter(category_id__parent_id__name__icontains=term)

        if not data:
            data = oldGame.objects.filter(category_id__name__icontains=term)

        if not data:
            data = oldGame.objects.filter(name__icontains=term)

        if not data:
            logger.error('Search term did not match any categories or token')
        return data


class GamesSearchView(View):

    # permission_classes = (AllowAny,)

    def get(self, request,  *args, **kwargs):
        q = request.GET.get('q')
        gameType = request.GET.get('type')
        category = request.GET.get('category')
        filterCategory = request.GET.get('filtercategory')
        jackpot = request.GET.get('jackpot')
        provider = request.GET.get('provider')
        jackpot = request.GET.get('jackpot')
        provider = request.GET.get('provider')
        fearture = request.GET.get('feature')
        theme = request.GET.get('theme')
        sort = request.GET.get('sort')

        # print("q: " + str(q))
        # print("type: " + str(gameType))
        # print("category: " + str(category))
        # print("filterCategory: " + str(filterCategory))
        # print("jackpot: " + str(jackpot))
        # print("provider: " + str(provider))
        attributeList = []
        # if gameType:
        #     attributeList = attributeList + gameType.split()
        if category:
            attributeList = attributeList + category.split()
        if filterCategory:
            attributeList = attributeList + filterCategory.split()
        if jackpot:
            attributeList = attributeList + jackpot.split()
        if provider:
            attributeList = attributeList + provider.split()
        if fearture:
            attributeList = attributeList + fearture.split()
        if theme:
            attributeList = attributeList + theme.split()
        
        # print(str(attributeList))
        # print("fearture: " + str(fearture))
        # print("theme: " + str(theme))
        # print("sort: " + str(sort))

        filter = Q()
        if q:
            filter |= (
                # Q(name__icontains=q)|Q(name_zh__icontains=q)|
                # Q(name_fr__icontains=q)|Q(description__icontains=q)|
                # Q(description_zh__icontains=q)|Q(description_fr__icontains=q)| 
                # Q(attribute__icontains=q)|Q(category_id__name__icontains=q)
                Q(name__icontains=q)|Q(name_zh__icontains=q)|
                Q(name_fr__icontains=q)
            )

        if gameType:
            # print(str(gameType))
            filter = filter & Q(category_id__name__icontains=gameType) 

        for attr in attributeList:
            filter = filter & Q(attribute__icontains=attr) 

        # if sort == 'name':
        #     data = Game.objects.filter(filter).order_by('name')
        if sort == 'popularity':
            data = Game.objects.filter(filter).order_by('-popularity')
        elif sort == 'jackpot-size-asc-rank':
            data = Game.objects.filter(filter).order_by('jackpot_size')
        elif sort == 'jackpot-size-desc-rank':
            data = Game.objects.filter(filter).order_by('-jackpot_size')
        else:
            data = Game.objects.filter(filter).order_by('name')

        if not data:
            logger.error('Search q did not match any categories or token')
        
        # print("!!!!" + str(data))
        data = serializers.serialize('json', data)
        data = json.loads(data)
        return HttpResponse(json.dumps(data), content_type='application/json')


class ProvidersSearchView(View):

    def get(self, request,  *args, **kwargs):
        q = request.GET.get('q').lower()
        res = []
        # print(str(q))
        for provider in GAME_PROVIDERS:
            name = provider[1]
            if q in name.lower():
                res.append(name)

        return HttpResponse(json.dumps(res), content_type='application/json')


class FilterAPI(View):

    def get(self, request, *args, **kwargs):
        
        return HttpResponse(json.dumps(GAME_FILTER_OPTION), content_type='application/json')