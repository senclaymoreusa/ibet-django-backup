from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import CustomUser, GameRequestsModel 
import simplejson as json
import xmltodict
import decimal

class YggdrasilAPI(APIView):

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):

        print(self.request.query_params)

        org                 = self.request.query_params.get('org', '')
        sessiontoken        = self.request.query_params.get('sessiontoken', '')
        cat                 = ','.join([self.request.query_params.get(item, '') for item in  ['cat1', 'cat2', 'cat3', 'cat4', 'cat5', 'cat6', 'cat7', 'cat8', 'cat9']])     
        lang                = self.request.query_params.get('lang', '')
        version             = self.request.query_params.get('version', '')
        tag                 = ','.join([self.request.query_params.get(item, '') for item in  ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6', 'tag7', 'tag8', 'tag9']]) 
        playerid            = self.request.query_params.get('playerid', '')
        amount              = self.request.query_params.get('amount', '')
        currency            = self.request.query_params.get('currency', '')
        reference           = self.request.query_params.get('reference', '')
        subreference        = self.request.query_params.get('subreference', '')
        description         = self.request.query_params.get('description', '')
        prepaidticketid     = self.request.query_params.get('prepaidticketid', '')
        prepaidvalue        = self.request.query_params.get('prepaidvalue', '')
        prepaidcost         = self.request.query_params.get('prepaidcost', '')
        prepaidref          = self.request.query_params.get('prepaidref', '')
        jackpotcontribution = self.request.query_params.get('jackpotcontribution', '')

        isJackpotWin        = self.request.query_params.get('isJackpotWin', '')
        bonusprize          = self.request.query_params.get('bonusprize', '')

        tickets             = self.request.query_params.get('tickets', '')
        singleWin           = self.request.query_params.get('singleWin', '')
        totalWin            = self.request.query_params.get('totalWin', '')
        roundCount          = self.request.query_params.get('roundCount', '')
        ruleType            = self.request.query_params.get('ruleType', '')
        cash                = self.request.query_params.get('cash', '')
        bonus               = self.request.query_params.get('bonus', '')
        campaignref         = self.request.query_params.get('campaignref', '')
        last                = self.request.query_params.get('last', '')

        gameid              = self.request.query_params.get('gameid', '')

 
        











        Status = status.HTTP_200_OK

        return Response(status=Status)