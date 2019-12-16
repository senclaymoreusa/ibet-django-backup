from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser
from  games.models import *
from django.utils import timezone
import decimal
import xmltodict
from games.helper import *
from django.core.exceptions import  ObjectDoesNotExist
import requests
import xml.etree.ElementTree as ET
import random
from django.utils import timezone
from time import gmtime, strftime, strptime
from django.http import  HttpResponse
from rest_framework.decorators import api_view, permission_classes
from time import sleep
from  accounting.models import *


def checkCreateGameAccoutOrGetBalance(user,password,method,oddtype,actype,cur):
    
    s = "cagent=" + AG_CAGENT + "/\\\\/" + "loginname=" + user.username + "/\\\\/" + "method=" + method + "/\\\\/" + "actype=" + actype + "/\\\\/" + "password=" + password + "/\\\\/" + "oddtype=" + oddtype + "/\\\\/" + "cur=" + cur  
    
    param = des_encrypt(s,AG_DES).decode("utf-8") 

    key = MD5(param + AG_MD5)
    r = requests.get(AG_URL ,  params={
            "params": param,
            "key": key,  
        })
    rdata = r.text
    
    if r.status_code == 200:
        tree = ET.fromstring(rdata)
        info = tree.get('info')   
        msg =  tree.get('msg')
        if info == '0' or msg == '':
            return 0
        else:
            return 1
    else:
        return 1
    


    
@api_view(['POST'])
@permission_classes((AllowAny,))        
def getBalance(request):  
    username =  request.POST['username']
    password = request.POST['password']
    oddtype = request.POST['oddtype']
    actype = request.POST['actype']
    cur = request.POST['cur']
    try:
        user = CustomUser.objects.get(username=username)
        s = "cagent=" + AG_CAGENT + "/\\\\/" + "loginname=" + username + "/\\\\/" + "method=" + "gb" + "/\\\\/" + "actype=" + actype + "/\\\\/" + "password=" + password + "/\\\\/" + "oddtype=" + oddtype + "/\\\\/" + "cur=" + cur  
        
        param = des_encrypt(s,AG_DES).decode("utf-8") 

        key = MD5(param + AG_MD5)
        r = requests.get(AG_URL ,  params={
                "params": param,
                "key": key,  
            })
        rdata = r.text
        if r.status_code == 200:
            tree = ET.fromstring(rdata)
            info = tree.get('info')
            msg =  tree.get('msg')
            return Response({'info': info, 'msg': msg})
        else:
            return Response({"error":"The request is failed"}) 
    except ObjectDoesNotExist:
        return Response({"error":"The user is not existed."}) 


def prepareTransferCredit(user, password, actype, cur, agtype, gameCategory, credit, fixcredit, billno):    

    
        
    s = "cagent=" + AG_CAGENT + "/\\\\/" + "loginname=" + user.username + "/\\\\/" + "method=tc/\\\\/" + "billno=" + billno +  "/\\\\/" + "type=" + agtype + "/\\\\/" + "fixcredit=" + fixcredit + "/\\\\/" + "credit=" + credit + "/\\\\/"+ "actype=" + actype + "/\\\\/" + "password=" + password + "/\\\\/" +  "gameCategory=" + gameCategory + "/\\\\/" + "cur=" + cur  
    
    param = des_encrypt(s,AG_DES).decode("utf-8") 
    
    key = MD5(param + AG_MD5)
    
    r = requests.get(AG_URL ,  params={
            "params": param,
            "key": key,  
        })
    rdata = r.text
    
    if r.status_code == 200:
        tree = ET.fromstring(rdata)
        info = tree.get('info')
        msg =  tree.get('msg')
        if info == '0':
            return 0
        else:
            return 1
        
    else:
        return 1
    


def transferCreditConfirm(user,password,actype,cur,agtype,fixcredit,gameCategory,credit,flag,billno):
      
    s = "cagent=" + AG_CAGENT + "/\\\\/" + "loginname=" + user.username + "/\\\\/" + "method=tcc/\\\\/" + "billno=" + billno +  "/\\\\/" + "type=" + agtype + "/\\\\/" + "credit=" + credit + "/\\\\/" + "fixcredit=" + fixcredit + "/\\\\/" + "actype=" + actype + "/\\\\/" +"flag=" + flag + "/\\\\/"  +  "password=" + password + "/\\\\/" +  "gameCategory=" + gameCategory + "/\\\\/" + "cur=" + cur  
    
    param = des_encrypt(s,AG_DES).decode("utf-8") 
    
    key = MD5(param + AG_MD5)
    
    r = requests.get(AG_URL ,  params={
            "params": param,
            "key": key,  
        })
    rdata = r.text
    
    if r.status_code == 200:
        tree = ET.fromstring(rdata)
        info = tree.get('info')
        msg =  tree.get('msg')
        if info == '0':
            return 0
        elif info == '1': #失败, 订单未处理状态
            return 1
        elif info == '2': #因无效的转账金额引致的失败
            return 2
        
    else:
        return 1
    


def queryOrderStatus(actype,cur,billno):      
    s = "cagent=" + AG_CAGENT + "/\\\\/" + "billno=" + billno + "/\\\\/" + "method=qos/\\\\/" + "actype=" + actype + "/\\\\/" + "cur=" + cur  
    
    param = des_encrypt(s,AG_DES).decode("utf-8") 

    key = MD5(param + AG_MD5)
    r = requests.get(AG_URL ,  params={
            "params": param,
            "key": key,  
        })
    rdata = r.text
    if r.status_code == 200:
        tree = ET.fromstring(rdata)
        info = tree.get('info')
        msg =  tree.get('msg')
        if info == '0':
            return 0
        elif info == '1':
            return 1
        elif info == '2':
            return 2
        elif info == 'network_error':
            return 3    
    else:
        return 4

#check or create game account and login to game lobby
@api_view(['POST'])
@permission_classes((AllowAny,))        
def forwardGame(request):
    username =  request.POST['username']
    password = request.POST['password']
    actype = request.POST['actype']
    cur = request.POST['cur']
    agtype = request.POST['type']
    credit = request.POST['credit']
    lang = request.POST['lang']
    billno = request.POST['billno']
    gameType = request.POST['gameType']
    oddtype = request.POST['oddtype']
    lg_method = 'lg'
    sid = AG_CAGENT + strftime("%Y%m%d%H%M%S", gmtime()) + str(random.randint(0, 10000000))
    try:
        user = CustomUser.objects.get(username=username)
        if checkCreateGameAccoutOrGetBalance(username, password, lg_method, oddtype, actype, cur) == 0:
            s = "cagent=" + AG_CAGENT + "/\\\\/" + "loginname=" + username + "/\\\\/" + "dm=" + AG_DM + "/\\\\/" + "sid=" + sid + "/\\\\/" + "lang=" + lang + "/\\\\/" + "gameType=" + gameType +  "/\\\\/" + "oddtype=" + oddtype +  "/\\\\/" +  "actype=" + actype + "/\\\\/"  +  "password=" + password + "/\\\\/" +   "cur=" + cur  
            
            param = des_encrypt(s,AG_DES).decode("utf-8") 
            
            key = MD5(param + AG_MD5)
            
            
            r = requests.get(AG_FORWARD_URL ,  data={
                    "params": param,
                    "key": key,  
                })
            rdata = r.text
        else:
            return Response({"error": "Cannot check or create AG game account."})
        
                
        return HttpResponse(rdata)
        
    except ObjectDoesNotExist:
        return Response({"error":"The  user is not existed."}) 


def fundTransfer(user, fund_wallet, password, oddtype, actype, gameCategory, credit, fixcredit, cur, agtype): 
        username =  user.username
        trans_id = username + strftime("%Y%m%d%H%M%S", gmtime())+str(random.randint(0,10000000))
        # password = request.POST['password']
        # oddtype = request.POST['oddtype']
        # actype = request.POST['actype']
        # cur = request.POST['cur']
        # agtype = request.POST['agtype']
        # gameCategory = request.POST['gameCategory']
        # credit = request.POST['credit']
        # fixcredit = request.POST['fixcredit']
        billno = AG_CAGENT + strftime("%Y%m%d%H%M%S", gmtime())
        lg_method = 'lg'
        gb_method = 'gb'
        success = True
        confirm = True
        checking = True
        if checkCreateGameAccoutOrGetBalance(user, password, lg_method, oddtype, actype, cur) == 0: #check or create game account
            while success:
                if checkCreateGameAccoutOrGetBalance(user, password, gb_method, oddtype, actype, cur) == 0: #get balance
                    if prepareTransferCredit(user, password, actype, cur, agtype, gameCategory, credit, fixcredit, billno) == 0:
                        print("prepare")
                        delay = kwargs.get("delay", 5)
                        while confirm:
                            flag = '1'
                            if transferCreditConfirm(user,password,actype,cur,agtype,fixcredit,gameCategory,credit,flag,billno) == 0:
                                if agtype == 'IN':
                                    Transaction.objects.create(transaction_id=trans_id,
                                        user_id=user,
                                        order_id=trans_id,
                                        amount=amount,
                                        currency=user.currency,
                                        transfer_from=fund_wallet,
                                        transfer_to='AG',
                                        product=0,
                                        transaction_type=TRANSACTION_TRANSFER,
                                        status=TRAN_SUCCESS_TYPE)
                                else:
                                    Transaction.objects.create(transaction_id=trans_id,
                                        user_id=user,
                                        order_id=trans_id,
                                        amount=amount,
                                        currency=user.currency,
                                        transfer_from='AG',
                                        transfer_to=fund_wallet,
                                        product=0,
                                        transaction_type=TRANSACTION_TRANSFER,
                                        status=TRAN_SUCCESS_TYPE)
                                print("confirm")
                                success = False
                                confirm = False
                                return CODE_SUCCESS
                                break
                                   
                            else:
                                while checking:
                                    if queryOrderStatus(actype,cur,billno) == 0:
                                        print("query")
                                        success = False
                                        confirm = False
                                        checking = False
                                        if agtype == 'IN':
                                            Transaction.objects.create(transaction_id=trans_id,
                                                user_id=user,
                                                order_id=trans_id,
                                                amount=amount,
                                                currency=user.currency,
                                                transfer_from=fund_wallet,
                                                transfer_to='AG',
                                                product=0,
                                                transaction_type=TRANSACTION_TRANSFER,
                                                status=TRAN_SUCCESS_TYPE)
                                        else:
                                            Transaction.objects.create(transaction_id=trans_id,
                                                user_id=user,
                                                order_id=trans_id,
                                                amount=amount,
                                                currency=user.currency,
                                                transfer_from='AG',
                                                transfer_to=fund_wallet,
                                                product=0,
                                                transaction_type=TRANSACTION_TRANSFER,
                                                status=TRAN_SUCCESS_TYPE)
                                        return CODE_SUCCESS
                                        break
                                    elif queryOrderStatus(actype,cur,billno) == 1:  
                                        success = True
                                        confirm = True
                                        checking = False
                                        
                                    elif queryOrderStatus(actype,cur,billno) == 3:  
                                        checking = True       
                                        sleep(delay)
                                        
                                    elif queryOrderStatus(actype,cur,billno) == 2: 
                                        success = True
                                        confirm = False
                                        checking = False
                                        sleep(delay)
                                        

                    else:
                        success = False
                        return Response({"error": "Cannot prepare transfer credit for AG game account."})
                        break
                else:
                    success = False
                    return Response({"error": "Cannot get balance for AG game account."})
                    break
        else:
            return Response({"error": "Cannot check or create AG game account."})

class test(APIView):
    permission_classes = (AllowAny, )
    def get(self, request, *args, **kwargs):
        user = CustomUser.objects.get(username="angela01")
        response = fundTransfer(user,  "main", "123123", "A", "1", "0", "300.00", "", "CNY", "IN")
        return HttpResponse(response)
  
class PostTransferforAG(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):

        ResponseCode = 'ERROR'
        balance = None

        data = str(request.body, 'utf-8')

        dic = xmltodict.parse(data)

        try:
            transactionType  = dic['Data']['Record']['transactionType']
        except:
            pass 

        if transactionType == 'BET':

            try:

                sessionToken    = dic['Data']['Record']['sessionToken']
                currency        = dic['Data']['Record']['currency']
                value           = dic['Data']['Record']['value']
                playname        = dic['Data']['Record']['playname']
                agentCode       = dic['Data']['Record']['agentCode']
                betTime         = dic['Data']['Record']['betTime']
                transactionID   = dic['Data']['Record']['transactionID']
                platformType    = dic['Data']['Record']['platformType']
                Round           = dic['Data']['Record']['round']
                gametype        = dic['Data']['Record']['gametype']
                gameCode        = dic['Data']['Record']['gameCode']
                tableCode       = dic['Data']['Record']['tableCode']
                transactionCode = dic['Data']['Record']['transactionCode']
                deviceType      = dic['Data']['Record']['deviceType']
                playtype        = dic['Data']['Record']['playtype']

                username = playname[len(agentCode):]
                
                try:

                    user = CustomUser.objects.filter(username = username)
                    balance = user[0].main_wallet

                    if balance >= decimal.Decimal(value):

                        balance -= decimal.Decimal(value)
                        user.update(main_wallet=balance, modified_time=timezone.now())
                        ResponseCode = 'OK'
                        Status = status.HTTP_200_OK

                    else:

                        Status = status.HTTP_409_CONFLICT
                        ResponseCode = 'INSUFFICIENT_FUNDS'

                except:
                        Status = status.HTTP_400_BAD_REQUEST
                        ResponseCode = 'INVALID_DATA'

                # GameRequestsModel.objects.create(
                #     sessionToken    = sessionToken,
                #     currency        = currency,
                #     MemberID        = username,
                #     agentCode       = agentCode,
                #     time           = betTime,
                #     transactionID   = transactionID,
                #     platformType    = platformType,
                #     Round           = Round,
                #     gametype        = gametype,
                #     gameCode        = gameCode,
                #     tableCode       = tableCode,
                #     TransType       = transactionType,
                #     transactionCode = transactionCode,
                #     deviceType      = deviceType, 
                #     playtype        = playtype
                # )

            except:

                Status = status.HTTP_400_BAD_REQUEST
                ResponseCode = 'INVALID_DATA'

            #print(sessionToken, currency, value, playname, agentCode, betTime, transactionID, platformType, Round, gametype, gameCode, tableCode, transactionType, transactionCode, deviceType, playtype )


        elif transactionType == 'WIN':

            try:

                sessionToken    = dic['Data']['Record']['sessionToken']
                currency        = dic['Data']['Record']['currency']
                netAmount       = dic['Data']['Record']['netAmount']
                validBetAmount  = dic['Data']['Record']['validBetAmount']
                playname        = dic['Data']['Record']['playname']
                agentCode       = dic['Data']['Record']['agentCode']
                settletime      = dic['Data']['Record']['settletime']
                transactionID   = dic['Data']['Record']['transactionID']
                billNo          = dic['Data']['Record']['billNo']
                gametype        = dic['Data']['Record']['gametype']
                gameCode        = dic['Data']['Record']['gameCode']
                transactionCode = dic['Data']['Record']['transactionCode']
                ticketStatus    = dic['Data']['Record']['ticketStatus']
                gameResult      = dic['Data']['Record']['gameResult']
                finish          = dic['Data']['Record']['finish']

                username = playname[len(agentCode):]

                try:

                    user = CustomUser.objects.filter(username = username)
                    balance = user[0].main_wallet
                    balance += decimal.Decimal(netAmount) + decimal.Decimal(validBetAmount)
                    user.update(main_wallet=balance, modified_time=timezone.now())
                    ResponseCode = 'OK'
                    Status = status.HTTP_200_OK

                except:

                    Status = status.HTTP_400_BAD_REQUEST
                    ResponseCode = 'INVALID_DATA'

                # GameRequestsModel.objects.create(
                #     sessionToken    = sessionToken,
                #     currency        = currency,
                #     netAmount       = netAmount,
                #     validBetAmount  = validBetAmount, 
                #     MemberID        = username, 
                #     agentCode       = agentCode, 
                #     time            = settletime, 
                #     transactionID   = transactionID, 
                #     billNo          = billNo, 
                #     gametype        = gametype, 
                #     gameCode        = gameCode, 
                #     TransType       = transactionType, 
                #     transactionCode = transactionCode, 
                #     ticketStatus    = ticketStatus, 
                #     gameResult      = gameResult, 
                #     finish          = finish
                # )

            except:

                Status = status.HTTP_400_BAD_REQUEST
                ResponseCode = 'INVALID_DATA'

        elif transactionType == 'LOSE':

            try:

                sessionToken    = dic['Data']['Record']['sessionToken']
                currency        = dic['Data']['Record']['currency']
                netAmount       = dic['Data']['Record']['netAmount']
                validBetAmount  = dic['Data']['Record']['validBetAmount']
                playname        = dic['Data']['Record']['playname']
                agentCode       = dic['Data']['Record']['agentCode']
                settletime      = dic['Data']['Record']['settletime']
                transactionID   = dic['Data']['Record']['transactionID']
                billNo          = dic['Data']['Record']['billNo']
                gametype        = dic['Data']['Record']['gametype']
                gameCode        = dic['Data']['Record']['gameCode']
                transactionCode = dic['Data']['Record']['transactionCode']
                ticketStatus    = dic['Data']['Record']['ticketStatus']
                gameResult      = dic['Data']['Record']['gameResult']
                finish          = dic['Data']['Record']['finish']

                #print(sessionToken, currency, netAmount, validBetAmount, playname, agentCode, settletime, transactionID, billNo, gametype, gameCode, transactionType, transactionCode, ticketStatus, gameResult, finish)

                username = playname[len(agentCode):]

                try:

                    user = CustomUser.objects.filter(username = username)
                    balance = user[0].main_wallet
                    balance += decimal.Decimal(validBetAmount) + decimal.Decimal(netAmount)
                    user.update(main_wallet=balance, modified_time=timezone.now())
                    ResponseCode = 'OK'
                    Status = status.HTTP_200_OK

                except:

                    Status = status.HTTP_400_BAD_REQUEST
                    ResponseCode = 'INVALID_DATA'

                # GameRequestsModel.objects.create(
                #     sessionToken    = sessionToken, 
                #     currency        = currency, 
                #     netAmount       = netAmount, 
                #     validBetAmount  = validBetAmount, 
                #     MemberID        = username, 
                #     agentCode       = agentCode, 
                #     time            = settletime, 
                #     transactionID   = transactionID, 
                #     billNo          = billNo, 
                #     gametype        = gametype, 
                #     gameCode        = gameCode, 
                #     TransType       = transactionType, 
                #     transactionCode = transactionCode, 
                #     ticketStatus    = ticketStatus, 
                #     gameResult      = gameResult, 
                #     finish          = finish
                # )

            except:

                Status = status.HTTP_400_BAD_REQUEST
                ResponseCode = 'INVALID_DATA'

        elif transactionType == 'WIN' and True: # This shares the same parameter with Win, needs to be further implemented

            try:

                sessionToken    = dic['Data']['Record']['sessionToken']
                currency        = dic['Data']['Record']['currency']
                netAmount       = dic['Data']['Record']['netAmount']
                validBetAmount  = dic['Data']['Record']['validBetAmount']
                playname        = dic['Data']['Record']['playname']
                agentCode       = dic['Data']['Record']['agentCode']
                settletime      = dic['Data']['Record']['settletime']
                transactionID   = dic['Data']['Record']['transactionID']
                billNo          = dic['Data']['Record']['billNo']
                gametype        = dic['Data']['Record']['gametype']
                gameCode        = dic['Data']['Record']['gameCode']
                transactionCode = dic['Data']['Record']['transactionCode']
                ticketStatus    = dic['Data']['Record']['ticketStatus']
                gameResult      = dic['Data']['Record']['gameResult']
                finish          = dic['Data']['Record']['finish']

                #print(sessionToken, currency, netAmount, validBetAmount, playname, agentCode, settletime, transactionID, billNo, gametype, gameCode, transactionType, transactionCode, ticketStatus, gameResult, finish)

                username = playname[len(agentCode):]

                try:

                    user = CustomUser.objects.filter(username = username)
                    balance = user[0].main_wallet
                    balance += decimal.Decimal(validBetAmount) + decimal.Decimal(netAmount)
                    user.update(main_wallet=balance, modified_time=timezone.now())
                    ResponseCode = 'OK'
                    Status = status.HTTP_200_OK

                except:

                    Status = status.HTTP_400_BAD_REQUEST
                    ResponseCode = 'INVALID_DATA'


                # GameRequestsModel.objects.create(
                #     sessionToken     = sessionToken, 
                #     currency         = currency, 
                #     netAmount        = netAmount, 
                #     validBetAmount   =  validBetAmount, 
                #     MemberID         =  username, 
                #     agentCode        =  agentCode, 
                #     time             = settletime, 
                #     transactionID    = transactionID, 
                #     billNo           =  billNo, 
                #     gametype         =  gametype, 
                #     gameCode         =  gameCode, 
                #     TransType        =  transactionType, 
                #     transactionCode  =  transactionCode, 
                #     ticketStatus     =  ticketStatus, 
                #     gameResult       =   gameResult, 
                #     finish  =  finish
                # )

            except:

                Status = status.HTTP_400_BAD_REQUEST
                ResponseCode = 'INVALID_DATA'

        elif transactionType == 'REFUND':

            try:

                ticketStatus    = dic['Data']['Record']['ticketStatus']
                sessionToken    = dic['Data']['Record']['sessionToken']
                currency        = dic['Data']['Record']['currency']
                value           = dic['Data']['Record']['value']
                playname        = dic['Data']['Record']['playname']
                agentCode       = dic['Data']['Record']['agentCode']
                betTime         = dic['Data']['Record']['betTime']
                transactionID   = dic['Data']['Record']['transactionID']
                platformType    = dic['Data']['Record']['platformType']
                Round           = dic['Data']['Record']['round']
                gametype        = dic['Data']['Record']['gametype']
                gameCode        = dic['Data']['Record']['gameCode']
                tableCode       = dic['Data']['Record']['tableCode']
                transactionCode = dic['Data']['Record']['transactionCode']
                playtype        = dic['Data']['Record']['playtype']

                #print(ticketStatus, sessionToken, currency, value, playname, agentCode, betTime, transactionID, platformType, Round, gametype, gameCode, tableCode, transactionType, transactionCode, playtype)

                username = playname[len(agentCode):]

                try:

                    user = CustomUser.objects.filter(username = username)
                    balance = user[0].main_wallet
                    balance += decimal.Decimal(value)
                    user.update(main_wallet=balance, modified_time=timezone.now())
                    ResponseCode = 'OK'
                    Status = status.HTTP_200_OK

                except:

                    Status = status.HTTP_400_BAD_REQUEST
                    ResponseCode = 'INVALID_DATA'


                # GameRequestsModel.objects.create(
                #     ticketStatus    = ticketStatus, 
                #     sessionToken    = sessionToken, 
                #     currency        = currency, 
                #     value           = value, 
                #     MemberID        = username, 
                #     agentCode       = agentCode, 
                #     time            = betTime, 
                #     transactionID   = transactionID, 
                #     platformType    = platformType, 
                #     Round           = Round, 
                #     gametype        = gametype, 
                #     gameCode        = gameCode, 
                #     tableCode       = tableCode, 
                #     TransType       = transactionType, 
                #     transactionCode = transactionCode, 
                #     playtype = playtype
                # )

            except:

                Status = status.HTTP_400_BAD_REQUEST
                ResponseCode = 'INVALID_DATA'

        elif transactionType == 'BALANCE':

            try:

                sessionToken     = dic['Data']['Record']['sessionToken']
                playname         = dic['Data']['Record']['playname']

                i = 0
                while playname[i].isalpha():
                    i += 1
                while playname[i].isnumeric():
                    i += 1
            
                username = playname[i:]

                try:

                    user = CustomUser.objects.get(username = username)
                    balance = user.main_wallet
                    Status = status.HTTP_200_OK
                    ResponseCode = 'OK'

                except:

                    Status = status.HTTP_400_BAD_REQUEST
                    ResponseCode = 'INVALID_DATA'

                # GameRequestsModel.objects.create(
                #     sessionToken = sessionToken,
                #     MemberID     = username,
                #     TransType    = transactionType
                # )

            except:

                Status = status.HTTP_400_BAD_REQUEST
                ResponseCode = 'INVALID_DATA'

        elif transactionType == 'WITHDRAW':

            try:

                sessionToken     = dic['Data']['Record']['sessionToken']
                playname         = dic['Data']['Record']['playname']
                transactionID    = dic['Data']['Record']['transactionID']
                currency         = dic['Data']['Record']['currency']
                amount           = dic['Data']['Record']['amount']
                gameId           = dic['Data']['Record']['gameId']
                roundId          = dic['Data']['Record']['roundId']
                time             = dic['Data']['Record']['time']
                remark           = dic['Data']['Record']['remark']

                #print(sessionToken, playname, transactionType, transactionID, currency, amount, gameId, roundId, time, remark)

                i = 0
                while playname[i].isalpha():
                    i += 1
                while playname[i].isnumeric():
                    i += 1
            
                username = playname[i:]

                try:

                    user = CustomUser.objects.filter(username = username)
                    balance = user[0].main_wallet

                    if balance >= decimal.Decimal(amount):
                        balance -= decimal.Decimal(amount)
                        user.update(main_wallet=balance, modified_time=timezone.now())
                        ResponseCode = 'OK'
                        Status = status.HTTP_200_OK

                    else:
                        
                        Status = status.HTTP_409_CONFLICT
                        ResponseCode = 'INSUFFICIENT_FUNDS'

                except:
                    Status = status.HTTP_400_BAD_REQUEST
                    ResponseCode = 'INVALID_DATA'

                # GameRequestsModel.objects.create(
                #     sessionToken     = sessionToken, 
                #     MemberID         = username, 
                #     TransType        = transactionType, 
                #     transactionID    = transactionID, 
                #     currency         = currency, 
                #     amount           = amount, 
                #     gameId           = gameId, 
                #     roundId          = roundId, 
                #     time             = time, 
                #     remark           = remark,
                # )

            
            except:

                Status = status.HTTP_400_BAD_REQUEST
                ResponseCode = 'INVALID_DATA'

        elif transactionType == 'DEPOSIT':

            try:

                sessionToken     = dic['Data']['Record']['sessionToken']
                playname         = dic['Data']['Record']['playname']
                transactionType  = dic['Data']['Record']['transactionType']
                transactionID    = dic['Data']['Record']['transactionID']
                currency         = dic['Data']['Record']['currency']
                amount           = dic['Data']['Record']['amount']
                gameId           = dic['Data']['Record']['gameId']
                roundId          = dic['Data']['Record']['roundId']
                time             = dic['Data']['Record']['time']
                remark           = dic['Data']['Record']['remark']

                #print(sessionToken, playname, transactionType, transactionID, currency, amount, gameId, roundId, time, remark)

                i = 0
                while playname[i].isalpha():
                    i += 1
                while playname[i].isnumeric():
                    i += 1
            
                username = playname[i:]

                try:

                    user = CustomUser.objects.filter(username = username)
                    balance = user[0].main_wallet
                    balance += decimal.Decimal(amount)
                    user.update(main_wallet=balance, modified_time=timezone.now())
                    ResponseCode = 'OK'
                    Status = status.HTTP_200_OK

                except:
                    Status = status.HTTP_400_BAD_REQUEST
                    ResponseCode = 'INVALID_DATA'

                # GameRequestsModel.objects.create(
                #     sessionToken     = sessionToken, 
                #     MemberID         = username, 
                #     TransType        = transactionType, 
                #     transactionID    = transactionID, 
                #     currency         = currency, 
                #     amount           = amount, 
                #     gameId           = gameId, 
                #     roundId          = roundId, 
                #     time             = time, 
                #     remark           = remark,
                # )

            except:

                Status = status.HTTP_400_BAD_REQUEST
                ResponseCode = 'INVALID_DATA'


        elif transactionType == 'ROLLBACK':    # Does not do anything for now

            try:

                sessionToken     = dic['Data']['Record']['sessionToken']
                playname         = dic['Data']['Record']['playname']
                transactionID    = dic['Data']['Record']['transactionID']
                currency         = dic['Data']['Record']['currency']
                amount           = dic['Data']['Record']['amount']
                gameId           = dic['Data']['Record']['gameId']
                roundId          = dic['Data']['Record']['roundId']
                time             = dic['Data']['Record']['time']
                remark           = dic['Data']['Record']['remark']

                #print(sessionToken, playname, transactionType, transactionID, currency, amount, gameId, roundId, time, remark)

                i = 0
                while playname[i].isalpha():
                    i += 1
                while playname[i].isnumeric():
                    i += 1
            
                username = playname[i:]

                try:

                    user = CustomUser.objects.get(username = username)
                    balance = user.main_wallet
                    Status = status.HTTP_200_OK
                    ResponseCode = 'OK'

                except:
                    Status = status.HTTP_400_BAD_REQUEST
                    ResponseCode = 'INVALID_DATA'

                # GameRequestsModel.objects.create(
                #     sessionToken     = sessionToken, 
                #     MemberID         = username, 
                #     TransType        =  transactionType, 
                #     transactionID    = transactionType, 
                #     currency         = transactionType, 
                #     amount           = amount, 
                #     gameId           = gameId, 
                #     roundId          = roundId, 
                #     time             = time, 
                #     remark           = remark,
                # )

            except:

                Status = status.HTTP_400_BAD_REQUEST
                ResponseCode = 'INVALID_DATA'


        response_data = '''<?xml version=”1.0” encoding=”UTF-8” standalone=”yes”?><TransferResponse><ResponseCode>{}</ResponseCode><Balance>{}</Balance></TransferResponse>'''.format(ResponseCode, balance)

        return Response(response_data, status=Status)