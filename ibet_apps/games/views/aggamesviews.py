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
from pyDes import des, ECB, PAD_PKCS5
import base64, hashlib
import ftplib
from io import BytesIO
import re
import xmltodict
import datetime
from datetime import date
from utils.aws_helper import writeToS3
from utils.admin_helper import *
import boto3
import logging
from utils.redisClient import RedisClient
from utils.redisHelper import RedisHelper
import games.ftp.ftp_client as ftpClient

logger = logging.getLogger('django')
AG_SUCCESS = 0
AG_FAIL = 1
AG_INVALID = 2
AG_NETWORK_ERROR = 3
AG_ERROR = 4

def des_encrypt(s, encrypt_key):
    iv = encrypt_key
    k = des(encrypt_key, ECB, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return base64.b64encode(en)

def MD5(code):
    res = hashlib.md5(code.encode()).hexdigest()
    return res

@api_view(['POST'])
@permission_classes((AllowAny,))        
def agftp(request): 

    try:
        ftp = ftpClient.agFtpConnect()
        
        try:
            r = RedisClient().connect()
            redis = RedisHelper()
        except:
            logger.critical("(FATAL_ERROR)There is something wrong with AG redis connection.")
            return HttpResponse({'status': 'There is something wrong with AG redis connection.'}, status=status.HTTP_400_BAD_REQUEST)


        try:
            folders = ftp.ftp_session.nlst()
            
        except ftplib.error_perm as resp:
            if str(resp) == "550 No files found":
                logger.error("No files in this directory of AG folders")
                return HttpResponse(ERROR_CODE_NOT_FOUND, status=status.HTTP_404_NOT_FOUND) 
            else:
                raise
        for folder in folders:
            ftp.ftp_session.cwd(folder) 

            small_folders = ftp.ftp_session.nlst()
            
            for sf in small_folders:
                ftp.ftp_session.cwd(sf) 
                try:
                    files = ftp.ftp_session.nlst()
                except ftplib.error_perm as resp:
                    if str(resp) == "550 No files found":
                        logger.error("No files in this directory of AG small folders")
                        return HttpResponse(ERROR_CODE_NOT_FOUND, status=status.HTTP_404_NOT_FOUND) 
                    else:
                        raise
                
                latest_time = None
                latest_name = None
                for file in files:
                    

                    if redis.check_ag_added_file(file) is False:   #if the file does not exist in redis
                        redis.set_ag_added_file(file)              #then add the file into redis
                    else:
                        continue                                   #if it is already existed then go to next index

                    time = ftp.ftp_session.voidcmd("MDTM " + file)
                    if (latest_time is None) or (time > latest_time):
                        latest_name = file
                        latest_time = time

                    
                    r = BytesIO()
                    read = ftp.ftp_session.retrbinary('RETR ' + latest_name, r.write)
                    rdata = r.getvalue().decode("utf-8")
                    xml = '<root>'+rdata+'</root>'

                    writeToS3(rdata, AWS_S3_ADMIN_BUCKET, 'AG-game-history/{}'.format(latest_name))
                    
                    root = ET.fromstring(xml)
                    for child in root:
                        dataType = child.attrib['dataType']
                        
                        if dataType == 'HSR': #捕鱼王場景的下注记录
                            playerName = child.attrib['playerName']
                            tradeNo = child.attrib['tradeNo']
                            transferAmount = child.attrib['transferAmount']
                            flag = child.attrib['flag']
                            SceneStartTime = child.attrib['SceneStartTime']
                            SceneEndTime = child.attrib['SceneEndTime']
                            netAmount = child.attrib['netAmount']
                            gameType = child.attrib['gameType']
                            sceneId = child.attrib['sceneId']
                            agtype = child.attrib['type']
                            Roomid =child.attrib['Roomid']
                            Roombet =child.attrib['Roombet']
                            Cost =child.attrib['Cost']
                            Earn =child.attrib['Earn']
                            exchangeRate =child.attrib['exchangeRate']
                            creationTime = child.attrib['creationTime']
                            deviceType = child.attrib['deviceType']
                            gameCode = child.attrib['gameCode']

                            try:
                                user = CustomUser.objects.get(username=playerName)
                                
                            except ObjectDoesNotExist:
                                logger.error("This user does not exist in AG ftp.")
                                return HttpResponse(ERROR_CODE_INVALID_INFO,status=status.HTTP_406_NOT_ACCEPTABLE) 

                            trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

                            GameBet.objects.create(provider=GameProvider.objects.get(provider_name=AG_PROVIDER),
                                                    category=Category.objects.get(name='Live Casino'),
                                                    user=user,
                                                    user_name=user.username,
                                                    transaction_id=trans_id,
                                                    amount_wagered=transferAmount,
                                                    currency=user.currency,
                                                    amount_won=transferAmount,
                                                    ref_no=tradeNo,
                                                    market=ibetCN,
                                                    bet_time=utcToLocalDatetime(SceneStartTime),
                                                    resolved_time=utcToLocalDatetime(SceneEndTime),
                                                    other_data={
                                                            "sceneId": sceneId,
                                                            "type": agtype,
                                                            "Roomid": Roomid,
                                                            "Roombet": Roombet,
                                                            "Cost": Cost,
                                                            "Earn": Earn,
                                                            "exchangeRate": exchangeRate,
                                                            "creationTime": creationTime,
                                                            "deviceType": deviceType,
                                                            "gameCode": gameCode,
                                                            "flag": flag,
                                                            'netAmount': netAmount
                                                        }
                                                    )
                            

                            
                        elif dataType == 'BR': #下注记录详情
                            playerName = child.attrib['playerName']
                            billNo = child.attrib['billNo']
                            betAmount = child.attrib['betAmount']
                            flag = child.attrib['flag']
                            betTime = child.attrib['betTime']
                            gameCode = child.attrib['gameCode']
                            netAmount = child.attrib['netAmount']
                            gameType = child.attrib['gameType']
                            result = child.attrib['result']
                            agentCode = child.attrib['agentCode']
                            playType = child.attrib['playType']
                            tableCode = child.attrib['tableCode']
                            recalcuTime = child.attrib['recalcuTime']
                            platformType = child.attrib['platformType']
                            aground = child.attrib['round']
                            beforeCredit = child.attrib['beforeCredit']
                            deviceType = child.attrib['deviceType']

                            try:
                                user = CustomUser.objects.get(username=playerName)
                                
                            except ObjectDoesNotExist:
                                logger.error("This user does not exist in AG ftp.")
                                return HttpResponse(ERROR_CODE_INVALID_INFO,status=status.HTTP_406_NOT_ACCEPTABLE) 

                            trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

                            GameBet.objects.create(provider=GameProvider.objects.get(provider_name=AG_PROVIDER),
                                                    category=Category.objects.get(name='Live Casino'),
                                                    user=user,
                                                    user_name=user.username,
                                                    transaction_id=trans_id,
                                                    amount_wagered=betAmount,
                                                    currency=user.currency,
                                                    amount_won=netAmount,
                                                    ref_no=billNo,
                                                    market=ibetCN,
                                                    resolved_time=timezone.now(),
                                                    other_data={
                                                            "agentCode": child.attrib['agentCode'],
                                                            "gameCode": gameCode,
                                                            "betTime": betTime,
                                                            "gameType": gameType,
                                                            "flag": flag,
                                                            "playType": playType,
                                                            "tableCode": tableCode,
                                                            "recalcuTime": recalcuTime,
                                                            "platformType": platformType,
                                                            "round": aground,
                                                            "beforeCredit": beforeCredit,
                                                            "deviceType": deviceType,
                                                        }
                                                    )

                        elif dataType == 'EBR': #电子游戏的下注记录
                            playerName = child.attrib['playerName']
                            billNo = child.attrib['billNo']
                            betAmount = child.attrib['betAmount']
                            flag = child.attrib['flag']
                            betTime = child.attrib['betTime']
                            gameCode = child.attrib['gameCode']
                            netAmount = child.attrib['netAmount']
                            gameType = child.attrib['gameType']
                            result = child.attrib['result']
                            slottype = child.attrib['slottype']
                            mainbillno = child.attrib['mainbillno']
                            subbillno = child.attrib['subbillno']
                            gameCategory = child.attrib['gameCategory']
                            netAmountBonus = child.attrib['netAmountBonus']
                            netAmountBase = child.attrib['netAmountBase']
                            betAmountBonus = child.attrib['betAmountBonus']
                            betAmountBase = child.attrib['betAmountBase']

                            try:
                                user = CustomUser.objects.get(username=playerName)
                                
                            except ObjectDoesNotExist:
                                logger.error("This user does not exist in AG ftp.")
                                return HttpResponse(ERROR_CODE_INVALID_INFO,status=status.HTTP_406_NOT_ACCEPTABLE) 

                            trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

                            GameBet.objects.create(provider=GameProvider.objects.get(provider_name=AG_PROVIDER),
                                                    category=Category.objects.get(name='Live Casino'),
                                                    user=user,
                                                    user_name=user.username,
                                                    transaction_id=trans_id,
                                                    amount_wagered=betAmount,
                                                    currency=user.currency,
                                                    amount_won=netAmount,
                                                    ref_no=billNo,
                                                    market=ibetCN,
                                                    resolved_time=timezone.now(),
                                                    other_data={
                                                            "gameType": gameType,
                                                            "result": result,
                                                            "slottype": slottype,
                                                            "mainbillno":mainbillno,
                                                            "subbillno": subbillno,
                                                            "gameCategory": gameCategory,
                                                            "netAmountBonus": netAmountBonus,
                                                            "netAmountBase":netAmountBase,
                                                            "betAmountBonus": betAmountBonus,
                                                            "betAmountBase": betAmountBase
                                                        }
                                                    )
                ftp.ftp_session.cwd('..')
            ftp.ftp_session.cwd('..')
        ftp.ftp_session.quit()
        return HttpResponse(CODE_SUCCESS, status=status.HTTP_200_OK)
    except ftplib.error_temp:
        logger.critical("(FATAL_ERROR)Cannot connect with AG ftp.")
        return HttpResponse(ERROR_CODE_FAIL, status=status.HTTP_400_BAD_REQUEST)

def checkCreateGameAccoutOrGetBalance(user,password,method,oddtype,actype,cur):
    
    s = "cagent=" + AG_CAGENT + "/\\\\/" + "loginname=" + user.username + "/\\\\/" + "method=" + method + "/\\\\/" + "actype=" + actype + "/\\\\/" + "password=" + password + "/\\\\/" + "oddtype=" + oddtype + "/\\\\/" + "cur=" + cur  
    # print(s)
    param = des_encrypt(s,AG_DES).decode("utf-8") 

    key = MD5(param + AG_MD5)
    r = requests.get(AG_URL ,  params={
            "params": param,
            "key": key,  
        })
    rdata = r.text
    #print(rdata)
    if r.status_code == 200:
        tree = ET.fromstring(rdata)
        info = tree.get('info')   
        msg =  tree.get('msg')
        if info == '0' or msg == '':
            return AG_SUCCESS
        else:
            return AG_FAIL
    else:
        return AG_FAIL
    


    
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
        logger.critical("The user does not exist in AG getBalance api.")
        return Response({"error":"The user does not exist in AG getBalance api."}) 


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
            return AG_SUCCESS
        else:
            return AG_FAIL
        
    else:
        return AG_FAIL
    


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
            return AG_SUCCESS
        elif info == '1': #失败, 订单未处理状态
            return AG_FAIL
        elif info == '2': #因无效的转账金额引致的失败
            return AG_INVALID
        
    else:
        return AG_FAIL
    


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
            return AG_SUCCESS
        elif info == '1':
            return AG_FAIL
        elif info == '2':
            return AG_INVALID
        elif info == 'network_error':
            return AG_NETWORK_ERROR    
    else:
        return AG_ERROR

#check or create game account and login to game lobby
@api_view(['POST'])
@permission_classes((AllowAny,))        
def forwardGame(request):
    username =  request.POST['username']
    password = AG_CAGENT + username
    actype = request.POST['actype']  #actype=1 代表真钱账号,0 代表试玩账号
    billno = AG_CAGENT + strftime("%Y%m%d%H%M%S", gmtime())
    gameType = request.POST['gameType']
    oddtype = 'A'
    lg_method = 'lg'
    sid = AG_CAGENT + strftime("%Y%m%d%H%M%S", gmtime()) + str(random.randint(0, 10000000))
    try:
        user = CustomUser.objects.get(username=username)
        if user.currency == CURRENCY_CNY:
            cur = "CNY"
        elif user.currency == CURRENCY_USD:
            cur = "USD"
        elif user.currency == CURRENCY_THB:
            cur = "THB"
        elif user.currency == CURRENCY_EUR:
            cur = "EUR"
        elif user.currency == CURRENCY_IDR:
            cur = "IDR"
        elif user.currency == CURRENCY_VND:
            cur = "VND"
        else:
            cur = "CNY"

        if user.language == 'English':
            lang = '3'
        elif user.language == 'Chinese':
            lang = '1'
        elif user.language == 'Thai':
            lang = '6'
        elif user.language == 'Vietnamese':
            lang = '8'
        elif user.language == 'en':
            lang = '3'
        elif user.language == 'zh':
            lang = '1'
        elif user.language == 'Th':
            lang = '6'
        elif user.language == 'Vi':
            lang = '8'   
        else:
            lang = '1'
            
        if checkCreateGameAccoutOrGetBalance(user, password, lg_method, oddtype, actype, cur) == AG_SUCCESS:
            s = "cagent=" + AG_CAGENT + "/\\\\/" + "loginname=" + username + "/\\\\/" + "dm=" + AG_DM + "/\\\\/" + "sid=" + sid + "/\\\\/" + "lang=" + lang + "/\\\\/" + "gameType=" + gameType +  "/\\\\/" + "oddtype=" + oddtype +  "/\\\\/" +  "actype=" + actype + "/\\\\/"  +  "password=" + password + "/\\\\/" +   "cur=" + cur  
            
            param = des_encrypt(s,AG_DES).decode("utf-8") 
            
            key = MD5(param + AG_MD5)
            
            
            # r = requests.get(AG_FORWARD_URL ,  data={
            #         "params": param,
            #         "key": key,  
            #     })
            # rdata = r.text
            return Response({"url": AG_FORWARD_URL + '?params=' + param + '&key=' + key})
        else:
            logger.error("Cannot check or create AG game account in AG forwardGame.")
            return Response({"error": "Cannot check or create AG game account in AG forwardGame."})
        
        
    except ObjectDoesNotExist:
        logger.error("The user does not exist in AG forwardGame.")
        return Response({"error":"The  user does not exist in AG forwardGame."}) 


def agFundTransfer(user, fund_wallet, credit, agtype): 
        username =  user.username
        trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))  
        password = AG_CAGENT + username
           
        oddtype = 'A'
        actype = '1'

        if user.currency == CURRENCY_CNY:
            cur = "CNY"
        elif user.currency == CURRENCY_USD:
            cur = "USD"
        elif user.currency == CURRENCY_THB:
            cur = "THB"
        elif user.currency == CURRENCY_EUR:
            cur = "EUR"
        elif user.currency == CURRENCY_IDR:
            cur = "IDR"
        elif user.currency == CURRENCY_VND:
            cur = "VND"
        else:
            cur = "CNY"

        # agtype = request.POST['agtype']
        gameCategory = ""
        # credit = request.POST['credit']
        fixcredit = ""
        billno = AG_CAGENT + strftime("%Y%m%d%H%M%S", gmtime())
        lg_method = 'lg'
        gb_method = 'gb'
        success = True
        confirm = True
        checking = True
        if checkCreateGameAccoutOrGetBalance(user, password, lg_method, oddtype, actype, cur) == AG_SUCCESS: #check or create game account
            while success:
                if checkCreateGameAccoutOrGetBalance(user, password, gb_method, oddtype, actype, cur) == AG_SUCCESS: #get balance
                    if prepareTransferCredit(user, password, actype, cur, agtype, gameCategory, credit, fixcredit, billno) == AG_SUCCESS:
                        # print("prepare")
                        
                        while confirm:
                            flag = '1'
                            if transferCreditConfirm(user,password,actype,cur,agtype,fixcredit,gameCategory,credit,flag,billno) == AG_SUCCESS:
                                if agtype == 'IN':
                                    Transaction.objects.create(transaction_id=trans_id,
                                        user_id=user,
                                        order_id=trans_id,
                                        amount=credit,
                                        currency=user.currency,
                                        transfer_from=fund_wallet,
                                        transfer_to='AG',
                                        product=GAME_TYPE_LIVE_CASINO,
                                        transaction_type=TRANSACTION_TRANSFER,
                                        channel=None,
                                        status=TRAN_SUCCESS_TYPE)
                                else:
                                    Transaction.objects.create(transaction_id=trans_id,
                                        user_id=user,
                                        order_id=trans_id,
                                        amount=credit,
                                        currency=user.currency,
                                        transfer_from='AG',
                                        transfer_to=fund_wallet,
                                        product=GAME_TYPE_LIVE_CASINO,
                                        channel=None,
                                        transaction_type=TRANSACTION_TRANSFER,
                                        status=TRAN_SUCCESS_TYPE)
                                # print("confirm")
                                success = False
                                confirm = False
                                return CODE_SUCCESS
                                break
                                   
                            else:
                                while checking:
                                    if queryOrderStatus(actype,cur,billno) == AG_SUCCESS:
                                        # print("query")
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
                                                product=GAME_TYPE_LIVE_CASINO,
                                                channel=None,
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
                                                product=GAME_TYPE_LIVE_CASINO,
                                                channel=None,
                                                transaction_type=TRANSACTION_TRANSFER,
                                                status=TRAN_SUCCESS_TYPE)
                                        return CODE_SUCCESS
                                        break
                                    elif queryOrderStatus(actype,cur,billno) == AG_FAIL:  
                                        success = True
                                        confirm = True
                                        checking = False
                                        
                                    elif queryOrderStatus(actype,cur,billno) == AG_NETWORK_ERROR:  
                                        checking = True       
                                        time.sleep(5)
                                        
                                    elif queryOrderStatus(actype,cur,billno) == AG_INVALID: 
                                        success = True
                                        confirm = False
                                        checking = False
                                        time.sleep(5)
                                        

                    else:
                        success = False
                        logger.error("Cannot prepare transfer credit for AG game account agFundTransfer.")
                        return Response({"error": "Cannot prepare transfer credit for AG game account agFundTransfer."})
                        break
                else:
                    success = False
                    logger.error("Cannot get balance for AG game account agFundTransfer.")
                    return Response({"error": "Cannot get balance for AG game account agFundTransfer."})
                    break
        else:
            logger.error("Cannot check or create AG game account agFundTransfer.")
            return Response({"error": "Cannot check or create AG game account agFundTransfer."})

class test(APIView):
    permission_classes = (AllowAny, )
    def get(self, request, *args, **kwargs):
        user = CustomUser.objects.get(username="angela03")
        response = fundTransfer(user, "main", "300.00",  "IN")
        
        return HttpResponse(response)

def agService(request):
    if request.method == "GET":
        
        username = request.GET.get("id")
        ag_type = request.GET.get("type")
        stamp = request.GET.get("stamp")
        feature = request.GET.get("feature")
        try:
            user = CustomUser.objects.get(username=username)
            if feature == MD5(username + ag_type + stamp + AG_MD5):
                return HttpResponse("Success")
            else:
                logger.error("error, invalid invoking agService api")
                return HttpResponse("error, invalid invoking api")
        except:
            logger.error("this user does not exist in AG agService.")
            return HttpResponse("error, this user does not exist in AG agService.")

