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
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer
from utils.constants import *
#from djauth.third_party_keys import *
from rest_framework import generics
from ..serializers import asiapayDepositSerialize, asiapayCashoutSerialize,asiapayDepositFinishSerialize,asiapayOrderStatusFinishSerialize,asiapayExchangeRateFinishSerialize,asiapayDepositArriveSerialize
from django.conf import settings
import requests,json
import logging
import time,datetime
import struct
import hashlib 
import xml.etree.ElementTree as ET
from time import sleep
from des import DesKey
import base64
from time import gmtime, strftime, strptime

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
url = ASIAPAY_API_URL
class submitDeposit(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = asiapayDepositSerialize
    permission_classes = [AllowAny, ]
    def post(self, request, *args, **kwargs):
       
        userid = self.request.POST.get("userid")
        uID = "n" + userid
        # uID = "nTEST2"
        UserIP= get_client_ip(request)
        TraceID = strftime("%Y%m%d%H%M%S", gmtime())
        OrderID =  "ibet" +strftime("%Y%m%d%H%M%S", gmtime())
        NoticeUrl = ""
        BankID = self.request.POST.get("method")
        PayWay = self.request.POST.get("PayWay")
        DesTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        amount = self.request.POST.get("amount")
        SignCode = str(uID)+ ASIAPAY_CID + UserIP + TraceID + OrderID + NoticeUrl + DesTime + ASIAPAY_DEPOSITKEY
        #user =  CustomUser.objects.get(pk=userid)
        currency = self.request.POST.get("currency")
        print(SignCode)
        print(MD5(SignCode))
        ParamList_Msg ={
            "rStr" : "",
            "TraceID" : TraceID,
            "C_OrderID": 'D' + OrderID,
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
            # "PayCardUserChName": user.last_name + user.first_name,
            "PayCardUserChName": "测试",
            "PayMoney": amount,
            "ResType": "xml",
            "C_RealName": "测试",
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
        print(encryptDES(eString, sign_encryptKey, myIv))
        print(encryptDES(CreateMsgStr(ParamList_Msg), msg_encryptKey, myIv))
      
        r = requests.post(url + "/standard/getway/depositiface", data={
            'Sign': encryptDES(eString, sign_encryptKey, myIv),
            'Msg': encryptDES(CreateMsgStr(ParamList_Msg), msg_encryptKey, myIv),
            'TraceID': TraceID,
            'OrderID':'D' + OrderID,
            'cID':ASIAPAY_CID,
            'uID':uID,
            'UserIP':UserIP,
            'DesTime':DesTime,
            'BankID':BankID,
            'PayWay':PayWay,
            'PayType':0,
            'PayMoney':amount,
            'ResType':'xml',
            'RealName':"测试",
            'SafeLevel':0,
            'ProcessLevel':0,
            'SignCode':MD5(SignCode),
            'PayCardUserChName':"测试",
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
                rrdata = rr.text
                print(rrdata)
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
        OrderID =  "ibet" +strftime("%Y%m%d%H%M%S", gmtime())
        NoticeUrl = ""
        #BankID = self.request.POST.get("method")
        PayWay = self.request.POST.get("PayWay")
        DesTime = "2019-06-21 10:00:00"
        #strftime("%Y-%m-%d %H:%M:%S", gmtime())
        amount = self.request.POST.get("amount")
        CashBankName =""
        CashCardNumber = "6222022000000000000"
        CashCardChName = "务必填写真实姓名"
        CashBankPro = ""
        CashBankCity = ""
        CashBankDetailName = "北京支行"
        SignCode = str(uID)+ ASIAPAY_CID + ASIAPAY_CPASS + amount+ CashBankName+ CashCardNumber+ CashCardChName+CashBankPro+CashBankCity+CashBankDetailName+ UserIP + TraceID + "W" + OrderID + NoticeUrl + DesTime + ASIAPAY_CASHKEY
        print(SignCode)
        user =  CustomUser.objects.get(pk=userid)
        currency = self.request.POST.get("currency")
        cashoutMethod = self.request.POST.get("cashoutMethod")
        # print(SignCode)
        # print(MD5(SignCode))
        ParamList_Msg ={
            "rStr" : "",
            "cID": ASIAPAY_CID,
            "uID": uID,
            "cPass": ASIAPAY_CPASS,
            "TraceID" : TraceID,
            "OrderID": "W" + OrderID,
            "CashMoney":amount,
            "CashBankName":CashBankName,
            "CashCardNumber":CashCardNumber,
            "CashCardChName":CashCardChName,
            "CashBankPro":CashBankPro,
            "CashBankCity":CashBankCity,
            "CashBankDetailName":CashBankDetailName,
            "UserIP": UserIP,
            "NoticeUrl": "",
            "DesTime": "2019-06-21 10:00:00",
            "SignCode": MD5(SignCode),
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
            "tempparam6" : "",
            "tempparam7" : "",
        }
        delay = kwargs.get("delay", 5)
        sign_encryptKey = DesKey(ASIAPAY_UNITEKEY.encode())
        msg_encryptKey = DesKey(Create_RandomKey(ASIAPAY_R1, ASIAPAY_KEY1,ASIAPAY_R2).encode())
        print("sign:" + encryptDES(eString, sign_encryptKey, myIv))
        print("msg:" + encryptDES(CreateMsgStr(ParamList_Msg), msg_encryptKey, myIv))
        r = requests.post(url + "/standard/getway/" + cashoutMethod, data={
            'rStr':'',
            'Sign': encryptDES(eString, sign_encryptKey, myIv),
            'Msg': encryptDES(CreateMsgStr(ParamList_Msg), msg_encryptKey, myIv),
            'TraceID': TraceID,
            'OrderID':"W" + OrderID,
            'cID':ASIAPAY_CID,
            'uID':uID,
            'cPass': ASIAPAY_CPASS,
            'UserIP':UserIP,
            'DesTime':"2019-06-21 10:00:",
            'CashCardNumber':CashCardNumber,
            'CashCardChName':CashCardChName,
            'CashBankPro':CashBankPro,
            'CashBankName':CashBankName,
            'CashBankCity':CashBankCity,
            'CashBankDetailName':CashBankDetailName,
            'NoticeUrl':'',
            'CashMoney':amount,
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
        tree = ET.fromstring(rdata)
        StatusCode = tree.find('StatusCode').text
        StatusMsg = tree.find('StatusMsg').text
        print(StatusMsg)
        if StatusCode == '50001':
            create = Transaction.objects.create(
                order_id=OrderID,
                amount=amount,
                user_id=CustomUser.objects.get(pk=userid),
                currency= int(currency),
                transaction_type=1, 
                channel=4,
                status=2,
                method=cashoutMethod,
            )
        else:
            print(StatusMsg)
        
        return Response(rdata)

class depositfinish(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = asiapayDepositFinishSerialize
    permission_classes = [AllowAny, ]
    def post(self, request, *args, **kwargs):
        userid = self.request.POST.get("userid")
        OrderID = self.request.POST.get("order_id")
        uID = "n" + userid
        r = requests.post(url + '/standard/getway/depositfinish', data={
            "cID":ASIAPAY_CID,
            "uID":uID,
            "CmdType":"02",
            "OrderID":OrderID,
        })
        rdata = r.text
        tree = ET.fromstring(rdata)
        StatusCode = tree.find('StatusCode').text
        if StatusCode == "00001":
            orderData = Transaction.objects.get(user_id=CustomUser.objects.get(pk=userid),
            order_id=OrderID)
            orderData.status = 3
            orderData.save()
        else:
            print('The request information is nor correct, please try again')
        print(rdata)
        return Response(rdata)

class orderStatus(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = asiapayOrderStatusFinishSerialize
    permission_classes = [AllowAny, ]
    def post(self, request, *args, **kwargs):
        userid = self.request.POST.get("userid")
        OrderID = self.request.POST.get("order_id")
        CmdType = self.request.POST.get("CmdType")
        uID = "n" + userid
        r = requests.post(url + '/standard/getway/orderstatus', data={
            "cID":ASIAPAY_CID,
            "uID":uID,
            "CmdType": CmdType,
            "OrderID":OrderID,
        })
        rdata = r.text
        print(rdata)
        return Response(rdata)
class exchangeRate(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = asiapayExchangeRateFinishSerialize
    permission_classes = [AllowAny, ]
    def post(self, request, *args, **kwargs):
        Amount = self.request.POST.get("Amount")
        r = requests.post(url + '/standard/getway/ticker', data={
            "cID":ASIAPAY_CID,
            "ModeType":"BTC",
            "Amount": Amount,
        })
        rdata = r.json()
        print(rdata)
        return Response(rdata)
class depositArrive(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = asiapayDepositArriveSerialize
    permission_classes = [AllowAny, ]
    parser_classes = (XMLParser,)
    renderer_classes = (XMLRenderer,)
    def post(self, request, *args, **kwargs):
        StatusCode = self.request.POST.get("StatusCode")
        RevCardNumber = self.request.POST.get("RevCardNumber")
        RevMoney = self.request.POST.get("amount")
        order_id = self.request.POST.get("order_id")
        OrderID = order_id[1:]
        print(OrderID)
        uID = self.request.POST.get("uID")
        userid = uID.strip('n')
        print(userid)
        serializer = self.serializer_class(data=request.data)
        print(serializer)
        datetime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        print(serializer.is_valid())
        if serializer.is_valid() and StatusCode == '001':  
            saveData = Transaction.objects.get(user_id=userid, order_id=order_id) 
            saveData.status = 6
            saveData.save()
            root = ET.Element("ProcessStatus")
            tr1 = ET.SubElement(root, "StatusCode")
            tr1.text = "001"
            tr2 = ET.SubElement(root, "StatusMsg")
            tr2.text = "操作成功"
            tr3 = ET.SubElement(root, "ProcessTime")
            tr3.text = datetime
            sucessTree = ET.ElementTree(root) 

            return Response({"StatusCode": "003", "StatusMsg": "请再次发起通知", "ProcessTime": datetime},status=status.HTTP_200_OK)
        else:
            return HttpResponse(sucessTree, content_type = "application/xml",status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     return Response({"StatusCode": "003", "StatusMsg": "请再次发起通知", "ProcessTime": datetime}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







