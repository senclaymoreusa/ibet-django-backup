from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser
import simplejson as json
import xmltodict
import decimal
import requests
import json
import uuid
from  games.models import *
from django.core.exceptions import  ObjectDoesNotExist
from time import gmtime, strftime, strptime
from django.utils import timezone
from datetime import datetime
from django.db import transaction
import random, logging
from rest_framework.decorators import api_view, permission_classes
import xml.etree.ElementTree as ET

logger = logging.getLogger('django')

class WalletGeneralAPI(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):

        data = json.loads(request.body)

        success = 0
        TransType = None
        TransData = None
        TransDataExists = 0
        error_code = -5
        error = 'Missing_Input_Parameter'
        TransType      = data['ThirdParty']['TransType']
        ThirdPartyCode = data['ThirdParty']['ThirdPartyCode']
        MemberID       = data['ThirdParty']['MemberID']
        try:
            user       =  CustomUser.objects.get(username = MemberID)   
            TransData  =  user.main_wallet
            error      =  'No_Error'
            error_code =  0
            success    =  1
            TransDataExists = 1
        
        except ObjectDoesNotExist:
            error      = 'Member_Not_Found'
            error_code = -2
            logger.error("GB::Member_Not_Found for WalletGeneralAPI")

        return Response({
            "ThirdParty": {
                "Success"  :        success,
                "TransType":        TransType,
                "TransData":        TransData,
                "TransDataExists":  TransDataExists,
                "ErrorCode":        error_code,
                "ErrorDesc":        error  
            }
        })


class WalletBetAPIURL(APIView):
    
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):

        data = json.loads(request.body)
        
        success = 0
        TransType = None
        TransData = None
        TransDataExists = 0
        error_code = -5
        error = 'Missing_Input_Parameter'
        game_type = None
        try:
            PROVIDER = GameProvider.objects.get(provider_name=GB_PROVIDER)
        except ObjectDoesNotExist:
            PROVIDER = GameProvider.objects.create(provider_name=GB_PROVIDER,
                                        type=GAME_TYPE_SPORTS,
                                        market='letouCN, letouTH, letouVN')
            logger.error("GB::PROVIDER AND/OR CATEGORY RELATIONS DO NOT EXIST FOR WalletBetAPIURL.")
        game_list = ["KenoList", "LottoList", "SscList", "PkxList", "KsList", "SportList"]
        if any(game in data['GB']['Result']['ReturnSet']['BettingList'] for game in game_list):
            game_type = 'dict'
        else:
            game_type = 'list'
        
        if game_type == 'dict':
            try:
                Method        = data['GB']['Result']['Method']
                Success       = data['GB']['Result']['Success']

                TransType     = data['GB']['Result']['ReturnSet']['TransType']
                BetTotalCnt   = data['GB']['Result']['ReturnSet']['BetTotalCnt']
                BetTotalAmt   = data['GB']['Result']['ReturnSet']['BetTotalAmt']

                BetID         = data['GB']['Result']['ReturnSet']['BettingList']['BetID']
                BetGrpNO      = data['GB']['Result']['ReturnSet']['BettingList']['BetGrpNO']
                TPCode        = data['GB']['Result']['ReturnSet']['BettingList']['TPCode']
                GBSN          = data['GB']['Result']['ReturnSet']['BettingList']['GBSN']
                MemberID      = data['GB']['Result']['ReturnSet']['BettingList']['MemberID']
                
                CurCode       = data['GB']['Result']['ReturnSet']['BettingList']['CurCode']
                BetDT         = data['GB']['Result']['ReturnSet']['BettingList']['BetDT']
                BetType       = data['GB']['Result']['ReturnSet']['BettingList']['BetType']
                BetTypeParam1 = data['GB']['Result']['ReturnSet']['BettingList']['BetTypeParam1']
                BetTypeParam2 = data['GB']['Result']['ReturnSet']['BettingList']['BetTypeParam2']
                Wintype       = data['GB']['Result']['ReturnSet']['BettingList']['Wintype']
                HxMGUID       = data['GB']['Result']['ReturnSet']['BettingList']['HxMGUID']
                InitBetAmt    = data['GB']['Result']['ReturnSet']['BettingList']['InitBetAmt']
                RealBetAmt    = data['GB']['Result']['ReturnSet']['BettingList']['RealBetAmt']
                HoldingAmt    = data['GB']['Result']['ReturnSet']['BettingList']['HoldingAmt']
                InitBetRate   = data['GB']['Result']['ReturnSet']['BettingList']['InitBetRate']
                RealBetRate   = data['GB']['Result']['ReturnSet']['BettingList']['RealBetRate']
                PreWinAmt     = data['GB']['Result']['ReturnSet']['BettingList']['PreWinAmt']

                try:
                    user = CustomUser.objects.get(username = MemberID)
                    trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
                    temp = user[0].main_wallet
                    if temp >= decimal.Decimal(BetTotalAmt)/100:
                        with transaction.atomic():
                            current_balance = temp-decimal.Decimal(BetTotalAmt)/100
                            user.update(main_wallet=current_balance)
                            error      =  'No_Error'
                            error_code =  0
                            success    =  1
                            TransData  = current_balance
                            

                            if data['GB']['Result']['ReturnSet']['BettingList']['SportList'] != '':
                                category = 'Sports'

                                try:
                                    cate = Category.objects.get(name=category)
                                except:
                                    logger.error("GB::missing category for WalletBetAPIURL")

                                sport_size = len(data['GB']['Result']['ReturnSet']['BettingList']['SportList'])
                                for x in range(sport_size):
                                    teams = data['GB']['Result']['ReturnSet']['BettingList']['SportList'][x]['Team']
                                    teams_size = len(teams)
                                    
                                    teamcode1 = teams[0]['TeamCode']
                                    teamcode2 = teams[1]['TeamCode']

                                    GameBet.objects.create(
                                        provider=PROVIDER,
                                        transaction_id=trans_id,
                                        category=cate,
                                        game_name=str(teamcode1) + '/' + str(teamcode2),
                                        user=user,
                                        user_name=user.username,
                                        currency=user.currency,
                                        market=ibetCN,
                                        ref_no=BetID,
                                        amount_wagered=decimal.Decimal(RealBetAmt)/100,
                                        bet_type=TransType,
                                        other_data=data,
                                    )

                            else:
                                category = 'Lotteries'
                                try:
                                    cate = Category.objects.get(name=category)
                                except:
                                    logger.error("GB::missing category for WalletBetAPIURL")
                            
                                GameBet.objects.create(
                                    provider=PROVIDER,
                                    transaction_id=trans_id,
                                    category=cate,
                                    user=user,
                                    user_name=user.username,
                                    currency=user.currency,
                                    market=ibetCN,
                                    ref_no=BetID,
                                    amount_wagered=decimal.Decimal(RealBetAmt)/100,
                                    bet_type=TransType,
                                    other_data=data,
                                )

                    else:
                        error      =  'Insufficient_Balance'
                        error_code =  -4
                
                    

                except:
                    logger.error("GB::Member_Not_Found FOR WalletBetAPIURL.")
                    error = 'Member_Not_Found'
                    error_code = -2
                
            except:
                logger.critical("GB:: Unable to receive WalletBetAPIURL")
                pass


        elif game_type == 'list':
           
            try:
                Method        = data['GB']['Result']['Method']
                Success       = data['GB']['Result']['Success']

                TransType     = data['GB']['Result']['ReturnSet']['TransType']
                BetTotalCnt   = data['GB']['Result']['ReturnSet']['BetTotalCnt']
                BetTotalAmt   = data['GB']['Result']['ReturnSet']['BetTotalAmt']
                username = data['GB']['Result']['ReturnSet']['BettingList'][0]['MemberID']
                
                try: 
                    user = CustomUser.objects.get(username=username)
                    
                    temp = user.main_wallet
                    
                    total_amount = decimal.Decimal(BetTotalAmt) / 100
                    
                    if temp >= total_amount:
                        current_balance = temp-total_amount
                        
                        with transaction.atomic():
                            
                            for x in range(len(data['GB']['Result']['ReturnSet']['BettingList'])):
                                
                                trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
                                BetID         = data['GB']['Result']['ReturnSet']['BettingList'][x]['BetID']
                                BetGrpNO      = data['GB']['Result']['ReturnSet']['BettingList'][x]['BetGrpNO']
                                TPCode        = data['GB']['Result']['ReturnSet']['BettingList'][x]['TPCode']
                                GBSN          = data['GB']['Result']['ReturnSet']['BettingList'][x]['GBSN']
                                MemberID      = data['GB']['Result']['ReturnSet']['BettingList'][x]['MemberID']
                                CurCode       = data['GB']['Result']['ReturnSet']['BettingList'][x]['CurCode']
                                BetDT         = data['GB']['Result']['ReturnSet']['BettingList'][x]['BetDT']
                                BetType       = data['GB']['Result']['ReturnSet']['BettingList'][x]['BetType']
                                BetTypeParam1 = data['GB']['Result']['ReturnSet']['BettingList'][x]['BetTypeParam1']
                                BetTypeParam2 = data['GB']['Result']['ReturnSet']['BettingList'][x]['BetTypeParam2']
                                Wintype       = data['GB']['Result']['ReturnSet']['BettingList'][x]['Wintype']
                                HxMGUID       = data['GB']['Result']['ReturnSet']['BettingList'][x]['HxMGUID']
                                InitBetAmt    = data['GB']['Result']['ReturnSet']['BettingList'][x]['InitBetAmt']
                                RealBetAmt    = data['GB']['Result']['ReturnSet']['BettingList'][x]['RealBetAmt']
                                HoldingAmt    = data['GB']['Result']['ReturnSet']['BettingList'][x]['HoldingAmt']
                                InitBetRate   = data['GB']['Result']['ReturnSet']['BettingList'][x]['InitBetRate']
                                RealBetRate   = data['GB']['Result']['ReturnSet']['BettingList'][x]['RealBetRate']
                                PreWinAmt     = data['GB']['Result']['ReturnSet']['BettingList'][x]['PreWinAmt']
                                
                                if BetType == '1':
                                    bet_type = SINGLE
                                else:
                                    bet_type = OTHER
                            
                                if data['GB']['Result']['ReturnSet']['BettingList'][x]['SportList'] != []:
                                    
                                    SportList = data['GB']['Result']['ReturnSet']['BettingList'][x]['SportList'] 
                                    
                                    category = 'Sports'
                                    try:
                                        cate = Category.objects.get(name=category)
                                    except:
                                        logger.error("GB::wallet bet API is missing category.")
                                    for y in range(len(SportList)):
                                        teams = SportList[y]['Team']
                                        
                                        teamcode1 = teams[0]['TeamCode']
                                        teamcode2 = teams[1]['TeamCode']
                                        
                                        GameBet.objects.create(
                                            provider=PROVIDER,
                                            category=cate,
                                            transaction_id=trans_id,
                                            user=user,
                                            game_name=str(teamcode1) + '/' + str(teamcode2),
                                            user_name=user.username,
                                            currency=user.currency,
                                            market=ibetCN,
                                            ref_no=BetID,
                                            amount_wagered=decimal.Decimal(RealBetAmt/100),
                                            bet_type=bet_type,
                                            other_data=data,
                                        )
                                else:
                                    category = 'Lotteries'
                                    try:
                                        cate = Category.objects.get(name=category)
                                    except:
                                        logger.error("missing category.")
                                
                                    GameBet.objects.create(
                                        provider=PROVIDER,
                                        category=cate,
                                        transaction_id=trans_id,
                                        user=user,
                                        user_name=user.username,
                                        currency=user.currency,
                                        market=ibetCN,
                                        ref_no=BetID,
                                        amount_wagered=decimal.Decimal(RealBetAmt/100),
                                        bet_type=bet_type,
                                        other_data=data,
                                    )
                            user.main_wallet=current_balance
                            user.save()    
                            error      =  'No_Error'
                            error_code =  0
                            success    =  1    
                            TransData  = user.main_wallet
                            
                    else:
                        error      =  'Insufficient_Balance'
                        error_code =  -4
            
                except ObjectDoesNotExist:
                    logger.error("GB:: Member_Not_Found for WalletSettleAPIURL")
                    error = 'Member_Not_Found'
                    error_code = -2
                
            except:
                logger.critical("GB:: Unable to receive WalletBetAPIURL")
                pass

        return Response({
            "ThirdParty": {
                "Success"  :       success,
                "TransType":       TransType,
                "TransData":       TransData,
                "TransDataExists": TransDataExists, 
                "ErrorCode":       error_code,
                "ErrorDesc":       error 
            }
        })

class WalletSettleAPIURL(APIView):

    permission_classes = (AllowAny, )
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        data = json.loads(request.body)
    
        success = 0
        TransType = None
        TransData = None
        TransDataExists = 0
        error_code = -5
        error = 'Missing_Input_Parameter'
        game_type = None

        game_list = ["KenoList", "LottoList", "SscList", "PkxList", "KsList", "SportList"]
        try:
            PROVIDER = GameProvider.objects.get(provider_name=GB_PROVIDER)
        except ObjectDoesNotExist:
            PROVIDER = GameProvider.objects.create(provider_name=GB_PROVIDER,
                                        type=GAME_TYPE_SPORTS,
                                        market='letouCN, letouTH, letouVN')
            logger.error("PROVIDER AND/OR CATEGORY RELATIONS DO NOT EXIST.")
        if any(game in data['GB']['Result']['ReturnSet']['SettleList'] for game in game_list):
            game_type = 'dict'
        else:
            game_type = 'list'
        
        if game_type == 'dict':
            try:
                Method        = data['GB']['Result']['Method']
                success       = data['GB']['Result']['Success']

                TransType     = data['GB']['Result']['ReturnSet']['TransType']
                BetTotalCnt   = data['GB']['Result']['ReturnSet']['BetTotalCnt']
                BetTotalAmt   = data['GB']['Result']['ReturnSet']['BetTotalAmt']
                SettleID      = data['GB']['Result']['ReturnSet']['SettleList']['SettleID']
                BetID         = data['GB']['Result']['ReturnSet']['SettleList']['BetID']
                BetGrpNO      = data['GB']['Result']['ReturnSet']['SettleList']['BetGrpNO']
                TPCode        = data['GB']['Result']['ReturnSet']['SettleList']['TPCode']
                GBSN          = data['GB']['Result']['ReturnSet']['SettleList']['GBSN']
                MemberID      = data['GB']['Result']['ReturnSet']['SettleList']['MemberID']
                CurCode       = data['GB']['Result']['ReturnSet']['SettleList']['CurCode']
                BetDT         = data['GB']['Result']['ReturnSet']['SettleList']['BetDT']
                BetType       = data['GB']['Result']['ReturnSet']['SettleList']['BetType']
                BetTypeParam1 = data['GB']['Result']['ReturnSet']['SettleList']['BetTypeParam1']
                BetTypeParam2 = data['GB']['Result']['ReturnSet']['SettleList']['BetTypeParam2']
                Wintype       = data['GB']['Result']['ReturnSet']['SettleList']['Wintype']
                HxMGUID       = data['GB']['Result']['ReturnSet']['SettleList']['HxMGUID']
                InitBetAmt    = data['GB']['Result']['ReturnSet']['SettleList']['InitBetAmt']
                RealBetAmt    = data['GB']['Result']['ReturnSet']['SettleList']['RealBetAmt']
                HoldingAmt    = data['GB']['Result']['ReturnSet']['SettleList']['HoldingAmt']
                InitBetRate   = data['GB']['Result']['ReturnSet']['SettleList']['InitBetRate']
                RealBetRate   = data['GB']['Result']['ReturnSet']['SettleList']['RealBetRate']
                PreWinAmt     = data['GB']['Result']['ReturnSet']['SettleList']['PreWinAmt']
                BetResult     = data['GB']['Result']['ReturnSet']['SettleList']['BetResult']
                WLAmt         = data['GB']['Result']['ReturnSet']['SettleList']['WLAmt']
                try:
                    RefundBetAmt  = data['GB']['Result']['ReturnSet']['SettleList']['RefundBetAmt'] 
                except:
                    RefundBetAmt  = data['GB']['Result']['ReturnSet']['SettleList']['RefundAmt']
                TicketBetAmt  = data['GB']['Result']['ReturnSet']['SettleList']['TicketBetAmt']
                TicketResult  = data['GB']['Result']['ReturnSet']['SettleList']['TicketResult']
                TicketWLAmt   = data['GB']['Result']['ReturnSet']['SettleList']['TicketWLAmt']
                SettleDT      = data['GB']['Result']['ReturnSet']['SettleList']['SettleDT']
                try: 
                    user = CustomUser.objects.get(username = MemberID)
                    trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
                    if BetType == '1':
                        bet_type = SINGLE
                    else:
                        bet_type = OTHER
                        
                    if TicketResult == '0':
                        TicketResult = 1 #lose
                    elif TicketResult == '1':
                        TicketResult = 0 #win
                    elif TicketResult == '2':
                        TicketResult = 2 #tie
                    elif TicketResult == '4':
                        TicketResult = 3 #cancel
                    elif TicketResult == '5':
                        TicketResult = 3 #兑现
                    elif TicketResult == 'R':
                        TicketResult = 3 #rollback 體育專屬,表示先前說的都不算,回沖輸贏,等待下次結算
                    
                    if data['GB']['Result']['ReturnSet']['SettleList']['SportList'] != []:
                        category = 'Sports'
                        try:
                            cate = Category.objects.get(name=category)
                        except:
                            logger.error("missing category.")
                        SportList = data['GB']['Result']['ReturnSet']['SettleList']['SportList']
                        SportList_size = len(SportList)
                        for x in range(SportList_size):
                            team = SportList[x]['Team']
                            teamcode1 = team[0]['TeamCode']
                            teamcode2 = team[1]['TeamCode']

                            GameBet.objects.create(
                                provider=PROVIDER,
                                category=cate,
                                transaction_id=trans_id,
                                user=user,
                                user_name=user.username,
                                game_name=str(teamcode1) + '/' + str(teamcode2),
                                currency=user.currency,
                                market=ibetCN,
                                ref_no=BetID,
                                amount_wagered=decimal.Decimal(RealBetAmt/100),
                                bet_type=bet_type,
                                amount_won=decimal.Decimal(WLAmt/100), 
                                outcome=TicketResult,
                                resolved_time=timezone.now(),
                                other_data=data,
                            )
                        
                            user.main_wallet += decimal.Decimal(WLAmt/100)
                            user.save()


                    else:
                        category = 'Lotteries'
                            
                        try:
                            cate = Category.objects.get(name=category)
                        except:
                            logger.error("missing category.")
                        
                        GameBet.objects.create(
                            provider=PROVIDER,
                            category=cate,
                            transaction_id=trans_id,
                            user=user,
                            user_name=user.username,
                            currency=user.currency,
                            market=ibetCN,
                            ref_no=BetID,
                            amount_wagered=decimal.Decimal(RealBetAmt/100),
                            bet_type=bet_type,
                            amount_won=decimal.Decimal(WLAmt/100), 
                            outcome=TicketResult,
                            resolved_time=timezone.now(),
                            other_data=data,
                        )
                        
                        user.main_wallet += decimal.Decimal(WLAmt/100)
                        user.save()
                    error      =  'No_Error'
                    error_code =  0
                    success    =  1
                    TransData  = user.main_wallet

                except: 
                    logger.error("GB:: Member_Not_Found for WalletSettleAPIURL")
                    error = 'Member_Not_Found'
                    error_code = -2

            except:
                logger.critical("GB:: Unable to receive WalletSettleAPIURL")
                pass

        elif game_type == 'list':
            try:
                Method        = data['GB']['Result']['Method']
                Success       = data['GB']['Result']['Success']

                TransType     = data['GB']['Result']['ReturnSet']['TransType']
                BetTotalCnt   = data['GB']['Result']['ReturnSet']['BetTotalCnt']
                BetTotalAmt   = data['GB']['Result']['ReturnSet']['BetTotalAmt']
                username      = data['GB']['Result']['ReturnSet']['SettleList'][0]['MemberID']
                
                try:
                    user = CustomUser.objects.get(username=username)
                    
                    for x in range(len(data['GB']['Result']['ReturnSet']['SettleList'])):
                        trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
                        SettleID      = data['GB']['Result']['ReturnSet']['SettleList'][x]['SettleID']
                        BetID         = data['GB']['Result']['ReturnSet']['SettleList'][x]['BetID']
                        BetGrpNO      = data['GB']['Result']['ReturnSet']['SettleList'][x]['BetGrpNO']
                        TPCode        = data['GB']['Result']['ReturnSet']['SettleList'][x]['TPCode']
                        GBSN          = data['GB']['Result']['ReturnSet']['SettleList'][x]['GBSN']
                        CurCode       = data['GB']['Result']['ReturnSet']['SettleList'][x]['CurCode']
                        BetDT         = data['GB']['Result']['ReturnSet']['SettleList'][x]['BetDT']
                        BetType       = data['GB']['Result']['ReturnSet']['SettleList'][x]['BetType']
                        BetTypeParam1 = data['GB']['Result']['ReturnSet']['SettleList'][x]['BetTypeParam1']
                        BetTypeParam2 = data['GB']['Result']['ReturnSet']['SettleList'][x]['BetTypeParam2']
                        Wintype       = data['GB']['Result']['ReturnSet']['SettleList'][x]['Wintype']
                        HxMGUID       = data['GB']['Result']['ReturnSet']['SettleList'][x]['HxMGUID']
                        InitBetAmt    = data['GB']['Result']['ReturnSet']['SettleList'][x]['InitBetAmt']
                        RealBetAmt    = data['GB']['Result']['ReturnSet']['SettleList'][x]['RealBetAmt']
                        HoldingAmt    = data['GB']['Result']['ReturnSet']['SettleList'][x]['HoldingAmt']
                        InitBetRate   = data['GB']['Result']['ReturnSet']['SettleList'][x]['InitBetRate']
                        RealBetRate   = data['GB']['Result']['ReturnSet']['SettleList'][x]['RealBetRate']
                        PreWinAmt     = data['GB']['Result']['ReturnSet']['SettleList'][x]['PreWinAmt']
                        BetResult     = data['GB']['Result']['ReturnSet']['SettleList'][x]['BetResult']
                        WLAmt         = data['GB']['Result']['ReturnSet']['SettleList'][x]['WLAmt']
                
                        RefundBetAmt  = data['GB']['Result']['ReturnSet']['SettleList'][x]['RefundAmt'] 
                
                        TicketBetAmt  = data['GB']['Result']['ReturnSet']['SettleList'][x]['TicketBetAmt']
                        TicketResult  = data['GB']['Result']['ReturnSet']['SettleList'][x]['TicketResult']
                        TicketWLAmt   = data['GB']['Result']['ReturnSet']['SettleList'][x]['TicketWLAmt']
                        SettleDT      = data['GB']['Result']['ReturnSet']['SettleList'][x]['SettleDT']
                        
                        
                        if BetType == '1':
                            bet_type = SINGLE
                        else:
                            bet_type = OTHER
                        
                        if TicketResult == '0':
                            TicketResult = 1 #lose
                        elif TicketResult == '1':
                            TicketResult = 0 #win
                        elif TicketResult == '2':
                            TicketResult = 2 #tie
                        elif TicketResult == '4':
                            TicketResult = 3 #cancel
                        elif TicketResult == '5':
                            TicketResult = 3 #兑现
                        elif TicketResult == 'R':
                            TicketResult = 3 #rollback 體育專屬,表示先前說的都不算,回沖輸贏,等待下次結算

                        if data['GB']['Result']['ReturnSet']['SettleList'][x]['SportList'] != []:
                            category = 'Sports'
                            try:
                                cate = Category.objects.get(name=category)
                            except:
                                logger.error("missing category.")
                            SportList = data['GB']['Result']['ReturnSet']['SettleList'][x]['SportList']
                            SportList_size = len(SportList)
                            for y in range(SportList_size):
                                Team = SportList[y][Team]
                                teamcode1 = Team[0]['TeamCode']
                                teamcode2 = Team[1]['TeamCode']

                                GameBet.objects.create(
                                    provider=PROVIDER,
                                    category=cate,
                                    user=user,
                                    user_name=user.username,
                                    game_name=str(teamcode1) + '/' + str(teamcode2),
                                    transaction_id=trans_id,
                                    currency=user.currency,
                                    market=ibetCN,
                                    ref_no=BetID,
                                    amount_wagered=decimal.Decimal(RealBetAmt/100),
                                    bet_type=bet_type,
                                    amount_won=decimal.Decimal(RefundBetAmt/100),
                                    outcome=TicketResult,
                                    resolved_time=timezone.now(),
                                    other_data=data,
                                )
                                

                        else:
                            category = 'Lotteries'
                            
                            try:
                                cate = Category.objects.get(name=category)
                            except:
                                logger.error("missing category.")
                        
                            GameBet.objects.create(
                                provider=PROVIDER,
                                category=cate,
                                user=user,
                                user_name=user.username,
                                transaction_id=trans_id,
                                currency=user.currency,
                                market=ibetCN,
                                ref_no=BetID,
                                amount_wagered=decimal.Decimal(RealBetAmt/100),
                                bet_type=bet_type,
                                amount_won=decimal.Decimal(RefundBetAmt/100),
                                outcome=TicketResult,
                                resolved_time=timezone.now(),
                                other_data=data,
                            )
                            
                        if RefundBetAmt != '0' :
                            user.main_wallet += decimal.Decimal(RefundBetAmt/100)
                            user.save()

                    error      =  'No_Error'
                    error_code =  0
                    success    =  1
                    TransData  = user.main_wallet

                    
                except ObjectDoesNotExist: 
                    logger.error("GB:: Member_Not_Found for WalletSettleAPIURL")
                    error = 'Member_Not_Found'
                    error_code = -2

            except:
                logger.critical("GB:: Unable to receive WalletSettleAPIURL")
                pass


        return Response({
            "ThirdParty": {
                "Success"  :       success,
                "TransType":       TransType,
                "TransData":       TransData,
                "TransDataExists": TransDataExists, 
                "ErrorCode":       error_code,
                "ErrorDesc":       error 
            }
        })

langConversion = {
    'English': 'en-us',
    'Chinese': 'zh-cn',
    'Thai': 'th-th',
    'Vietnamese':'vi-vn',
    'en': 'en-us',
    'zh': 'zh-cn',
    'th': 'th-th',
    'vi': 'vi-vn',
}
class GenerateGameURL(APIView):

    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        
        game = self.request.GET['game']
        language = langConversion[self.request.user.language]
        

        TPUniqueID = uuid.uuid4()
        try:
            data = requests.post(GB_URL, json = {
                
            "GB": {
                "Method": "UpdateTPUniqueID",
                "TPCode": "011",
                "AuthKey": GB_GENERALKEY,
                "Params": {
                    "MemberID": self.request.user.username,
                    "TPUniqueID": str(TPUniqueID) 
                    }
                }
            })

            dic = data.json()
        except Exception as e:
            logger.critical("GB:: Unable to request GenerateGameURL api")
            return Response({'error': 'GB:: Unable to request GenerateGameURL api'})
        
        if 'Error' in dic['GB']['Result']['ReturnSet']:

            #temp = '-'.join([self.request.user.date_of_birth.split('/')[2], self.request.user.date_of_birth.split('/')[0], self.request.user.date_of_birth.split('/')[1]])
            if self.request.user.date_of_birth:

                dob_fields = self.request.user.date_of_birth.split('/') 

                temp = '-'.join([
                    dob_fields[2],
                    dob_fields[0],
                    dob_fields[1]
                ])
            else:
                temp = '1990-01-01'

            if self.request.user.country:
                country = self.request.user.country
                if country == 'china':
                    CyCode = 'CN'    
                elif country == 'vietnam':
                    CyCode = 'VN'
                elif country == 'thailand':
                    CyCode = 'TH'  
                else:
                    CyCode = 'CN'
            else:
                CyCode = 'CN'

            if self.request.user.currency:
                 currency = self.request.user.currency
                 if currency == 0:
                     CurCode = "CNY"
                 elif currency == 1:
                     CurCode = "USD"
                 elif currency == 2:
                     CurCode = "THB"
                 elif currency == 7:
                     CurCode = "VND"
                 else:
                     CurCode = "CNY"
            else:
                CurCode = "CNY"



            create_user_data = requests.post(GB_URL, json = {
            
            "GB": {
                "Method": "CreateMember",
                "TPCode": "011",
                "AuthKey": GB_GENERALKEY,
                "Params": {
                    "MemberID": self.request.user.username,
                    "FirstName": self.request.user.first_name,
                    "LastName": self.request.user.last_name,
                    "Nickname": self.request.user.username,
                    "Gender": "2",
                    "Birthdate": temp,
                    "CyCode": CyCode,
                    "CurCode": CurCode,
                    "LangCode": language,
                    "TPUniqueID": "new"
                    }
                }
            })

            create_user_data = create_user_data.json()

            GBSN = create_user_data['GB']['Result']['ReturnSet']['GBSN']

        else:
            GBSN = dic['GB']['Result']['ReturnSet']['GBSN']
        try:
            res = requests.get(GB_API_URL + '?gbsn={}&TPUniqueID={}'.format(GBSN, TPUniqueID))
            res = res.content.decode('utf-8')
            
            res = res[2:-2]
        except:
            logger.error("GB:: Unable to get token.")
            return Response({"error":"GB:: Unable to get token."})
        
        dic = {'SSC': 'ssc', 'K3': 'k3', 'PK10': 'pk10', 'Keno': 'keno', 'Lotto': 'lotto' }
        
        if game == 'GB Sports':
            url = GB_SPORT_URL + '?tpid=011&token={}&languagecode={}&oddstype=00001'.format(res,language)
            mobile = GB_MOBILE_SPORT_URL + '?tpid=011&token={}&languagecode={}&oddstype=00001'.format(res,language)
        elif game == 'GB ESports':
            url = GB_SPORT_URL + '?tpid=011&token={}&languagecode={}&oddstype=00001&sc=00111'.format(res,language)
            mobile = GB_MOBILE_SPORT_URL + '?tpid=011&token={}&languagecode={}&oddstype=00001&sc=00111'.format(res,language)
        else:
            url = GB_OTHER_URL + '/{}/default.aspx?tpid=011&token={}&languagecode={}'.format(dic[game], res, language)
            mobile = GB_MOBILE_OTHER_URL + '/{}/index.aspx?tpid=011&token={}&languagecode={}'.format(dic[game], res, language)
        
        return Response({'game_url': url, 'mobile_url':mobile})

class GenerateFakeUserGameURL(APIView):

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):

        game = self.request.GET['game']
        language = self.request.GET['language']
        TPUniqueID = uuid.uuid4()
        try: 
            data = requests.post(GB_URL, json = {
          
            "GB": {
                "Method": "UpdateTPUniqueID",
                "TPCode": "011",
                "AuthKey": GB_GENERALKEY,
                "Params": {
                    "MemberID": 'Fakeuser',
                    "TPUniqueID": str(TPUniqueID) 
                    }
                }
            })

            dic = data.json()
        except Exception as e:
            logger.critical("GB:: Unable to request GenerateFakeUserGameURL api")
            return Response({'error': 'GB:: Unable to request GenerateFakeUserGameURL api'})

        if 'Error' in dic['GB']['Result']['ReturnSet']:
             
            create_user_data = requests.post(GB_URL, json = {
            
            "GB": {
                "Method": "CreateMember",
                "TPCode": "011",
                "AuthKey": GB_GENERALKEY,
                "Params": {
                    "MemberID": 'Fakeuser',
                    "FirstName": 'Fake',
                    "LastName": 'User',
                    "Nickname": 'Fake User',
                    "Gender": "2",
                    "Birthdate": '10-10-1996',
                    "CyCode": "CN",
                    "CurCode": "CNY",
                    "LangCode": "zh-cn",
                    "TPUniqueID": "new"
                    }
                }
            })

            create_user_data = create_user_data.json()

            GBSN = create_user_data['GB']['Result']['ReturnSet']['GBSN']

        else:
            GBSN = dic['GB']['Result']['ReturnSet']['GBSN']
       
        try:
            res = requests.get(GB_API_URL + '?gbsn={}&TPUniqueID={}'.format(GBSN, TPUniqueID))
            res = res.content.decode('utf-8')
        
            res = res[2:-2]
        except:
            logger.error("GB:: Unable to get token.")
            return Response({"error":"GB:: Unable to get token."})
        
        dic = {'SSC': 'ssc', 'K3': 'k3', 'PK10': 'pk10', 'Keno': 'keno', 'Lotto': 'lotto'}

        if game == 'GB Sports':
            url = GB_SPORT_URL + '?tpid=011&token={}&languagecode={}&oddstype=00001'.format(res, language)
            mobile = GB_MOBILE_SPORT_URL + '?tpid=011&token={}&languagecode={}&oddstype=00001'.format(res, language)
        elif game == 'GB ESports':
            url = GB_SPORT_URL + '?tpid=011&token={}&languagecode={}&oddstype=00001&sc=00111'.format(res, language)
            mobile = GB_MOBILE_SPORT_URL + '?tpid=011&token={}&languagecode={}&oddstype=00001&sc=00111'.format(res, language)
        else:
            url = GB_OTHER_URL + '/{}/default.aspx?tpid=011&token={}&languagecode={}'.format(dic[game], res, language)
            mobile = GB_MOBILE_OTHER_URL + '/{}/index.aspx?tpid=011&token={}&languagecode={}'.format(dic[game], res, language)
            
        return Response({'game_url': url, 'mobile_url':mobile})

@api_view(['POST'])
@permission_classes((AllowAny,)) 
def getSportTeamInfo(request):
    teamcode = request.POST.get("teamcode")
    language = request.POST.get("language")
    if language == 'en': 
        language = 'en-us'
    elif language == 'zh': 
        language = 'zh-cn'
    elif language == 'th':
        language = 'th-th'
    elif language == 'vi':
        language = 'vi-vn'
    else:
        language = 'zh-cn'

    headers =  {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        r = requests.post(GB_CLIENT_API_URL + "GetSportTeamInfo", headers=headers, data={
            "intSportCompetitorCode": teamcode,
            "strLanguageCode": language   
        })
                        
        rdata = r.text
    except requests.RequestException:
        logger.error("Connectivity error for GB getSportTeamInfo API.")
        return Response({'error': 'Connectivity error for GB getSportTeamInfo API.'})
    except ValueError:
        logger.error("JSON parsing error for GB getSportTeamInfo API.")
        return Response({'error': 'JSON parsing error for GB getSportTeamInfo API.'})
    except (IndexError, KeyError):
        logger.error("JSON format error for GB getSportTeamInfo API.")
        return Response({'error': 'JSON format error for GB getSportTeamInfo API.'})
        
    if r.status_code == 200:
        dic = xmltodict.parse(rdata)
        TeamName = dic['DataTable']['diffgr:diffgram']['NewDataSet']['Table']['TeamName']

        return Response(TeamName)
    else:
        logger.warning('GB::There was something wrong with the GB getSportTeamInfo connection')
        return Response({'error':'There was something wrong with the GB getSportTeamInfo connection'}, status=status.HTTP_400_BAD_REQUEST)





