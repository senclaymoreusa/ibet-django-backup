from django.shortcuts import render
from django.http import HttpResponse
from django.views import View, generic
from users.models import CustomUser
from ..models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from utils.constants import *
from djauth.third_party_keys import *
from rest_framework import generics
from ..serializers import asiapayDepositSerialize, asiapayCashoutSerialize
from django.conf import settings
import requests,json
import logging
import time
import struct
import hashlib 
import xml.etree.ElementTree as ET
from time import sleep
from des import DesKey
import base64
from time import gmtime, strftime

bankidConversion = {
    '1':'工商银行',
    '2':'建设银行',
    '3':'农业银行',
    '4':'招商银行',
    '6':'广发银行',
    '7':'中国银行',
    '9':'中国邮政储蓄银行',
    '10':'中信银行',
    '11':'光大银行',
    '12':'民生银行',
    '16':'兴业银行',
    '17':'华夏银行',
    '23':'平安银行',
    '38':'微信支付',
    '39':'快捷支付',
    '41':'支付宝',
    '49':'京东支付',
    '201': '比特币',
}

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def MD5(code):
    res = hashlib.md5(code.encode()).hexdigest()
    return res

def encryptDES(encryptString,encryptKey,myIv):
    msg = encryptKey.encrypt(encryptString.encode(), initial=myIv, padding=True)
    signKey = base64.b64encode(msg).decode("utf-8") 
    return signKey
 
def Create_RandomKey(r1, key, r2):
    TPass = MD5(key).upper()
    TPass = MD5(r1 + TPass + r2).upper()
    TPass = TPass[15:23]
    return TPass

def CreateMsgStr(ParamList):
    print(ParamList.values())
    msgStr = ",".join(str(x) for x in ParamList.values())+ ","
    print("msgStr:" + msgStr)
    return msgStr

def decryptDES(decryptString, decryptKey, myIv):
    byteMi = base64.b64decode(decryptString)
    msg = decryptKey.decrypt(byteMi, initial=myIv, padding=True).decode("utf-8") 
    return msg


eString = ASIAPAY_R1 + "," + ASIAPAY_CID + "," + ASIAPAY_R2
myIv = bytearray(b'\x32\xCD\x13\x58\x21\xAB\xBC\xEF')
class submitDeposit(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = asiapayDepositSerialize
    permission_classes = [AllowAny, ]
    def post(self, request, *args, **kwargs):
       
        userid = self.request.POST.get("userid")
        uID = "n" + userid
        UserIP= get_client_ip(request)
        TraceID = strftime("%Y%m%d%H%M%S", gmtime())
        OrderID = 'D' + "ibet" +strftime("%Y%m%d%H%M%S", gmtime())
        NoticeUrl = ""
        BankID = self.request.POST.get("method")
        PayWay = self.request.POST.get("PayWay")
        DesTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        amount = self.request.POST.get("amount")
        SignCode = str(uID)+ ASIAPAY_CID + UserIP + TraceID + OrderID + NoticeUrl + DesTime + ASIAPAY_DEPOSITKEY
        user =  CustomUser.objects.get(pk=userid)
        currency = self.request.POST.get("currency")
        print(SignCode)
        print(MD5(SignCode))
        ParamList_Msg ={
            "rStr" : "",
            "TraceID" : TraceID,
            "C_OrderID": OrderID,
            "cID": ASIAPAY_CID,
            "uID": uID,
            "UserIP": UserIP,
            "C_DesTime": DesTime,
            "NoticeUrl": "",
            "SingCode": MD5(SignCode),
            "BankID": BankID,
            "PayWay": PayWay,
            "PayType": 0,
            "PayCardPro": "",
            "PayCardCity": "",
            "PayCardUserChName": user.last_name + user.first_name,
            "PayMoney": amount,
            "ResType": "xml",
            "C_RealName": user.last_name + user.first_name,
            "UserRealID": "",
            "SafeLevel": "0",
            "ProcessLevel": "0",
            "tempparam" : "",
            "tempparam1" : "",
            "tempparam2" : "",
            "tempparam3" : "",
            "tempparam4" : "",
            "tempparam5" : "",
            "tempparam6" : "",
            "tempparam7" : "",
            "tempparam8" : "",
        }
        delay = kwargs.get("delay", 5)
        sign_encryptKey = DesKey(ASIAPAY_UNITEKEY.encode())
        msg_encryptKey = DesKey(Create_RandomKey(ASIAPAY_R1, ASIAPAY_KEY1,ASIAPAY_R2).encode())
        url = ASIAPAY_API_URL
        print(encryptDES(eString, sign_encryptKey, myIv))
        print(encryptDES(CreateMsgStr(ParamList_Msg), msg_encryptKey, myIv))
      
        r = requests.post(url + "/standard/getway/depositiface", data={
            'Sign': encryptDES(eString, sign_encryptKey, myIv),
            'Msg': encryptDES(CreateMsgStr(ParamList_Msg), msg_encryptKey, myIv),
            'TraceID': TraceID,
            'OrderID':OrderID,
            'cID':ASIAPAY_CID,
            'uID':uID,
            'UserIP':UserIP,
            'DesTime':DesTime,
            'BankID':BankID,
            'PayWay':PayWay,
            'PayType':0,
            'PayMoney':amount,
            'ResType':'xml',
            'RealName':user.last_name + user.first_name,
            'SafeLevel':0,
            'ProcessLevel':0,
            'SignCode':MD5(SignCode),
            'PayCardUserChName':user.last_name + user.first_name,
        })
        rdata = r.text
        print(rdata)
        if r.status_code == 200:
            tree = ET.fromstring(rdata)
            StatusCode = tree.find('StatusCode').text
            StatusMsg = tree.find('StatusMsg').text
            paymentAPIURL = tree.find('RedirectUrl').text
            paymentAPIURL = decryptDES(paymentAPIURL,msg_encryptKey, myIv)
            print(paymentAPIURL)
            if StatusMsg == 'OK':
                create = Transaction.objects.create(
                    order_id=OrderID,
                    amount=amount,
                    user_id=CustomUser.objects.get(pk=userid),
                    currency= int(currency),
                    transaction_type=0, 
                    channel=4,
                    status=2,
                    method=bankidConversion[BankID],
                )
                rr = requests.get(paymentAPIURL, params={
                        "cid":ASIAPAY_CID,
                        "oid":OrderID
                    })
                rrdata = rr.json()
                Response(rrdata)
            else:
                print("There was something wrong with the result")
        else:
            # Handle error
            print("There was something wrong with the result")
            print(rdata)
            return Response(rdata)
        return Response(rrdata)


class submitCashout(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = asiapayCashoutSerialize
    permission_classes = [AllowAny, ]
    def post(self, request, *args, **kwargs):
       
        userid = self.request.POST.get("userid")
        uID = "n" + userid
        UserIP= get_client_ip(request)
        TraceID = strftime("%Y%m%d%H%M%S", gmtime())
        OrderID = 'D' + "ibet" +strftime("%Y%m%d%H%M%S", gmtime())
        NoticeUrl = ""
        BankID = self.request.POST.get("method")
        PayWay = self.request.POST.get("PayWay")
        DesTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        amount = self.request.POST.get("amount")
        SignCode = str(uID)+ ASIAPAY_CID + UserIP + TraceID + OrderID + NoticeUrl + DesTime + ASIAPAY_DEPOSITKEY
        user =  CustomUser.objects.get(pk=userid)
        currency = self.request.POST.get("currency")
        # print(SignCode)
        # print(MD5(SignCode))
        ParamList_Msg ={
            "rStr" : "",
            "cID": ASIAPAY_CID,
            "uID": "ntest001",
            "cPass": ASIAPAY_CPASS,
            "TraceID" : "2148923489",
            "OrderID": "W" + "111231234564",
            "CashMoney":"10",
            "CashBankName":"BTC",
            "CashCardNumber":"6222022000000000000",
            "CashCardChName":"务必填写真实姓名",
            "CashBankPro":"",
            "CashBankCity":"",
            "CashBankDetailName":"北京支行",
            "UserIP": "127.0.0.1",
            "NoticeUrl": "",
            "DesTime": "2019-06-21 10:00:",
            "SingCode": MD5(SignCode),
            "CashMobile": "",
            "CashType":"1",
            "SafeLevel": "0",
            "RealID": "",
            "ResType": "xml",
            "tempparam" : "",
            "tempparam1" : "",
            "tempparam2" : "",
            "tempparam3" : "",
            "tempparam4" : "",
            "tempparam5" : "",
        }
        delay = kwargs.get("delay", 5)
        sign_encryptKey = DesKey(ASIAPAY_UNITEKEY.encode())
        msg_encryptKey = DesKey(Create_RandomKey(ASIAPAY_R1, ASIAPAY_KEY1,ASIAPAY_R2).encode())
        url = ASIAPAY_API_URL
        print("sign:" + encryptDES(eString, sign_encryptKey, myIv))
        print("msg:" + encryptDES(CreateMsgStr(ParamList_Msg), msg_encryptKey, myIv))
        for x in range(3):   
            r = requests.post(url + "/standard/getway/depositiface", data={
                'rStr':'',
                'Sign': encryptDES(eString, sign_encryptKey, myIv),
                'Msg': encryptDES(CreateMsgStr(ParamList_Msg), msg_encryptKey, myIv),
                'TraceID': "2148923489",
                'OrderID':"W" + "111231234564",
                'cID':ASIAPAY_CID,
                'uID':"ntest001",
                'cPass': ASIAPAY_CPASS,
                'UserIP':"127.0.0.1",
                'DesTime':"2019-06-21 10:00:",
                'CashCardNumber':'6222022000000000000',
                'CashCardChName':'务必填写真实姓名',
                'CashBankPro':'CashBankPro',
                'CashBankName':'BTC',
                'CashBankCity':'',
                'CashBankDetailName':'北京支行',
                'NoticeUrl':'',
                'CashMoney':'10',
                'CashMobile':'',
                'CashType':'1',
                'RealID':'',
                'ResType':'xml',
                'SafeLevel':0,
                'SignCode':MD5(SignCode),
                'tempparam':''
            })
            rdata = r.text
            print(rdata)
            if r.status_code == 201:
                break
            elif r.status_code == 500:
                print("Request failed {} time(s)'.format(x+1)")
                print("Waiting for %s seconds before retrying again")
                sleep(delay)
            elif r.status_code == 400:
                # Handle error
                print("There was something wrong with the result")
                print(rdata)
                return Response(rdata)
        tree = ET.fromstring(rdata)
        StatusCode = tree.find('StatusCode').text
        StatusMsg = tree.find('StatusMsg').text
        print(StatusMsg)
        if StatusCode == '100503' or StatusMsg == 'OK':
            create = Transaction.objects.create(
                order_id=OrderID,
                amount=amount,
                user_id=CustomUser.objects.get(pk=userid),
                currency= int(currency),
                transaction_type=0, 
                channel=4,
                status=2,
                method=bankidConversion[BankID],
            )
        else:
            print(StatusMsg)
        return Response(rdata)



