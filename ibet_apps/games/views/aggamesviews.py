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
            return Response({"error": "Cannot check or create AG game account."})
        
        
    except ObjectDoesNotExist:
        return Response({"error":"The  user is not existed."}) 


def agFundTransfer(user, fund_wallet, credit, agtype): 
        username =  user.username
        trans_id = username + strftime("%Y%m%d%H%M%S", gmtime())+str(random.randint(0,10000000))
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
                return HttpResponse("error, invalid invoking api")
        except:
            logger.error("this user is not existed.")

