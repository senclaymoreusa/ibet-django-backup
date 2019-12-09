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
import random
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
            logger.error("Member_Not_Found")

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
            logger.error("PROVIDER AND/OR CATEGORY RELATIONS DO NOT EXIST.")
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
                            else:
                                category = 'Lotteries'
                            try:
                                cate = Category.objects.get(name=category)
                            except:
                                cate = Category.objects.create(name=category)
                                logger.info("Create new category.")

                            GameBet.objects.create(
                                provider=PROVIDER,
                                transaction_id=trans_id,
                                category=cate,
                                username=user,
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
                    error = 'Member_Not_Found'
                    error_code = -2
                
            except:
                
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
                                
                            
                                if data['GB']['Result']['ReturnSet']['BettingList'][x]['SportList'] != []:
                                    category = 'Sports'
                                else:
                                    category = 'Lotteries'
                                
                                try:
                                    cate = Category.objects.get(name=category)
                                except:
                                    cate = Category.objects.create(name=category)
                                    logger.info("Create new category.")
                                if BetType == '1':
                                    bet_type = SINGLE
                                else:
                                    bet_type = OTHER
                                
                                GameBet.objects.create(
                                    provider=PROVIDER,
                                    category=cate,
                                    transaction_id=trans_id,
                                    username=user,
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
                    error = 'Member_Not_Found'
                    error_code = -2
                
            except:
                
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
                    if data['GB']['Result']['ReturnSet']['SettleList']['SportList'] != []:
                        category = 'Sports'
                    else:
                        category = 'Lotteries'
                            
                    try:
                        cate = Category.objects.get(name=category)
                    except:
                        cate = Category.objects.create(name=category)
                        logger.info("Create new category.")
                        
                    if BetType == '1':
                        bet_type = SINGLE
                    else:
                        bet_type = OTHER
                        
                    if BetResult == '0':
                        BetResult = 1 #lose
                    elif BetResult == '1':
                        BetResult = 0 #win
                    elif BetResult == '2':
                        BetResult = 2 #tie
                    elif BetResult == '4':
                        BetResult = 8 #cancel
                    elif BetResult == '5':
                        BetResult = 9 #兑现
                    elif BetResult == 'R':
                        BetResult = 7 #rollback 體育專屬,表示先前說的都不算,回沖輸贏,等待下次結算
                    with transaction.atomic():    
                        GameBet.objects.create(
                            provider=PROVIDER,
                            category=cate,
                            transaction_id=trans_id,
                            username=user,
                            currency=user.currency,
                            market=ibetCN,
                            ref_no=BetID,
                            amount_wagered=decimal.Decimal(RealBetAmt/100),
                            bet_type=bet_type,
                            amount_won=decimal.Decimal(RefundBetAmt/100),
                            outcome=BetResult,
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

                except: 
                    error = 'Member_Not_Found'
                    error_code = -2

            except:
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
                        
                        
                            
                        if data['GB']['Result']['ReturnSet']['SettleList'][x]['SportList'] != []:
                            category = 'Sports'
                        else:
                            category = 'Lotteries'
                            
                        try:
                            cate = Category.objects.get(name=category)
                        except:
                            cate = Category.objects.create(name=category)
                            logger.info("Create new category.")
                        
                        if BetType == '1':
                            bet_type = SINGLE
                        else:
                            bet_type = OTHER
                        
                        if BetResult == '0':
                            BetResult = 1 #lose
                        elif BetResult == '1':
                            BetResult = 0 #win
                        elif BetResult == '2':
                            BetResult = 2 #tie
                        elif BetResult == '4':
                            BetResult = 8 #cancel
                        elif BetResult == '5':
                            BetResult = 9 #兑现
                        elif BetResult == 'R':
                            BetResult = 7 #rollback 體育專屬,表示先前說的都不算,回沖輸贏,等待下次結算
                        with transaction.atomic():
                            GameBet.objects.create(
                                provider=PROVIDER,
                                category=cate,
                                username=user,
                                transaction_id=trans_id,
                                currency=user.currency,
                                market=ibetCN,
                                ref_no=BetID,
                                amount_wagered=decimal.Decimal(RealBetAmt/100),
                                bet_type=bet_type,
                                amount_won=decimal.Decimal(RefundBetAmt/100),
                                outcome=BetResult,
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
                    error = 'Member_Not_Found'
                    error_code = -2

            except:
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
}
class GenerateGameURL(APIView):

    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):

        game = self.request.GET['game']
        language = langConversion[self.request.user.language]
        

        TPUniqueID = uuid.uuid4()

        data = requests.post(GB_URL, json = {
            
        "GB": {
            "Method": "UpdateTPUniqueID",
            "TPCode": "011",
            "AuthKey": "kvZES8",
            "Params": {
                "MemberID": self.request.user.username,
                "TPUniqueID": str(TPUniqueID) 
                }
            }
        })

        dic = data.json()

        
        if 'Error' in dic['GB']['Result']['ReturnSet']:

            #temp = '-'.join([self.request.user.date_of_birth.split('/')[2], self.request.user.date_of_birth.split('/')[0], self.request.user.date_of_birth.split('/')[1]])
            
            dob_fields = self.request.user.date_of_birth.split('/') 

            temp = '-'.join([
                dob_fields[2],
                dob_fields[0],
                dob_fields[1]
            ])
            
            create_user_data = requests.post(GB_URL, json = {
            
            "GB": {
                "Method": "CreateMember",
                "TPCode": "011",
                "AuthKey": "kvZES8",
                "Params": {
                    "MemberID": self.request.user.username,
                    "FirstName": self.request.user.first_name,
                    "LastName": self.request.user.last_name,
                    "Nickname": self.request.user.username,
                    "Gender": "2",
                    "Birthdate": temp,
                    "CyCode": "CN",
                    "CurCode": "CNY",
                    "LangCode": language,
                    "TPUniqueID": "new"
                    }
                }
            })

            create_user_data = create_user_data.json()

            GBSN = create_user_data['GB']['Result']['ReturnSet']['"GBSN"']

        else:
            GBSN = dic['GB']['Result']['ReturnSet']['GBSN']

        res = requests.get(GB_API_URL + '?gbsn={}&TPUniqueID={}'.format(GBSN, TPUniqueID))
        res = res.content.decode('utf-8')
        res = res[2:-2]

        dic = {'SSC': 'ssc', 'K3': 'k3', 'PK10': 'pk10', 'Keno': 'keno', 'Lotto': 'lotto' }
        
        if game == 'GB Sports':
            url = GB_SPORT_URL + '?tpid=011&token={}&languagecode={}&oddstype=00001'.format(res,language)
        elif game == 'GB ESports':
            url = GB_SPORT_URL + '?tpid=011&token={}&languagecode={}&oddstype=00001&sc=00111'.format(res,language)
        else:
            url = GB_OTHER_URL + '/{}/default.aspx?tpid=011&token={}&languagecode={}'.format(dic[game], res, language)

        return Response({'game_url': url})

class GenerateFakeUserGameURL(APIView):

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):

        game = self.request.GET['game']

        TPUniqueID = uuid.uuid4()

        data = requests.post(GB_URL, json = {
            
        "GB": {
            "Method": "UpdateTPUniqueID",
            "TPCode": "011",
            "AuthKey": "kvZES8",
            "Params": {
                "MemberID": 'Fakeuser',
                "TPUniqueID": str(TPUniqueID) 
                }
            }
        })

        dic = data.json()

        if 'Error' in dic['GB']['Result']['ReturnSet']:
             
            create_user_data = requests.post(GB_URL, json = {
            
            "GB": {
                "Method": "CreateMember",
                "TPCode": "011",
                "AuthKey": "kvZES8",
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

            GBSN = create_user_data['GB']['Result']['ReturnSet']['"GBSN"']

        else:
            GBSN = dic['GB']['Result']['ReturnSet']['GBSN']

        res = requests.get(GB_API_URL + '?gbsn={}&TPUniqueID={}'.format(GBSN, TPUniqueID))
        res = res.content.decode('utf-8')
        res = res[2:-2]
       
        dic = {'SSC': 'ssc', 'K3': 'k3', 'PK10': 'pk10', 'Keno': 'keno', 'Lotto': 'lotto'}

        if game == 'GB Sports':
            url = GB_SPORT_URL + '?tpid=011&token={}&languagecode=en-us&oddstype=00001'.format(res)
        elif game == 'GB ESports':
            url = GB_SPORT_URL + '?tpid=011&token={}&languagecode=en-us&oddstype=00001&sc=00111'.format(res)
        else:
            url = GB_OTHER_URL + '/{}/default.aspx?tpid=011&token={}&languagecode=en-us'.format(dic[game], res)

        return Response({'game_url': url})


