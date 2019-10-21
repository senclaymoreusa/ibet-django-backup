from django.shortcuts import render
from rest_framework.views import APIView
from django.views import View
from games.models import *
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
from django.db.models import Q, F 
from utils.constants import GAME_PROVIDERS, GAME_FILTER_OPTION

logger = logging.getLogger('django')

class GamesSearchView(View):

    def get(self, request,  *args, **kwargs):
        q = request.GET.get('q')
        gameType = request.GET.get('type')
        category = request.GET.get('category')
        filterCategory = request.GET.get('filtercategory')
        jackpot = request.GET.get('jackpot')
        provider = request.GET.get('provider')
        feature = request.GET.get('feature')
        theme = request.GET.get('theme')
        sort = request.GET.get('sort')

        # print("q: " + str(q))
        # print("type: " + str(gameType))
        # print("category: " + str(category))
        # print("filterCategory: " + str(filterCategory))
        # print("jackpot: " + str(jackpot))
        # print("provider: " + str(provider))
        # print("sort: " + str(sort))

        attributeList = []
        providerList = []
        # if gameType:
        #     attributeList = attributeList + gameType.split()
        # if category:
        #     attributeList = attributeList + category.split()
        if filterCategory:
            attributeList = attributeList + filterCategory.split('+')
        if jackpot:
            attributeList = attributeList + jackpot.split('+')
        if provider:
            providerList = provider.split('+')
        if feature:
            attributeList = attributeList + feature.split('+')
        if theme:
            attributeList = attributeList + theme.split('+')
        
        # print(str(attributeList))
        # print("feature: " + str(feature))
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
            logger.info("Searching key word: " + str(q) + "from all games")

        if gameType:
            # print(str(gameType))
            filter = filter & Q(category_id__parent_id__name__iexact=gameType)
            if category != 'all' and category:
                filter = filter & Q(category_id__name__iexact=category)
            logger.info("Filter by game category: " + str(gameType))

        providerFilter = Q()
        if provider:
            for provider in providerList:
                # print('provider: ' + str(provider))
                for gameProvider in GAME_PROVIDERS:
                    name = gameProvider[1]
                    if provider.lower() == name.lower():
                        providerFilter = providerFilter | Q(provider=gameProvider[0])
                    else:
                        providerFilter = providerFilter | Q(provider=-1)

        filter = filter & providerFilter

        for attr in attributeList:
            filter = filter & Q(attribute__icontains=attr)
            logger.info("Filter by attributes: " + str(attr)) 

        if sort == 'popularity':
            data = Game.objects.filter(filter).order_by('-popularity')
            logger.info("Order list of games by: popularity") 
        elif sort == 'jackpot-size-asc':
            data = Game.objects.filter(filter).order_by(F('jackpot_size').asc(nulls_last=True))
            logger.info("Order list of games by: jackpot size asc") 
        elif sort == 'jackpot-size-desc':
            data = Game.objects.filter(filter).order_by(F('jackpot_size').desc(nulls_last=True))
            logger.info("Order list of games by: jackpot size desc") 
        else:
            data = Game.objects.filter(filter).order_by('name')
            logger.info("Re-order list of games alphabetically by name") 

        if not data:
            logger.info('Search q did not match any categories or token')
        
        data = serializers.serialize('json', data)
        data = json.loads(data)
        logger.info("Sending search game results response......... ")
        return HttpResponse(json.dumps(data), content_type='application/json')


class ProvidersSearchView(View):

    def get(self, request,  *args, **kwargs):
        q = request.GET.get('q').lower()
        logger.info("Search providers by key word: " + str(q))
        res = []
        # print(str(q))
        for provider in GAME_PROVIDERS:
            name = provider[1]
            if q in name.lower():
                res.append(name)

        logger.info("Sending game providers response......... ")
        return HttpResponse(json.dumps(res), content_type='application/json')


class FilterAPI(View):

    def get(self, request, *args, **kwargs):
        
        logger.info("Sending filter options response......... ")
        return HttpResponse(json.dumps(GAME_FILTER_OPTION), content_type='application/json')