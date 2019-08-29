from django.shortcuts import render
from django.http import HttpResponse
from django.views import View, generic
from users.models import CustomUser
from accounting.models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from utils.constants import *
import utils.helpers as helpers

#from djauth.third_party_keys import *
from rest_framework import generics
from accounting.serializers import asiapayDepositSerialize, asiapayCashoutSerialize,asiapayDepositFinishSerialize,asiapayOrderStatusFinishSerialize,asiapayExchangeRateFinishSerialize,asiapayDepositArriveSerialize,asiapayPayoutArriveSerialize
from django.conf import settings
import requests,json,random
import logging, time, struct, hashlib, xml.etree.ElementTree as ET
from time import sleep
from des import DesKey
import base64, socket
from time import gmtime, strftime, strptime
from django.utils import timezone

logger = logging.getLogger("django")

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
    '47':'银联支付',
    '49':'京东支付',
    '201': '比特币',
}


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
    logger.info(ParamList.values())
    msgStr = ",".join(str(x) for x in ParamList.values())+ ","
    logger.info("msgStr:" + msgStr)
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
        user = CustomUser.objects.get(pk=userid)
        trans_id = user.username+strftime("%Y%m%d%H%M%S", gmtime())+str(random.randint(0,10000000))
        UserIP=helpers.get_client_ip(request)
        TraceID = strftime("%Y%m%d%H%M%S", gmtime())
        #OrderID =  "ibet" +strftime("%Y%m%d%H%M%S", gmtime())
        NoticeUrl = ""
        BankID = self.request.POST.get("method")
        PayWay = self.request.POST.get("PayWay")
        DesTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        amount = self.request.POST.get("amount")
        SignCode = str(uID)+ ASIAPAY_CID + UserIP + TraceID + "D" + trans_id + NoticeUrl + DesTime + ASIAPAY_DEPOSITKEY
        #user =  CustomUser.objects.get(pk=userid)
        currency = self.request.POST.get("currency")
        logger.info(SignCode)
        logger.info(MD5(SignCode))
        ParamList_Msg ={
            "rStr" : "",
            "TraceID" : TraceID,
            "C_OrderID": 'D' + trans_id,
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
        logger.info(encryptDES(eString, sign_encryptKey, myIv))
        logger.info(encryptDES(CreateMsgStr(ParamList_Msg), msg_encryptKey, myIv))
      
        r = requests.post(url + "/standard/getway/depositiface", data={
            'Sign': encryptDES(eString, sign_encryptKey, myIv),
            'Msg': encryptDES(CreateMsgStr(ParamList_Msg), msg_encryptKey, myIv),
            'TraceID': TraceID,
            'OrderID':'D' + trans_id,
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
        logger.info(rdata)
        if r.status_code == 200 or r.status_code == 201:
            tree = ET.fromstring(rdata)
            StatusCode = tree.find('StatusCode').text
            StatusMsg = tree.find('StatusMsg').text
            paymentAPIURL = tree.find('RedirectUrl').text
            paymentAPIURL = decryptDES(paymentAPIURL,msg_encryptKey, myIv)
            print(paymentAPIURL)
            logger.info(paymentAPIURL)
            if StatusMsg == 'OK':
                oID = tree.find('oID').text
                create = Transaction.objects.create(
                    order_id=oID,
                    transaction_id=trans_id,
                    amount=amount,
                    user_id=CustomUser.objects.get(pk=userid),
                    currency= int(currency),
                    transaction_type=0, 
                    channel=4,
                    status=2,
                    method=bankidConversion[BankID],
                    request_time=timezone.now(),
                )
                if PayWay == ASIAPAY_QRPAYWAY or PayWay == '30':
                    rr = requests.get(paymentAPIURL, params={
                            "cid":ASIAPAY_CID,
                            "oid":"D" + trans_id
                        })
                    
                    rrdata = rr.json()
                    logger.info(rrdata)
                    print(rrdata)
                    return Response(rrdata)
               
            else:
                logger.info("There was something wrong with the result")
                logger.info(StatusMsg)
                return Response(StatusMsg)
                
        else:
            # Handle error
            logger.info("There was something wrong with the result")
            logger.info(rdata)
            return Response(rdata)
        return Response({"order_id": "D"+trans_id, "url": paymentAPIURL})


class submitCashout(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = asiapayCashoutSerialize
    permission_classes = [AllowAny, ]
    
    def post(self, request, *args, **kwargs):
        userid = self.request.POST.get("userid")
        uID = "n" + userid
        UserIP=helpers.get_client_ip(request)
        TraceID = strftime("%Y%m%d%H%M%S", gmtime())
        user = CustomUser.objects.get(pk=userid)
        trans_id = user.username+strftime("%Y%m%d%H%M%S", gmtime())+str(random.randint(0,10000000))
        #OrderID =  "ibet" +strftime("%Y%m%d%H%M%S", gmtime())
        NoticeUrl = ""
        DesTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        amount = self.request.POST.get("amount")
        CashBankName =""
        CashCardNumber = self.request.POST.get("CashCardNumber")
        CashCardChName = self.request.POST.get("CashCardChName")
        CashBankPro = ""
        CashBankCity = ""
        CashBankDetailName = self.request.POST.get("CashBankDetailName")
        SignCode = str(uID)+ ASIAPAY_CID + ASIAPAY_CPASS + amount+ CashBankName+ CashCardNumber+ CashCardChName+CashBankPro+CashBankCity+CashBankDetailName+ UserIP + TraceID + "W" + trans_id + NoticeUrl + DesTime + ASIAPAY_CASHKEY
        logger.info(SignCode)
        currency = self.request.POST.get("currency")
        cashoutMethod = self.request.POST.get("cashoutMethod")
        # logger.info(SignCode)
        # logger.info(MD5(SignCode))
        ParamList_Msg ={
            "rStr" : "",
            "cID": ASIAPAY_CID,
            "uID": uID,
            "cPass": ASIAPAY_CPASS,
            "TraceID" : TraceID,
            "OrderID": "W" + trans_id,
            "CashMoney":amount,
            "CashBankName":CashBankName,
            "CashCardNumber":CashCardNumber,
            "CashCardChName":CashCardChName,
            "CashBankPro":CashBankPro,
            "CashBankCity":CashBankCity,
            "CashBankDetailName":CashBankDetailName,
            "UserIP": UserIP,
            "NoticeUrl": NoticeUrl,
            "DesTime": DesTime,
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
        logger.info("sign:" + encryptDES(eString, sign_encryptKey, myIv))
        logger.info("msg:" + encryptDES(CreateMsgStr(ParamList_Msg), msg_encryptKey, myIv))
        r = requests.post(url + "/standard/getway/" + cashoutMethod, data={
            'rStr':'',
            'Sign': encryptDES(eString, sign_encryptKey, myIv),
            'Msg': encryptDES(CreateMsgStr(ParamList_Msg), msg_encryptKey, myIv),
            'TraceID': TraceID,
            'OrderID':"W" + trans_id,
            'cID':ASIAPAY_CID,
            'uID':uID,
            'cPass': ASIAPAY_CPASS,
            'UserIP':UserIP,
            'DesTime':DesTime,
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
        logger.info(rdata)
    
        tree = ET.fromstring(rdata)
        StatusCode = tree.find('StatusCode').text
        StatusMsg = tree.find('StatusMsg').text
        logger.info(StatusMsg)
        if StatusCode == '50001':
            create = Transaction.objects.create(
                transaction_id=trans_id,
                amount=amount,
                user_id=CustomUser.objects.get(pk=userid),
                currency= int(currency),
                transaction_type=1, 
                channel=4,
                status=2,
                method=cashoutMethod,
                request_time=timezone.now(),
            )
            return Response(StatusCode)
        else:
            logger.info(StatusMsg)
        
        return Response(StatusCode)

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
            transaction_id=OrderID)
            orderData.status = 3
            orderData.last_updated = timezone.now(),
            orderData.save()
        else:
            logger.info('The request information is nor correct, please try again')
        logger.info(rdata)
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
        logger.info(rdata)
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
        logger.info(rdata)
        return Response(rdata)

def depositArrive(request):
    if request.method == "POST":
        print("HAHAHAHAHA")
        print(request.POST)
        StatusCode = request.POST.get("StatusCode")
        RevCardNumber = request.POST.get("RevCardNumber")
        RevMoney = request.POST.get("amount")
        order_id = request.POST.get("OrderID")
        OrderID = order_id[1:]
        print(OrderID)
        uID = request.POST.get("uID")
        userid = uID.strip('n')
        logger.info(userid)
        # serializer = serializer_class(data=request.data)
        # logger.info(serializer)
        datetime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        
        #if trans.order_id != '0':

        # logger.info(serializer.is_valid())
        root = ET.Element("ProcessStatus")
        tr1 = ET.SubElement(root, "StatusCode")
        tr1.text = StatusCode
        tr2 = ET.SubElement(root, "StatusMsg")
        tr2.text = "success"
        tr3 = ET.SubElement(root, "ProcessTime")
        tr3.text = datetime
        
        root1 = ET.Element("ProcessStatus")
        tr1 = ET.SubElement(root1, "StatusCode")
        tr1.text = StatusCode
        tr2 = ET.SubElement(root1, "StatusMsg")
        tr2.text = "Parameter is not correct"
        tr3 = ET.SubElement(root1, "ProcessTime")
        tr3.text = datetime

        root2 = ET.Element("ProcessStatus")
        tr1 = ET.SubElement(root2, "StatusCode")
        tr1.text = StatusCode
        tr2 = ET.SubElement(root2, "StatusMsg")
        tr2.text = "Please send it again"
        tr3 = ET.SubElement(root2, "ProcessTime")
        tr3.text = datetime

        try:
            trans = Transaction.objects.get(transaction_id=OrderID)
            print(trans)
            if StatusCode == '001':  
                trans.status = 0
                trans.arrive_time = timezone.now()
                trans.save()
                return HttpResponse(ET.tostring(root),content_type="text/xml")
            else:
                trans.status = 1
                trans.save()
                return HttpResponse(ET.tostring(root1),content_type="text/xml")

        except trans.DoesNotExist:
            trans = None
            return HttpResponse(ET.tostring(root2),content_type="text/xml")


# class depositArrive(generics.GenericAPIView):
#     queryset = Transaction.objects.all()
#     serializer_class = asiapayDepositArriveSerialize
#     permission_classes = [AllowAny, ]
#     # parser_classes = (XMLParser,)
#     # rendere9r_classes = (XMLRenderer,)
#     def post(self, request, *args, **kwargs):
#         print("HAHAHAHAHA")
#         StatusCode = self.request.POST.get("StatusCode")
#         RevCardNumber = self.request.POST.get("RevCardNumber")
#         RevMoney = self.request.POST.get("amount")
#         order_id = self.request.POST.get("order_id")
#         OrderID = order_id[1:]
#         logger.info(OrderID)
#         uID = self.request.POST.get("uID")
#         userid = uID.strip('n')
#         logger.info(userid)
#         serializer = self.serializer_class(data=request.data)
#         logger.info(serializer)
#         datetime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
#         logger.info(serializer.is_valid())
        
#         root = ET.Element("ProcessStatus")
#         tr1 = ET.SubElement(root, "StatusCode")
#         tr1.text = "001"
#         tr2 = ET.SubElement(root, "StatusMsg")
#         tr2.text = "success"
#         tr3 = ET.SubElement(root, "ProcessTime")
#         tr3.text = datetime
        
#         root1 = ET.Element("ProcessStatus")
#         tr1 = ET.SubElement(root1, "StatusCode")
#         tr1.text = "002"
#         tr2 = ET.SubElement(root1, "StatusMsg")
#         tr2.text = "Parameter is not correct"
#         tr3 = ET.SubElement(root1, "ProcessTime")
#         tr3.text = datetime

#         root2 = ET.Element("ProcessStatus")
#         tr1 = ET.SubElement(root2, "StatusCode")
#         tr1.text = "003"
#         tr2 = ET.SubElement(root2, "StatusMsg")
#         tr2.text = "Please send it again"
#         tr3 = ET.SubElement(root2, "ProcessTime")
#         tr3.text = datetime

#         if serializer.is_valid() and StatusCode == '001':  
#             saveData = Transaction.objects.get(user_id=userid, order_id=order_id) 
#             saveData.status = 6
#             saveData.arrive_time = timezone.now()
#             saveData.save()
            
#             return HttpResponse(ET.tostring(root),content_type=status.HTTP_200_OK)
#         elif not serializer.is_valid():
#             return Response(ET.tostring(root1), status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response(ET.tostring(root2), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class payoutArrive(generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = asiapayPayoutArriveSerialize
    permission_classes = [AllowAny, ]
    def post(self, request, *args, **kwargs):
        TrustIUser = self.request.data.get('TrustIUser')
        OrderID = self.request.data.get('OrderID')
        OrderID = order_id[1:]
        findData = Transaction.objects.get(order_id=OrderID)
        uID = findData.user_id
        uID = 'n' + uID
        amount = findData.amount
        root = ET.Element("CashInfo")
        tr1 = ET.SubElement(root, "StatusCode")
        tr1.text = "001"
        tr2 = ET.SubElement(root, "uID")
        tr2.text = uID
        tr3 = ET.SubElement(root, "CashMoney")
        tr3.text = amount
        tr4 = ET.SubElement(root, "CashCardNumber")
        tr4.text = CashCardNumber
        tr5 = ET.SubElement(root, "ProccessTime")
        tr5.text = timezone.now()
        if TrustIUser == ASIAPAY_TRUSTUSER :

            if serializer.is_valid() and findData == OrderID:  

                saveData = Transaction.objects.get(user_id=userid, order_id=order_id) 
                saveData.status = 6
                saveData.arrive_time = timezone.now()
                saveData.save()
                
                return Response(ET.tostring(root),status=status.HTTP_200_OK)
            elif not serializer.is_valid():
                return Response(ET.tostring(root1), status=status.ccc)
            else:
                return Response(ET.tostring(root2), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"detail" : "need a trust user please."}, status=HTTP_401_UNAUTHORIZED)








