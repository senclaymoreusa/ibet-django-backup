from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import CustomUser, GameRequestsModel 
import simplejson as json
import xmltodict
import decimal
import requests
import json
import uuid

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

        try:

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

                GameRequestsModel.objects.create(
                    TransType = TransType,
                    ThirdPartyCode = ThirdPartyCode,
                    MemberID = MemberID
                )

            except:
                error      = 'Member_Not_Found'
                error_code = -2

        except:

            pass

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
                    user = CustomUser.objects.filter(username = MemberID)
                    temp = user[0].main_wallet
                    if temp >= decimal.Decimal(BetTotalAmt):
                        current_balance = temp-decimal.Decimal(BetTotalAmt)
                        user.update(main_wallet=current_balance)
                        error      =  'No_Error'
                        error_code =  0
                        success    =  1
                        TransData  = current_balance

                    else:
                        error      =  'Insufficient_Balance'
                        error_code =  -4
                

                    GameRequestsModel.objects.create(
                        Method        = Method,
                        Success       = Success,

                        TransType     = TransType,
                        BetTotalCnt   = BetTotalCnt,
                        BetTotalAmt   = BetTotalAmt,

                        BetID         = BetID,
                        BetGrpNO      = BetGrpNO,
                        TPCode        = TPCode,
                        GBSN          = GBSN,
                        MemberID      = MemberID,
                        CurCode       = CurCode,
                        time          = BetDT,
                        BetType       = BetType,
                        BetTypeParam1 = BetTypeParam1,
                        BetTypeParam2 = BetTypeParam2,
                        Wintype       = Wintype,
                        HxMGUID       = HxMGUID,
                        InitBetAmt    = InitBetAmt,
                        RealBetAmt    = RealBetAmt,
                        HoldingAmt    = HoldingAmt,
                        InitBetRate   = InitBetRate,
                        RealBetRate   = RealBetRate,
                        PreWinAmt     = PreWinAmt
                    )

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

                BetID         = data['GB']['Result']['ReturnSet']['BettingList'][0]['BetID']
                BetGrpNO      = data['GB']['Result']['ReturnSet']['BettingList'][0]['BetGrpNO']
                TPCode        = data['GB']['Result']['ReturnSet']['BettingList'][0]['TPCode']
                GBSN          = data['GB']['Result']['ReturnSet']['BettingList'][0]['GBSN']
                MemberID      = data['GB']['Result']['ReturnSet']['BettingList'][0]['MemberID']
                CurCode       = data['GB']['Result']['ReturnSet']['BettingList'][0]['CurCode']
                BetDT         = data['GB']['Result']['ReturnSet']['BettingList'][0]['BetDT']
                BetType       = data['GB']['Result']['ReturnSet']['BettingList'][0]['BetType']
                BetTypeParam1 = data['GB']['Result']['ReturnSet']['BettingList'][0]['BetTypeParam1']
                BetTypeParam2 = data['GB']['Result']['ReturnSet']['BettingList'][0]['BetTypeParam2']
                Wintype       = data['GB']['Result']['ReturnSet']['BettingList'][0]['Wintype']
                HxMGUID       = data['GB']['Result']['ReturnSet']['BettingList'][0]['HxMGUID']
                InitBetAmt    = data['GB']['Result']['ReturnSet']['BettingList'][0]['InitBetAmt']
                RealBetAmt    = data['GB']['Result']['ReturnSet']['BettingList'][0]['RealBetAmt']
                HoldingAmt    = data['GB']['Result']['ReturnSet']['BettingList'][0]['HoldingAmt']
                InitBetRate   = data['GB']['Result']['ReturnSet']['BettingList'][0]['InitBetRate']
                RealBetRate   = data['GB']['Result']['ReturnSet']['BettingList'][0]['RealBetRate']
                PreWinAmt     = data['GB']['Result']['ReturnSet']['BettingList'][0]['PreWinAmt']

                try:
                    user = CustomUser.objects.filter(username = MemberID)
                    temp = user[0].main_wallet
                    if temp >= decimal.Decimal(BetTotalAmt):
                        current_balance = temp-decimal.Decimal(BetTotalAmt)
                        user.update(main_wallet=current_balance)
                        error      =  'No_Error'
                        error_code =  0
                        success    =  1
                        TransData  = current_balance

                    else:
                        error      =  'Insufficient_Balance'
                        error_code =  -4
                

                    GameRequestsModel.objects.create(
                        Method        = Method,
                        Success       = Success,

                        TransType     = TransType,
                        BetTotalCnt   = BetTotalCnt,
                        BetTotalAmt   = BetTotalAmt,

                        BetID         = BetID,
                        BetGrpNO      = BetGrpNO,
                        TPCode        = TPCode,
                        GBSN          = GBSN,
                        MemberID      = MemberID,
                        CurCode       = CurCode,
                        time          = BetDT,
                        BetType       = BetType,
                        BetTypeParam1 = BetTypeParam1,
                        BetTypeParam2 = BetTypeParam2,
                        Wintype       = Wintype,
                        HxMGUID       = HxMGUID,
                        InitBetAmt    = InitBetAmt,
                        RealBetAmt    = RealBetAmt,
                        HoldingAmt    = HoldingAmt,
                        InitBetRate   = InitBetRate,
                        RealBetRate   = RealBetRate,
                        PreWinAmt     = PreWinAmt
                    )

                except:
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

        if any(game in data['GB']['Result']['ReturnSet']['SettleList'] for game in game_list):
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

                    error      =  'No_Error'
                    error_code =  0
                    success    =  1
                    TransData  = user.main_wallet

                    GameRequestsModel.objects.create(
                        Method        = Method,
                        Success       = Success,

                        TransType     = TransType,
                        BetTotalCnt   = BetTotalCnt,
                        BetTotalAmt   = BetTotalAmt,

                        SettleID      = SettleID,
                        BetID         = BetID,
                        BetGrpNO      = BetGrpNO,
                        TPCode        = TPCode,
                        GBSN          = GBSN,
                        MemberID      = MemberID,
                        CurCode       = CurCode,
                        time          = BetDT,
                        BetType       = BetType,
                        BetTypeParam1 = BetTypeParam1,
                        BetTypeParam2 = BetTypeParam2,
                        Wintype       = Wintype,
                        HxMGUID       = HxMGUID,
                        InitBetAmt    = InitBetAmt,
                        RealBetAmt    = RealBetAmt,
                        HoldingAmt    = HoldingAmt,
                        InitBetRate   = InitBetRate,
                        RealBetRate   = RealBetRate,
                        PreWinAmt     = PreWinAmt,

                        BetResult     = BetResult,
                        WLAmt         = WLAmt,
                        RefundBetAmt  = RefundBetAmt,
                        TicketBetAmt  = TicketBetAmt,
                        TicketResult  = TicketResult,
                        TicketWLAmt   = TicketWLAmt,
                        SettleDT      = SettleDT
                    )

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
            
                SettleID      = data['GB']['Result']['ReturnSet']['SettleList'][0]['SettleID']
                BetID         = data['GB']['Result']['ReturnSet']['SettleList'][0]['BetID']
                BetGrpNO      = data['GB']['Result']['ReturnSet']['SettleList'][0]['BetGrpNO']
                TPCode        = data['GB']['Result']['ReturnSet']['SettleList'][0]['TPCode']
                GBSN          = data['GB']['Result']['ReturnSet']['SettleList'][0]['GBSN']
                MemberID      = data['GB']['Result']['ReturnSet']['SettleList'][0]['MemberID']
                CurCode       = data['GB']['Result']['ReturnSet']['SettleList'][0]['CurCode']
                BetDT         = data['GB']['Result']['ReturnSet']['SettleList'][0]['BetDT']
                BetType       = data['GB']['Result']['ReturnSet']['SettleList'][0]['BetType']
                BetTypeParam1 = data['GB']['Result']['ReturnSet']['SettleList'][0]['BetTypeParam1']
                BetTypeParam2 = data['GB']['Result']['ReturnSet']['SettleList'][0]['BetTypeParam2']
                Wintype       = data['GB']['Result']['ReturnSet']['SettleList'][0]['Wintype']
                HxMGUID       = data['GB']['Result']['ReturnSet']['SettleList'][0]['HxMGUID']
                InitBetAmt    = data['GB']['Result']['ReturnSet']['SettleList'][0]['InitBetAmt']
                RealBetAmt    = data['GB']['Result']['ReturnSet']['SettleList'][0]['RealBetAmt']
                HoldingAmt    = data['GB']['Result']['ReturnSet']['SettleList'][0]['HoldingAmt']
                InitBetRate   = data['GB']['Result']['ReturnSet']['SettleList'][0]['InitBetRate']
                RealBetRate   = data['GB']['Result']['ReturnSet']['SettleList'][0]['RealBetRate']
                PreWinAmt     = data['GB']['Result']['ReturnSet']['SettleList'][0]['PreWinAmt']
                BetResult     = data['GB']['Result']['ReturnSet']['SettleList'][0]['BetResult']
                WLAmt         = data['GB']['Result']['ReturnSet']['SettleList'][0]['WLAmt']
                try:
                    RefundBetAmt  = data['GB']['Result']['ReturnSet']['SettleList'][0]['RefundAmt'] 
                except:
                    RefundBetAmt  = data['GB']['Result']['ReturnSet']['SettleList'][0]['RefundBetAmt'] 
                TicketBetAmt  = data['GB']['Result']['ReturnSet']['SettleList'][0]['TicketBetAmt']
                TicketResult  = data['GB']['Result']['ReturnSet']['SettleList'][0]['TicketResult']
                TicketWLAmt   = data['GB']['Result']['ReturnSet']['SettleList'][0]['TicketWLAmt']
                SettleDT      = data['GB']['Result']['ReturnSet']['SettleList'][0]['SettleDT']

                try: 
                    user = CustomUser.objects.get(username = MemberID)

                    error      =  'No_Error'
                    error_code =  0
                    success    =  1
                    TransData  = user.main_wallet

                    GameRequestsModel.objects.create(
                        Method        = Method,
                        Success       = Success,

                        TransType     = TransType,
                        BetTotalCnt   = BetTotalCnt,
                        BetTotalAmt   = BetTotalAmt,

                        SettleID      = SettleID,
                        BetID         = BetID,
                        BetGrpNO      = BetGrpNO,
                        TPCode        = TPCode,
                        GBSN          = GBSN,
                        MemberID      = MemberID,
                        CurCode       = CurCode,
                        time          = BetDT,
                        BetType       = BetType,
                        BetTypeParam1 = BetTypeParam1,
                        BetTypeParam2 = BetTypeParam2,
                        Wintype       = Wintype,
                        HxMGUID       = HxMGUID,
                        InitBetAmt    = InitBetAmt,
                        RealBetAmt    = RealBetAmt,
                        HoldingAmt    = HoldingAmt,
                        InitBetRate   = InitBetRate,
                        RealBetRate   = RealBetRate,
                        PreWinAmt     = PreWinAmt,

                        BetResult     = BetResult,
                        WLAmt         = WLAmt,
                        RefundBetAmt  = RefundBetAmt,
                        TicketBetAmt  = TicketBetAmt,
                        TicketResult  = TicketResult,
                        TicketWLAmt   = TicketWLAmt,
                        SettleDT      = SettleDT
                    )

                except: 
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


class GenerateGameURL(APIView):

    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):

        print(self.request.user.username)

        TPUniqueID = uuid.uuid4()

        data = requests.post("http://uatapi.gbb2b.com/GBGameAPI/API.aspx", json = {
            
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

            temp = '-'.join([self.request.user.date_of_birth.split('/')[2], self.request.user.date_of_birth.split('/')[0], self.request.user.date_of_birth.split('/')[1]])
            print(temp)
            create_user_data = requests.post("http://uatapi.gbb2b.com/GBGameAPI/API.aspx", json = {
            
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
                    "Birthdate": '-'.join([self.request.user.date_of_birth.split('/')[2], self.request.user.date_of_birth.split('/')[0], self.request.user.date_of_birth.split('/')[1]]),
                    "CyCode": "CN",
                    "CurCode": "CNY",
                    "LangCode": "zh-cn",
                    "TPUniqueID": "new"
                    }
                }
            })

            print('456789')

            create_user_data = create_user_data.json()

            print(create_user_data)
            GBSN = create_user_data['GB']['Result']['ReturnSet']['"GBSN"']

        else:
            GBSN = dic['GB']['Result']['ReturnSet']['GBSN']

        res = requests.get('http://ibetapiscsharp-env.us-west-2.elasticbeanstalk.com/api/values/?gbsn={}&TPUniqueID={}'.format(GBSN, TPUniqueID))
        res = res.content.decode('utf-8')
        res = res[2:-2]

        url = 'http://164.claymoreusa.net/sports/asia/index.aspx?tpid=011&token={}&languagecode=en-us&oddstype=00001'.format(res)

        print(url)

        return Response({'game_url': url})



