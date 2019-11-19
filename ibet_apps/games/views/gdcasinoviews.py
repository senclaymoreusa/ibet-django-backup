from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from users.models import CustomUser
from  games.models import *
import hashlib,logging,hmac,requests,xmltodict,random,string
import xml.etree.ElementTree as ET
from time import gmtime, strftime, strptime
from rest_framework.authtoken.models import Token
from games.helper import *
logger = logging.getLogger('django')

#soap
from django.views.decorators.csrf import csrf_exempt
from spyne.application import Application
from spyne.decorator import rpc,srpc
from spyne.model.primitive import Unicode, Integer, Decimal, Double
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from spyne.service import ServiceBase,Service
from spyne.protocol.xml import XmlDocument
from spyne.util.django import DjangoComplexModel, DjangoService
from django.core.exceptions import  ObjectDoesNotExist
from spyne.error import ResourceNotFoundError,Fault
from spyne.model.complex import ComplexModel, XmlAttribute, Array

from django.db import transaction
class Container(ComplexModel):
    # __namespace__ = 'https://testgdgame-namespace.org'
    StatusCode = Integer
    UserBalance = Decimal
    

# class GD(DjangoComplexModel):
#     class Attributes(DjangoComplexModel.Attributes):
#         django_model = GDCasino
#         django_exclude = ['username','id','gameId','gameType','transactionId','currency']

class ObjectNotFoundError(ResourceNotFoundError):

    """Fault constructed from `model.DoesNotExist` exception."""

    def __init__(self, does_not_exist_exc):
        """Construct fault with code Client.<object_name>NotFound."""
        message = str(does_not_exist_exc)
        object_name = message.split()[0]
        # we do not want to reuse initialization of ResourceNotFoundError
        Fault.__init__(
            self, faultcode='Client.{0}NotFound'.format(object_name),
            faultstring=message)

class GetUserBalanceRequest(ComplexModel):
    __type_name__ = 'GetUserBalance'
    __namespace__ = 'https://testgdgame-namespace.org'
    _type_info = [
        ('userId', Unicode),
        ('currency', Unicode),
        ('loginToken', Unicode),
    ]
# class betDebit(ComplexModel):
#     __type_name__ = 'bet'
#     __namespace__ = 'https://testgdgame-namespace.org'
#     # _type_info = [
#     #     ('betType', Unicode),
#     #     ('amount', Decimal),
#     # ]
#     betType = Unicode
#     amount = Decimal
class Bet(ComplexModel):
    __type_name__ = 'bet'
    __namespace__ = 'https://testgdgame-namespace.org'
    betType = Unicode
    amount = Decimal
    result = Unicode
    betId = Unicode
    betTime = Unicode

class DebitRequest(ComplexModel):
    __type_name__ = 'Debit'
    __namespace__ = 'https://testgdgame-namespace.org'
    _type_info = [
        ('userId', Unicode),
        ('gameId', Unicode),
        ('gameType', Unicode),
        ('transactionId', Unicode),
        ('amount', Decimal),
        ('currency', Unicode),
        ('ipAddress', Unicode),
        ('gameView', Unicode),
        ('clientType', Unicode),
        ('betInfo', Array(Bet)),
        ('loginToken', Unicode),
        ('linkId', Unicode),
        
    ]

class CreditRequest(ComplexModel):
    __type_name__ = 'Credit'
    __namespace__ = 'https://testgdgame-namespace.org'
    _type_info = [
        ('userId', Unicode),
        ('gameId', Unicode),
        ('gameType', Unicode),
        ('transactionId', Unicode),
        ('amount', Decimal),
        ('currency', Unicode),
        ('validBetAmount', Unicode),
        ('betInfo', Array(Bet)),
        ('closeFlag', Unicode),
        ('ipAddress', Unicode),
        ('loginToken', Unicode),
        ('linkId', Unicode),
        ('turnOver', Unicode),
        ('winLoss', Unicode),
    ]
class TipRequest(ComplexModel):
    __type_name__ = 'Tip'
    __namespace__ = 'https://testgdgame-namespace.org'
    _type_info = [
        ('userId', Unicode),
        ('transactionId', Unicode),
        ('amount', Decimal),
        ('currency', Unicode),
        ('ipAddress', Unicode),
        ('loginToken', Unicode),
        ('tipId', Integer),
        ('anchorId', Integer)
    ]
class CancelRequest(ComplexModel):
    __type_name__ = 'Cancel'
    __namespace__ = 'https://testgdgame-namespace.org'
    _type_info = [
        ('userId', Unicode),
        ('gameId', Unicode),
        ('gameType', Unicode),
        ('transactionId', Unicode),
        ('amount', Decimal),
        ('currency', Unicode),
        ('cancelReason', Unicode),
        ('loginToken', Unicode),
    ]
 
class LiveDealerSoapService(ServiceBase):
    @rpc(GetUserBalanceRequest,  _body_style='bare', _returns=Container)
    def GetUserBalance(ctx,request):
        logger.info(request)
        userId = request.userId
        loginToken = request.loginToken
        currency = request.currency
        res = Container()
        try:
            user = CustomUser.objects.get(username=userId)
            userBalance = user.main_wallet
            token = Token.objects.get(user=user)
            

            res.StatusCode = 0
            res.UserBalance = userBalance
            return res
            
        except ObjectDoesNotExist as e:
            # raise ObjectNotFoundError(e)
            res.StatusCode = -1
            res.UserBalance = 0
            return res

    
    @rpc(DebitRequest, _body_style='bare', _returns=Container)
    def Debit(crx, request):
        try:
            PROVIDER = GameProvider.objects.get(provider_name="GD Casino")
        except ObjectDoesNotExist:
            logger.error("PROVIDER AND/OR CATEGORY RELATIONS DO NOT EXIST.")

        res = Container()
        try:
            user = CustomUser.objects.get(username=request.userId)
            userBalance = user.main_wallet - request.amount
            CATEGORY = request.gameType
            if CATEGORY == '6':
                category = 'Baccarat'
            elif CATEGORY == '28':
                category = 'Roulette'
            elif CATEGORY == '29':
                category = 'Sicbo'
            elif CATEGORY == '100':
                category = 'Slots'
            cate = Category.objects.get(name=category)
            token = Token.objects.get(user=user)
            if request.gameId == GDCASINO_FISHING_GAMEID:
                if CATEGORY == '100': #fishing
                    if str(token) == request.loginToken:
                        res.StatusCode = 0
                        GameBet.objects.create(provider=PROVIDER,   
                                            category=cate,
                                            game_name=request.gameId,
                                            username=user, 
                                            currency=request.currency, 
                                            market=ibetCN,
                                            ref_no=request.transactionId,
                                            amount_wagered=request.amount,
                                            )    
                    else:
                        res.StatusCode = 2
                    res.UserBalance = userBalance
                    user.main_wallet = userBalance
                    user.save()
                    return res
            else:
                if userBalance >= 0:
                    with transaction.atomic():
                        user.main_wallet = userBalance
                        user.save()
                    
                        if CATEGORY == '100': #slot
                            res.StatusCode = 0
                            GameBet.objects.create(provider=PROVIDER,
                                        
                                        category=cate,
                                        username=user, 
                                        currency=request.currency, 
                                        market=ibetCN,
                                        ref_no=request.transactionId,
                                        amount_wagered=request.amount,
                                        )
                        else:
                            if str(token) == request.loginToken:
                                res.StatusCode = 0
                                GameBet.objects.create(provider=PROVIDER, 
                                                    game_name=request.gameId,  
                                                    category=cate,
                                                    username=user, 
                                                    currency=request.currency, 
                                                    market=ibetCN,
                                                    ref_no=request.transactionId,
                                                    amount_wagered=request.amount,
                                                    )
                            else:
                                res.StatusCode = 2
                    res.UserBalance = userBalance
                    return res
                else:
                    res.UserBalance = user.main_wallet
                    res.StatusCode = 7
                    return res
            
        except ObjectDoesNotExist as e:
            res.StatusCode = -1
            res.UserBalance = 0
            return res


    @rpc(CreditRequest,_body_style='bare', _returns=Container)
    def Credit(crx,request):  
        try:
            PROVIDER = GameProvider.objects.get(provider_name="GD Casino")
        except ObjectDoesNotExist:
            logger.error("PROVIDER AND/OR CATEGORY RELATIONS DO NOT EXIST.")

        res = Container()
        try:
            user = CustomUser.objects.get(username=request.userId)
            userBalance = user.main_wallet + request.amount
            token = Token.objects.get(user=user)
            user.main_wallet = userBalance
            user.save()
            
            CATEGORY = request.gameType
            if CATEGORY == '6':
                category = 'Baccarat'
            elif CATEGORY == '28':
                category = 'Roulette'
            elif CATEGORY == '29':
                category = 'Sicbo'
            elif CATEGORY == '100':
                category = 'Slots'
            cate = Category.objects.get(name=category)
            if CATEGORY == '100':
                with transaction.atomic():
                    if request.gameId == GDCASINO_FISHING_GAMEID:
                        if int(request.winLoss) < 0:
                            GameBet.objects.create(provider=PROVIDER,   
                                                    category=cate,
                                                    username=user, 
                                                    game_name=request.gameId,
                                                    currency=request.currency, 
                                                    market=ibetCN,
                                                    ref_no=request.transactionId,
                                                    amount_wagered=request.amount,
                                                    amount_won=request.winLoss,
                                                    outcome=1,
                                                    )
                        else:
                            GameBet.objects.create(provider=PROVIDER,   
                                                    category=cate,
                                                    username=user, 
                                                    game_name=request.gameId,
                                                    currency=request.currency, 
                                                    market=ibetCN,
                                                    ref_no=request.transactionId,
                                                    amount_wagered=request.amount,
                                                    amount_won=request.winLoss,
                                                    outcome=0,
                                                    )
                        
                    else:
                        if int(request.amount) < 0:
                            GameBet.objects.create(provider=PROVIDER,   
                                                        category=cate,
                                                        username=user, 
                                                        currency=request.currency, 
                                                        market=ibetCN,
                                                        ref_no=request.transactionId,
                                                        amount_won=request.amount,
                                                        outcome=1,
                                                        )
                        else:
                            GameBet.objects.create(provider=PROVIDER,   
                                                        category=cate,
                                                        username=user, 
                                                        currency=request.currency, 
                                                        market=ibetCN,
                                                        ref_no=request.transactionId,
                                                        amount_won=request.amount,
                                                        outcome=0,
                                                        )
                    
                res.UserBalance = userBalance
                res.StatusCode = 0
                return res
            else: 
                try:
                    betTrans = GameBet.objects.get(provider=PROVIDER, category=cate,ref_no=request.transactionId,username=user)
                    
                    if str(token) == request.loginToken:
                        with transaction.atomic():
                            res.StatusCode = 0
                            betTrans.amount_won = request.amount
                            betTrans.outcome = 0
                            betTrans.save()
                    else:
                        res.StatusCode = 2
                    res.UserBalance = userBalance
                    return res
                except ObjectDoesNotExist as e:
                    res.StatusCode = -1
                    res.UserBalance = userBalance
                    return res
        except ObjectDoesNotExist as e:
            res.StatusCode = -1
            res.UserBalance = 0
            return res
    
    @rpc(TipRequest,_body_style='bare', _returns=Container)
    def Tip(crx, request): 
        try:
            PROVIDER = GameProvider.objects.get(provider_name="GD Casino")
        except ObjectDoesNotExist:
            logger.error("PROVIDER AND/OR CATEGORY RELATIONS DO NOT EXIST.")
 
        res = Container()
        try:
            user = CustomUser.objects.get(username=request.userId)
            userBalance = user.main_wallet - request.amount
            
            if userBalance > 0:
                token = Token.objects.get(user=user)
                user.main_wallet = userBalance
                user.save()
                
                cate = Category.objects.get(name='LIVE-CASINO')
                
                if str(token) == request.loginToken:
                    GameBet.objects.create(provider=PROVIDER,   
                                        category=cate,
                                        username=user, 
                                        currency=request.currency, 
                                        market=ibetCN,
                                        ref_no=request.transactionId,
                                        amount_wagered=request.amount,
                                        bet_type=TIP,
                                        )
                    res.StatusCode = 0
                else:
                    res.StatusCode = 2
                res.UserBalance = userBalance
                return res
            else:
                res.StatusCode = 7
                res.UserBalance = user.main_wallet
                return res 
        except ObjectDoesNotExist as e:
            res.StatusCode = -1
            res.UserBalance = 0
            return res
    
    @rpc(CancelRequest,_body_style='bare', _returns=Container)
    def Cancel(crx, request): 
        res = Container() 
        try:
            user = CustomUser.objects.get(username=request.userId)
            userBalance = user.main_wallet + request.amount
            token = Token.objects.get(user=user)

            try: 
                record = GameBet.objects.get(ref_no=request.transactionId,
                                              amount_wagered=request.amount,
                                              currency=request.currency,
                                              username=user)
                record.delete()
                user.main_wallet = userBalance
                user.save()
                res.StatusCode = 0
                res.UserBalance = userBalance
                return res
            except ObjectDoesNotExist as e:
                res.StatusCode = -1
                res.UserBalance = userBalance
                return res                    
            
        except ObjectDoesNotExist as e:
            res.StatusCode = -1
            res.UserBalance = 0
            return res

class SlotSoapService(ServiceBase):
    @rpc(Unicode(nillable=True),Unicode(nillable=True), _returns=Container)
    def GetUserBalance(ctx, userId, currency):
        res = Container()
        try:
            user = CustomUser.objects.get(username=userId)
            userBalance = user.main_wallet
            token = Token.objects.get(user=user)
            
            res.StatusCode = 0
            res.UserBalance = userBalance
            return res
            
        except ObjectDoesNotExist as e:
            raise ObjectNotFoundError(e)

def on_method_return_string(ctx):
    ctx.out_string[0] = ctx.out_string[0].replace(b'tns:', b'')
    ctx.out_string[0] = ctx.out_string[0].replace(b's0:', b'')

LiveDealerSoapService.event_manager.add_listener('method_return_string', on_method_return_string)

soap_app = Application(
    [LiveDealerSoapService],
    tns='https://testgdgame-namespace.org',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11(),
    
)
#soap_app.interface.nsmap['soap'] = soap_app.interface.nsmap['soap11env']
django_soap_application = DjangoApplication(soap_app)

my_soap_application = csrf_exempt(django_soap_application)



# def generateHash(message):
#     hash = hashlib.sha256(message.encode('utf-8')).hexdigest()
#     return hash
# def get_client_ip(request):
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip

#The following apis are for transfer wallet:

class LoginView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
        currency = request.GET['currency']
        username = request.GET['username']
        user = CustomUser.objects.get(username=username)
        token = Token.objects.get(user=user)
        
        lang = request.GET['lang']
        theme = request.GET['theme']
        list = [GDCASINO_MERCHANT_CODE, token, GDCASINO_MERCHANT_ACCESS_KEY, username, currency]
        message = ''.join(str(x) for x in list)
        
        #mymessage = bytes(message, 'utf-8') 
        key = generateHash(message)
        
        url = GDCASINO_URL
        user = CustomUser.objects.get(username=username)
        r = requests.get(url,  params = {
                # 'userId' : userId,
                'OperatorCode' : GDCASINO_MERCHANT_CODE,
                'Currency' : currency,
                'playerid': username,
                'lang': lang,
                'LoginTokenID': token,
                'theme': theme,
                'Key': key
            })
        rdata = r.text
        
        return HttpResponse(rdata)

class CreateMember(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        root = ET.Element("Request")
        a1 = ET.SubElement(root, "Header")
        a2 = ET.SubElement(root, "Param")
        b1 = ET.SubElement(a1, "Method")
        b1.text = 'cCreateMember'
        b2 = ET.SubElement(a1, "MerchantID")
        b2.text = GDCASINO_MERCHANT_CODE
        b3 = ET.SubElement(a1, "MessageID")
        b3.text = 'M' + strftime("%Y%m%d%H%M%S", gmtime())[2:]+str(''.join(random.choices(string.ascii_uppercase + string.ascii_letters + string.digits, k=5)))
        c1 = ET.SubElement(a2, "UserID")
        c1.text = request.POST['username']
        c2 = ET.SubElement(a2, "CurrencyCode")
        c2.text = request.POST['currency']
        c3 = ET.SubElement(a2, "BetGroup")
        c3.text = 'default'
        c4 = ET.SubElement(a2, "Affiliate")
        c4.text = ''
        data = ET.tostring(root)
        headers = {'Content-Type': 'application/xml'}
        r = requests.post(GDCASINO_API_URL, headers=headers, data=data)
        rdata = r.text
        
        if r.status_code == 200 or r.status_code == 201:
            tree = ET.fromstring(rdata)
            code = tree.find('Header').find('ErrorCode').text
            method = tree.find('Header').find('Method').text
            MerchantID = tree.find('Header').find('MerchantID').text
            
            MessageID = tree.find('Header').find('MessageID').text
            currency = tree.find('Param').find('CurrencyCode').text
            userid = tree.find('Param').find('UserID').text
            errorDes = tree.find('Param').find('ErrorDesc').text
            if code == '0': #SUCCESS
                create = GDCasino.objects.create(username=userid,
                                                 currency=currency,
                                                 message_id=MessageID )
                return Response({"ErrorCode": code, "Method":method, "MessageID": MessageID})
            else:
                return Response({"ErrorCode": code, "Method":method,"MessageID": MessageID, "ErrorDesc":errorDes })
        return Response(rdata)

class LogoutPlayer(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        root = ET.Element("Request")
        a1 = ET.SubElement(root, "Header")
        a2 = ET.SubElement(root, "Param")
        b1 = ET.SubElement(a1, "Method")
        b1.text = 'cLogoutPlayer'
        b2 = ET.SubElement(a1, "MerchantID")
        b2.text = GDCASINO_MERCHANT_CODE
        b3 = ET.SubElement(a1, "MessageID")
        b3.text = 'L' + strftime("%Y%m%d%H%M%S", gmtime())[2:]+str(''.join(random.choices(string.ascii_uppercase + string.ascii_letters + string.digits, k=5)))
        c1 = ET.SubElement(a2, "UserID")
        c1.text = request.POST['username']
        data = ET.tostring(root)
        headers = {'Content-Type': 'application/xml'}
        r = requests.post(GDCASINO_API_URL, headers=headers, data=data)
        rdata = r.text
        logger.info(rdata)
        if r.status_code == 200 or r.status_code == 201:
            tree = ET.fromstring(rdata)
            code = tree.find('Header').find('ErrorCode').text
            method = tree.find('Header').find('Method').text
            MerchantID = tree.find('Header').find('MerchantID').text
            MessageID = tree.find('Header').find('MessageID').text
            errorDes = tree.find('Param').find('ErrorDesc').text
            if code == '0': #SUCCESS
                return Response({"ErrorCode": code, "Method":method, "MessageID": MessageID})
            else:
                return Response({"ErrorCode": code, "Method":method,"MessageID": MessageID, "ErrorDesc":errorDes })
        return Response(rdata)

class Withdrawal(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        root = ET.Element("Request")
        a1 = ET.SubElement(root, "Header")
        a2 = ET.SubElement(root, "Param")
        b1 = ET.SubElement(a1, "Method")
        b1.text = 'cWithdrawal'
        b2 = ET.SubElement(a1, "MerchantID")
        b2.text = GDCASINO_MERCHANT_CODE
        b3 = ET.SubElement(a1, "MessageID")
        b3.text = 'W' + strftime("%Y%m%d%H%M%S", gmtime())[2:]+str(''.join(random.choices(string.ascii_uppercase + string.ascii_letters + string.digits, k=5)))
        c1 = ET.SubElement(a2, "UserID")
        c1.text = request.POST['username']
        c2 = ET.SubElement(a2, "CurrencyCode")
        c2.text = request.POST['currency']
        c3 = ET.SubElement(a2, "Amount")
        c3.text = request.POST['amount']
        data = ET.tostring(root)
        headers = {'Content-Type': 'application/xml'}
        r = requests.post(GDCASINO_API_URL, headers=headers, data=data)
        rdata = r.text
        logger.info(rdata)
        if r.status_code == 200 or r.status_code == 201:
            tree = ET.fromstring(rdata)
            code = tree.find('Header').find('ErrorCode').text
            method = tree.find('Header').find('Method').text
            MerchantID = tree.find('Header').find('MerchantID').text
            MessageID = tree.find('Header').find('MessageID').text
            errorDes = tree.find('Param').find('ErrorDesc').text
            transID = tree.find('Param').find('TransactionID').text
            paymentID = tree.find('Param').find('PaymentID').text
            if code == '0': #SUCCESS
                return Response({"ErrorCode": code, "Method":method, "MessageID": MessageID,"transID": transID, "paymentID": paymentID})
            else:
                return Response({"ErrorCode": code, "Method":method,"MessageID": MessageID,"transID": transID, "paymentID": paymentID,"ErrorDesc":errorDes })
        return Response(rdata)

class Deposit(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        root = ET.Element("Request")
        a1 = ET.SubElement(root, "Header")
        a2 = ET.SubElement(root, "Param")
        b1 = ET.SubElement(a1, "Method")
        b1.text = 'cDeposit'
        b2 = ET.SubElement(a1, "MerchantID")
        b2.text = GDCASINO_MERCHANT_CODE
        b3 = ET.SubElement(a1, "MessageID")
        b3.text = 'D' + strftime("%Y%m%d%H%M%S", gmtime())[2:]+str(''.join(random.choices(string.ascii_uppercase + string.ascii_letters + string.digits, k=5)))
        c1 = ET.SubElement(a2, "UserID")
        c1.text = request.POST['username']
        c2 = ET.SubElement(a2, "CurrencyCode")
        c2.text = request.POST['currency']
        c3 = ET.SubElement(a2, "Amount")
        c3.text = request.POST['amount']
        data = ET.tostring(root)
        
        headers = {'Content-Type': 'application/xml'}
        r = requests.post(GDCASINO_API_URL, headers=headers, data=data)
        rdata = r.text
        logger.info(rdata)
       
        if r.status_code == 200 or r.status_code == 201:
            tree = ET.fromstring(rdata)
            code = tree.find('Header').find('ErrorCode').text
            method = tree.find('Header').find('Method').text
            MerchantID = tree.find('Header').find('MerchantID').text
            MessageID = tree.find('Header').find('MessageID').text
            errorDes = tree.find('Param').find('ErrorDesc').text
            transID = tree.find('Param').find('TransactionID').text
            paymentID = tree.find('Param').find('PaymentID').text
            if code == '0': #SUCCESS
                return Response({"ErrorCode": code, "Method":method, "MessageID": MessageID,"transID": transID, "paymentID": paymentID})
            else:
                return Response({"ErrorCode": code, "Method":method,"MessageID": MessageID,"transID": transID, "paymentID": paymentID,"ErrorDesc":errorDes })
        return Response(rdata)

class CheckClient(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        root = ET.Element("Request")
        a1 = ET.SubElement(root, "Header")
        a2 = ET.SubElement(root, "Param")
        b1 = ET.SubElement(a1, "Method")
        b1.text = 'cCheckClient'
        b2 = ET.SubElement(a1, "MerchantID")
        b2.text = GDCASINO_MERCHANT_CODE
        b3 = ET.SubElement(a1, "MessageID")
        b3.text = 'C' + strftime("%Y%m%d%H%M%S", gmtime())[2:]+str(''.join(random.choices(string.ascii_uppercase + string.ascii_letters + string.digits, k=5)))
        c1 = ET.SubElement(a2, "UserID")
        c1.text = request.POST['username']
        c2 = ET.SubElement(a2, "CurrencyCode")
        c2.text = request.POST['currency']
        c3 = ET.SubElement(a2, "RequestBetLimit")
        c3.text = request.POST['bet_limit']
        data = ET.tostring(root)
       
        headers = {'Content-Type': 'application/xml'}
        r = requests.post(GDCASINO_API_URL, headers=headers, data=data)
        rdata = r.text
        logger.info(rdata)
        
        if r.status_code == 200 or r.status_code == 201:
            tree = ET.fromstring(rdata)
            code = tree.find('Header').find('ErrorCode').text
            method = tree.find('Header').find('Method').text
            MerchantID = tree.find('Header').find('MerchantID').text
            MessageID = tree.find('Header').find('MessageID').text
            errorDes = tree.find('Param').find('ErrorDesc').text
            balance = tree.find('Param').find('Balance').text
            player_group = tree.find('Param').find('PlayerGroup').text
            Baccarat = tree.find('Param').find('BetLimit').find('Baccarat')
            bet_list1 = {}
            for i, option in enumerate(Baccarat.findall('Option')):
                No = option.find('No').text
                Max = option.find('Max').text
                Min = option.find('Min').text
                baccarat_list = {}
                baccarat_list.update({"No" + str(i): No})
                baccarat_list.update({"Max" + str(i): Max})
                baccarat_list.update({"Min" + str(i): Min})
                bet_list1.update(baccarat_list)
                
            bet_list2 = {}
            Roulette = tree.find('Param').find('BetLimit').find('Roulette')
            for i, option in enumerate(Roulette.findall('Option')):
                No = option.find('No').text
                Max = option.find('Max').text
                Min = option.find('Min').text
                baccarat_list = {}
                baccarat_list.update({"No" + str(i): No})
                baccarat_list.update({"Max" + str(i): Max})
                baccarat_list.update({"Min" + str(i): Min})
                bet_list2.update(baccarat_list)

            if code == '0': #SUCCESS
                return Response({"ErrorCode": code, "Method":method, "MessageID": MessageID,
                "balance": balance, "PlayerGroup": player_group,"Baccarat":bet_list1, "Roulette":bet_list2})
            else:
                return Response({"ErrorCode": code, "Method":method,"MessageID": MessageID,"balance": balance, "PlayerGroup": player_group,"ErrorDesc":errorDes })
        return Response(rdata)

class GetBetHistory(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        root = ET.Element("Request")
        a1 = ET.SubElement(root, "Header")
        a2 = ET.SubElement(root, "Param")
        b1 = ET.SubElement(a1, "Method")
        b1.text = 'cGetBetHistory'
        b2 = ET.SubElement(a1, "MerchantID")
        b2.text = GDCASINO_MERCHANT_CODE
        b3 = ET.SubElement(a1, "MessageID")
        b3.text = 'H' + strftime("%Y%m%d%H%M%S", gmtime())[2:]+str(''.join(random.choices(string.ascii_uppercase + string.ascii_letters + string.digits, k=5)))
        c2 = ET.SubElement(a2, "FromTime")
        c2.text = request.POST['FromTime']
        c3 = ET.SubElement(a2, "ToTime")
        c3.text = request.POST['ToTime']
        c4 = ET.SubElement(a2, "Index")
        c4.text = request.POST['index']
        c1 = ET.SubElement(a2, "UserID")
        c1.text = request.POST['username']    
        c5 = ET.SubElement(a2, "ShowRefID")
        c5.text = '1'
        c5 = ET.SubElement(a2, "ShowOdds")
        c5.text = '1'
        data = ET.tostring(root)
        headers = {'Content-Type': 'application/xml'}
        r = requests.post(GDCASINO_API_URL, headers=headers, data=data)
        rdata = r.text
        logger.info(rdata)
        if r.status_code == 200 or r.status_code == 201:
            tree = ET.fromstring(rdata)
            code = tree.find('Header').find('ErrorCode').text
            method = tree.find('Header').find('Method').text
            MerchantID = tree.find('Header').find('MerchantID').text
            MessageID = tree.find('Header').find('MessageID').text
            errorDes = tree.find('Param').find('ErrorDesc').text

            if code == '0': #SUCCESS
                return Response(rdata)
            else:
                return Response(rdata)
        return Response(rdata)
class GetMemberBalance(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        root = ET.Element("Request")
        a1 = ET.SubElement(root, "Header")
        a2 = ET.SubElement(root, "Param")
        b1 = ET.SubElement(a1, "Method")
        b1.text = 'cGetMemberBalance'
        b2 = ET.SubElement(a1, "MerchantID")
        b2.text = GDCASINO_MERCHANT_CODE
        b3 = ET.SubElement(a1, "MessageID")
        b3.text = 'B' + strftime("%Y%m%d%H%M%S", gmtime())[2:]+str(''.join(random.choices(string.ascii_uppercase + string.ascii_letters + string.digits, k=5)))
        
        c4 = ET.SubElement(a2, "Index")
        c4.text = request.POST['index']
        c1 = ET.SubElement(a2, "CurrencyCode")
        c1.text = request.POST['currency']    
        c5 = ET.SubElement(a2, "BalanceMin")
        c5.text = request.POST['min']    
        # c5 = ET.SubElement(a2, "BalanceMax")
        # c5.text = request.POST['max']    
        data = ET.tostring(root)
        headers = {'Content-Type': 'application/xml'}
        r = requests.post(GDCASINO_API_URL, headers=headers, data=data)
        rdata = r.text
        
        if r.status_code == 200 or r.status_code == 201:
            tree = ET.fromstring(rdata)
            code = tree.find('Header').find('ErrorCode').text
            method = tree.find('Header').find('Method').text
            MerchantID = tree.find('Header').find('MerchantID').text
            MessageID = tree.find('Header').find('MessageID').text
            errorDes = tree.find('Param').find('ErrorDesc').text
            totalRecord = tree.find('Param').find('TotalRecord').text


            if code == '0': #SUCCESS
                return Response(rdata)
            else:
                return Response(rdata)
        return Response(rdata)
class checkTransactionStatus(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        root = ET.Element("Request")
        a1 = ET.SubElement(root, "Header")
        a2 = ET.SubElement(root, "Param")
        b1 = ET.SubElement(a1, "Method")
        b1.text = 'cCheckTransactionStatus'
        b2 = ET.SubElement(a1, "MerchantID")
        b2.text = GDCASINO_MERCHANT_CODE
        b3 = ET.SubElement(a1, "MessageID")
        b3.text = 'S' + strftime("%Y%m%d%H%M%S", gmtime())[2:]+str(''.join(random.choices(string.ascii_uppercase + string.ascii_letters + string.digits, k=5)))
        c2 = ET.SubElement(a2, "MessageID")
        c2.text = b3.text
        c4 = ET.SubElement(a2, "UserID")
        c4.text = request.POST['username']
        c1 = ET.SubElement(a2, "CurrencyCode")
        c1.text = request.POST['currency']    
        
        data = ET.tostring(root)
        
        headers = {'Content-Type': 'application/xml'}
        r = requests.post(GDCASINO_API_URL, headers=headers, data=data)
        rdata = r.text
        
        if r.status_code == 200 or r.status_code == 201:
            tree = ET.fromstring(rdata)
            code = tree.find('Header').find('ErrorCode').text
            method = tree.find('Header').find('Method').text
            MerchantID = tree.find('Header').find('MerchantID').text
            MessageID = tree.find('Header').find('MessageID').text
            errorDes = tree.find('Param').find('ErrorDesc').text
            TransactionID = tree.find('Param').find('TransactionID').text
            PaymentID = tree.find('Param').find('PaymentID').text
            Status = tree.find('Param').find('Status').text

            if code == '0': #SUCCESS
                return Response({"ErrorCode": code, "Method":method, "MessageID": MessageID,
                "TransactionID": TransactionID, "PaymentID": PaymentID,"Status":Status})
            else:
                return Response({"ErrorCode": code, "Method":method, "MessageID": MessageID,
                "TransactionID": TransactionID, "PaymentID": PaymentID,"Status":Status, "errorDes": errorDes})
        else:
            logger.info("There was something wrong with the result")
            logger.info(rdata)
            return Response(rdata)
        






    

