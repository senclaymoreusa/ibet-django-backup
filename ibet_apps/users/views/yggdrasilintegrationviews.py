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
        
        # Bet API
        if sessiontoken and org and playerid and amount and currency and reference and subreference and description and prepaidticketid and prepaidvalue and prepaidcost and prepaidref and jackpotcontribution and cat and tag and lang and version:
  
            GameRequestsModel.objects.create(
                sessionToken        = sessiontoken,
                organization        = org,
                MemberID            = playerid,
                value               = amount,
                currency            = currency,
                reference           = reference,
                subreference        = subreference,
                description         = description,
                prepaidticketid     = prepaidticketid,
                prepaidvalue        = prepaidvalue,
                prepaidcost         = prepaidcost,
                prepaidref          = prepaidref,
                jackpotcontribution = jackpotcontribution,
                cat                 = cat,
                tag                 = tag,
                lang                = lang,
                version             = version
            )

            try:
                user = CustomUser.objects.filter(username = playerid)
                temp = user[0].main_wallet
                if temp >= decimal.Decimal(amount):
                    current_balance = temp - decimal.Decimal(amount)
                    user.update(main_wallet=current_balance)
                    data = {
                        "code": 0,
                        "data":{
                            "organization":         org,
                            "playerId":             playerid,
                            "currency":             currency,
                            "applicableBonus":      "",
                            "homeCurrency":         "",
                            "balance":              current_balance,
                            "nickName":             user[0].username,
                            "bonus":                "",
                            "gameHistorySessionId": "",
                            "gameHistoryTicketId":  ""
                        }
                    }

                    Status = status.HTTP_200_OK

                else:
                    data = {
                        "code": 1002,
                        'msg': 'Insufficient_Balance'
                    }
            except:
 
                data = {
                        "code": 1003,
                        'msg': 'User_Not_Exist'
                    }


        # Cancel
        elif playerid and reference and subreference and org and version and not amount:

            GameRequestsModel.objects.create(
                MemberID     = playerid,
                reference    = reference,
                subreference = subreference,
                organization = org,
                version      = version
            )

            try:

                user = CustomUser.objects.filter(username = playerid)
                balance = user[0].main_wallet

                data = {
                        "code": 0,
                        "data":{
                            "organization":         org,
                            "playerId":             playerid,
                            "currency":             currency,
                            "balance":              balance,
                            "bonus":                "",
                        }
                    }

                Status = status.HTTP_200_OK

            except:

                data = {
                        "code": 1003,
                        'msg': 'User_Not_Exist'
                    }


        # Append
        elif org and playerid and amount and isJackpotWin and bonusprize and currency and reference and subreference and description and cat and tag and lang and version:
           
            GameRequestsModel.objects.create(
               organization = org,
               MemberID     = playerid,
               value        = amount,
               isJackpotWin = isJackpotWin,
               bonusprize   = bonusprize,
               currency     = currency,
               reference    = reference,
               subreference = subreference,
               description  = description,
               cat          = cat,
               tag          = tag,
               lang         = lang,
               version      = version
            )

            try:

                user = CustomUser.objects.filter(username = playerid)
                balance = user[0].main_wallet

                data = {
                        "code": 0,
                        "data":{
                            "organization":         org,
                            "playerId":             playerid,
                            "currency":             currency,
                            "applicableBonus":      "",
                            "homeCurrency":         "",
                            "balance":              balance,
                            "nickName":             user[0].username,
                            "bonus":                "",
                        }
                    }

                Status = status.HTTP_200_OK

            except:

                data = {
                        "code": 1003,
                        'msg': 'User_Not_Exist'
                    }

        # End bet
        elif org and playerid and amount and isJackpotWin and bonusprize and currency and tickets and reference and subreference and description and cat and tag and lang and version and prepaidref and prepaidticketid and singleWin and totalWin and roundCount and ruleType:
            
            GameRequestsModel.objects.create(
                organization    = org,
                MemberID        = playerid,
                value           = amount,
                isJackpotWin    = isJackpotWin,
                bonusprize      = bonusprize,
                currency        = currency,
                tickets         = tickets,
                reference       = reference,
                subreference    = subreference,
                description     = description,
                cat             = cat,
                tag             = tag,
                lang            = lang,
                version         = version,
                prepaidref      = prepaidref,
                prepaidticketid = prepaidticketid,
                singleWin       = singleWin,
                totalWin        = totalWin,
                roundCount      = roundCount,
                ruleType        = ruleType
            )

            try: 

                user = CustomUser.objects.filter(username = playerid)
                balance = user[0].main_wallet

                current_balance = balance + decimal.Decimal(totalWin)
                user.update(main_wallet=current_balance)
    
                data = {
                        "code": 0,
                        "data":{
                            "organization":         org,
                            "playerId":             playerid,
                            "currency":             currency,
                            "applicableBonus":      "",
                            "homeCurrency":         "",
                            "balance":              current_balance,
                            "nickName":             user[0].username,
                            "gameSessionBalance":   "",
                            "gameParticipation":    "",
                            "gamePrizes":           ""
                        }
                    }

                Status = status.HTTP_200_OK

            except:

                data = {
                        "code": 1003,
                        'msg': 'User_Not_Exist'
                    }

        #  campaignpayout
        elif cash and campaignref and last and prepaidref and prepaidticketid and singleWin:

            GameRequestsModel.objects.create(
                organization    = org,
                MemberID        = playerid,
                cash            = cash,
                bonus           = bonus,
                currency        = currency,
                reference       = reference,
                description     = description,
                cat             = cat,
                tag             = tag,
                campaignref     = campaignref,
                last            = last,
                lang            = lang,
                version         = version,
                prepaidref      = prepaidref,
                prepaidticketid = prepaidticketid,
                singleWin       = singleWin,
                totalWin        = totalWin,
                roundCount      = roundCount,
                ruleType        = ruleType
            )

            try:

                user = CustomUser.objects.filter(username = playerid)
                balance = user[0].main_wallet

                current_balance = balance + decimal.Decimal(totalWin)
                user.update(main_wallet=current_balance)

                data = {
                        "code": 0,
                        "data":{
                            "organization":         org,
                            "playerId":             playerid,
                            "currency":             currency,
                            "applicableBonus":      "",
                            "homeCurrency":         "",
                            "balance":              current_balance,
                            "nickName":             user[0].username
                        }
                    }

                Status = status.HTTP_200_OK

            except:

                data = {
                        "code": 1003,
                        'msg': 'User_Not_Exist'
                    }
        # getbalance

        elif org and sessiontoken and playerid and gameid and description and not amount and not version and not lang and not totalWin:
         
            GameRequestsModel.objects.create(
                organization    = org,
                MemberID        = playerid,
                sessionToken    = sessiontoken,
                gameId          = gameid,
                description     = description
            )

            try:

                user = CustomUser.objects.filter(username = playerid)
                balance = user[0].main_wallet
    
                data = {
                        "code": 0,
                        "data":{
                            "organization":         org,
                            "playerId":             playerid,
                            "currency":             currency,
                            "applicableBonus":      "",
                            "homeCurrency":         "",
                            "balance":              balance,
                            "nickName":             user[0].username,
                            "bonus":                ""
                        }
                    }

                Status = status.HTTP_200_OK
                
            except:

                data = {
                        "code": 1003,
                        'msg': 'User_Not_Exist'
                    }


        return Response(data)
