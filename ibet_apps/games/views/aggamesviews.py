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

class CheckOrCreateGameAccout(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        username =  request.POST['username']
        password = request.POST['password']
        oddtype = request.POST['oddtype']
        actype = request.POST['actype']
        cur = request.POST['cur']
        try:
            user = CustomUser.objects.get(username=username)
            s = "cagent=" + AG_CAGENT + "/\\\\/" + "loginname=" + username + "/\\\\/" + "method=lg/\\\\/" + "actype=" + actype + "/\\\\/" + "password=" + password + "/\\\\/" + "oddtype=" + oddtype + "/\\\\/" + "cur=" + cur  
            
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

class GetBalance(APIView):
    permission_classes = (AllowAny, )
    def post(self, request, *args, **kwargs):
        username =  request.POST['username']
        password = request.POST['password']
        oddtype = request.POST['oddtype']
        actype = request.POST['actype']
        cur = request.POST['cur']
        try:
            user = CustomUser.objects.get(username=username)
            s = "cagent=" + AG_CAGENT + "/\\\\/" + "loginname=" + username + "/\\\\/" + "method=gb/\\\\/" + "actype=" + actype + "/\\\\/" + "password=" + password + "/\\\\/" + "oddtype=" + oddtype + "/\\\\/" + "cur=" + cur  
            
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


class PrepareTransferCredit(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        
        username =  request.POST['username']
        password = request.POST['password']
        actype = request.POST['actype']
        cur = request.POST['cur']
        agtype = request.POST['type']
        # fixcredit = request.POST['fixcredit']
        gameCategory = request.POST['gameCategory']
        credit = request.POST['credit']
        try:
            user = CustomUser.objects.get(username=username)
            billno = AG_CAGENT + str(random.randint(0, 10000000))
            s = "cagent=" + AG_CAGENT + "/\\\\/" + "loginname=" + username + "/\\\\/" + "method=tc/\\\\/" + "billno=" + billno +  "/\\\\/" + "type=" + agtype + "/\\\\/" + "credit=" + credit + "/\\\\/" + "actype=" + actype + "/\\\\/" + "password=" + password + "/\\\\/" +  "gameCategory=" + gameCategory + "/\\\\/" + "cur=" + cur  
            print(s)
            param = des_encrypt(s,AG_DES).decode("utf-8") 
            print(param)
            key = MD5(param + AG_MD5)
            print(key)
            r = requests.get(AG_URL ,  params={
                    "params": param,
                    "key": key,  
                })
            rdata = r.text
            print(rdata)
            if r.status_code == 200:
                tree = ET.fromstring(rdata)
                info = tree.get('info')
                msg =  tree.get('msg')
                return Response({'info': info, 'msg': msg})
            else:
                return Response({"error":"The request is failed"}) 
        except ObjectDoesNotExist:
            return Response({"error":"The user is not existed."}) 
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