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
from ..serializers import asiapayDepositSerialize
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
    msgStr = ",".join(str(x) for x in ParamList.values())
    print("msgStr:" + msgStr)
    return msgStr

class submitDeposit(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = asiapayDepositSerialize
    permission_classes = [AllowAny, ]
    def post(self, request, *args, **kwargs):
        serializer = asiapayDepositSerialize(self.queryset, many=True)
        eString = ASIAPAY_R1 + "," + ASIAPAY_CID + "," + ASIAPAY_R2
        myIv = bytearray(b'\x32\xCD\x13\x58\x21\xAB\xBC\xEF')
        
        userid = self.request.POST.get("userid")
        uID = "n" + userid
        UserIP= self.request.POST.get("UserIP")
        TraceID = self.request.POST.get("TraceID")
        OrderID = self.request.POST.get("OrderID")
        NoticeUrl = ""
        BankID = self.request.POST.get("BankID")
        PayWay = self.request.POST.get("PayWay")
        # DesTime = strftime("%Y%m%d%H%M%S", gmtime())
        DesTime = "2019-06-19 19:07:31"
        amount = self.request.POST.get("amount")
        SignCode = str(uID)+ ASIAPAY_CID + UserIP + TraceID + OrderID + NoticeUrl + DesTime + COMDEPOSITKET
        user =  CustomUser.objects.get(pk=userid)
        
        print(SignCode)
        print(MD5(SignCode))
        ParamList_Msg ={
            "rStr" : "",
            "TraceID" : TraceID,
            "C_OrderID":OrderID ,
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
            "tempparam" : "",
            "tempparam" : "",
            "tempparam" : "",
            "tempparam" : "",
            "tempparam" : "",
            "tempparam" : "",
            "tempparam" : "",
            "tempparam" : "",
        }
        delay = kwargs.get("delay", 5)
        sign_encryptKey = DesKey(ASIAPAY_UNITEKEY.encode())
        msg_encryptKey = DesKey(Create_RandomKey(ASIAPAY_R1, ASIAPAY_KEY1,ASIAPAY_R2).encode())
        url = ASIAPAY_API_URL
        print(encryptDES(eString, sign_encryptKey, myIv))
        print(encryptDES(CreateMsgStr(ParamList_Msg), msg_encryptKey, myIv))
        for x in range(3):   
            r = requests.post(url, data={
                'Sign': encryptDES(eString, sign_encryptKey, myIv),
                'Msg': encryptDES(CreateMsgStr(ParamList_Msg), msg_encryptKey, myIv),
                'TraceID': TraceID
            })
            rdata = r.text
            print(rdata)
            tree = ET.fromstring(rdata)
            redirect_url = tree.find('RedirectUrl').text
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
        depositData = {
            "order_id": invoice, 
            "amount": data[3],
            "user_id":  data[1],
            "bank": data[7],
            "currency": currencyConversion[data[10]],
            "channel": 2,
            "status": statusConversion[data[0]]
        }
        return Response(rdata)


