import logging

from django.shortcuts import render
from rest_framework.views import APIView
from django.views import View
from games.models import Game, GameProvider, Category
from games.serializers import GameSerializer, CategorySerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
# Create your views here.

from django.core import serializers
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.http import HttpResponseRedirect, HttpResponse
import simplejson as json
from django.db.models import Q, F 
from utils.constants import *

logger = logging.getLogger('django')

class GamesSearchView(View):

    def get(self, request,  *args, **kwargs):
        q = request.GET.get('q')
        # gameType = request.GET.get('type')
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
        # print('theme:' + str(theme))
        # print('featrue:' + str(feature))

        attributeList = []
        providerList = []
        # if gameType:
        #     attributeList = attributeList + gameType.split()
        # if category:
        #     attributeList = attributeList + category.split()

        if provider:
            providerList = provider.split('+')
        if filterCategory:
            attributeList = attributeList + filterCategory.split('+')
        if jackpot:
            attributeList = attributeList + jackpot.split('+')
        if feature:
            attributeList = attributeList + feature.split('+')
        if theme:
            attributeList = attributeList + theme.split('+')
        
        # print(providerList)
        # print(str(attributeList))
        # print("feature: " + str(feature))
        # print("theme: " + str(theme))
        # print("sort: " + str(sort))
        try:
            games_category = Category.objects.get(name='Games')
            all_child_category_of_games = Category.objects.filter(parent_id=games_category)
        except:
            logger.error("Cannot find Games category")
        
        category_pk_arr = []
        for i in all_child_category_of_games:
            category_pk_arr.append(
                { 'pk': str(i.pk), 'name': i.name }
            )
        
        gameFilter = (Q(category_id__parent_id=games_category)|Q(category_id=games_category))
        if q:
            gameFilter &= (
                # Q(name__icontains=q)|Q(name_zh__icontains=q)|
                # Q(name_fr__icontains=q)|Q(description__icontains=q)|
                # Q(description_zh__icontains=q)|Q(description_fr__icontains=q)| 
                # Q(attribute__icontains=q)|Q(category_id__name__icontains=q)
                Q(name__icontains=q)|Q(name_zh__icontains=q)|
                Q(name_fr__icontains=q)
            )
            logger.info("Searching key word: " + str(q) + "from all games")

        # if gameType:
        #     # print(str(gameType))
        #     gameFilter = gameFilter & Q(category_id__parent_id__name__iexact=gameType)
        #     if category != 'all' and category:
        #         gameFilter = gameFilter & Q(category_id__name__iexact=category)
        #     logger.info("Filter by game category: " + str(gameType))
        if category != 'all' and category:
            # category = category.split('-')
            category = ' '.join(category.split('-'))
            gameFilter = gameFilter & Q(category_id__name__iexact=category)

        # providerFilter = Q()
        # if provider:
        #     gameFilter |= (
        #         Q(provider__provider_name__icontains=q)
            # all_providers = GameProvider.objects.all()
            # for each_provider in providerList:
            #     # print('provider: ' + str(provider))
            #     for gameProvider in GAME_PROVIDERS:
            #         name = gameProvider[1]
            #         if provider.lower() == name.lower():
            #             providerFilter = providerFilter | Q(provider=gameProvider[0])
            #         else:
            #             providerFilter = providerFilter | Q(provider=-1)
            # GameProvider.objects.all()


        # gameFilter = gameFilter & providerFilter
        providerFilter = Q()
        if provider:
            for i in providerList:
                providerFilter |= (
                    Q(provider__provider_name__icontains=i)
                )
        gameFilter &= providerFilter

        for attr in attributeList:
            gameFilter = gameFilter & Q(attribute__icontains=attr)
            logger.info("Filter by attributes: " + str(attr)) 

        if sort == 'popularity':
            data = Game.objects.filter(gameFilter).order_by('-popularity')
            logger.info("Order list of games by: popularity") 
        elif sort == 'jackpot-size-asc':
            data = Game.objects.filter(gameFilter).order_by(F('jackpot_size').asc(nulls_last=True))
            logger.info("Order list of games by: jackpot size asc") 
        elif sort == 'jackpot-size-desc':
            data = Game.objects.filter(gameFilter).order_by(F('jackpot_size').desc(nulls_last=True))
            logger.info("Order list of games by: jackpot size desc") 
        else:
            data = Game.objects.filter(gameFilter).order_by('name')
            logger.info("Re-order list of games alphabetically by name") 
        
        
        if not data:
            logger.info('Search q did not match any categories or token')
        
        data = serializers.serialize('json', data)
        data = json.loads(data)

        for i in data:
            for category_obj in category_pk_arr:
                if category_obj['pk'] == i['fields']['category_id']:
                    i['fields']['category_name'] = category_obj['name']

        logger.info("Sending search game results response......... ")
        return HttpResponse(json.dumps(data), content_type='application/json')


class ProvidersSearchView(View):

    def get(self, request,  *args, **kwargs):

        try:
            q = request.GET.get('q')
            logger.info("Search providers by keyword: " + str(q))
            res = []
            # print(str(q))
            providers = GameProvider.objects.filter(type=GAME_TYPE_GAMES)
            if not q:
                for provider in providers:
                    res.append(provider.provider_name)
            
            else:
                q = q.lower()
                for provider in providers:
                    name = provider.provider_name
                    if q in name.lower():
                        res.append(name)

            logger.info("Sending game providers response......... ")
            # print(res)
            return HttpResponse(json.dumps(res), content_type='application/json')

        except Exception as e:
            logger.error("Error getting GameProvider objects: ", e)
            return HttpResponse(status=400)


class FilterAPI(View):

    def get(self, request, *args, **kwargs):
        
        logger.info("Sending filter options response......... ")
        res = []
        providers = GameProvider.objects.filter(type=1)
        for provider in providers:
            res.append(provider.provider_name)
        GAME_FILTER_OPTIONS['Providers'] = res
        return HttpResponse(json.dumps(GAME_FILTER_OPTIONS), content_type='application/json')


class GameDetailAPIListView(ListAPIView):
    
    serializer_class = GameSerializer
    def get_queryset(self):
        id = self.request.GET['id']
        data = Game.objects.filter(pk=id)
        return data


class CategoryAPIListView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()



class GamesCategoryAPI(View):

    def get(self, request, *args, **kwargs):
        
        try:
            categories = Category.objects.filter(parent_id__name="Games")
            res = []
            for i in categories:
                res.append(i.name)
        except Exception as e:
            logger.error("Error: getting all the slot category")

        return HttpResponse(json.dumps(res), content_type='application/json')