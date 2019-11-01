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
from django.core.exceptions import  ObjectDoesNotExist
from decimal import Decimal
from time import sleep
from datetime import datetime
from utils.admin_helper import *

logger = logging.getLogger('django')
try:
    PROVIDER = GameProvider.objects.get(provider_name="Onebook")
except ObjectDoesNotExist:
    logger.error("PROVIDER AND/OR CATEGORY RELATIONS DO NOT EXIST.")


convertCurrency = {
    3:CURRENCY_USD,
    4:CURRENCY_THB,
    6:CURRENCY_EUR,
    13:CURRENCY_CNY,
    15:CURRENCY_IDR,
    20:CURRENCY_TEST,
    51:CURRENCY_VND,
}

outcomeConversion = {
    "won": 0,
    "lose": 1,
    "running": 4,
    "draw":5,
    "half lose":6,
}

class CreateMember(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        try :
            user = CustomUser.objects.get(username=username)
            currency = request.POST['currency']
            oddsType = request.POST['oddsType']
            headers =  {'Content-Type': 'application/x-www-form-urlencoded'}
            delay = kwargs.get("delay", 5)
            success = False
            for x in range(3):
                r = requests.post(ONEBOOK_API_URL + "CreateMember/", headers=headers, data={
                    "vendor_id": ONEBOOK_VENDORID,
                    "Vendor_Member_ID": username + "_test",  #will remove _test when go production
                    "OperatorId": ONEBOOK_OPERATORID,
                    "UserName": username + "_test",  #will remove _test when go production
                    "OddsType": oddsType,
                    "Currency": currency,
                    "MaxTransfer": ONEBOOK_MAXTRANSFER,
                    "MinTransfer": ONEBOOK_MINTRANSFER,
                })
                rdata = r.json()
                print(rdata)
                if r.status_code == 200:
                    success = True
                    break
                elif r.status_code == 204:
                    success = True
                    # Handle error
                    logger.info("Failed to complete a request for createMember...")
                    logger.error(rdata)
                    return Response(rdata)
                elif r.status_code == 500:
                    logger.info("Request failed {} time(s)'.format(x+1)")
                    logger.info("Waiting for %s seconds before retrying again")
                    sleep(delay)
            if not success:
                return Response(rdata)
            print(rdata)
            if rdata['error_code'] == 0:
                return Response({"success":"The user is created successful."})
            else:
                message = rdata['message']
                return Response({"failed": message})
            
            return Response(rdata)
        except ObjectDoesNotExist as e:
            return Response({"error":"The user is not existed."}) 

class FundTransfer(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        try:
            user = CustomUser.objects.get(username=username)
            currency = request.POST['currency']
            amount = request.POST['amount']
            direction = request.POST['direction']
            oddsType = request.POST['oddsType']
            wallet_id = request.POST['wallet_id']
            trans_id = username + strftime("%Y%m%d%H%M%S", gmtime())+str(random.randint(0,10000000))
            if direction == '1' and user.main_wallet - Decimal(amount.replace(',','')) < 0:
                #deposit
                return Response({"error":"Your balance is not enough."})
            else:
                headers =  {'Content-Type': 'application/x-www-form-urlencoded'}
                delay = kwargs.get("delay", 5)
                success = False
                for x in range(3):
                    r = requests.post(ONEBOOK_API_URL + "FundTransfer/", headers=headers, data={
                        "vendor_id": ONEBOOK_VENDORID,
                        "Vendor_Member_ID": username + "_test",  #will remove _test when go production
                        "vendor_trans_id": trans_id,
                        "amount": amount,
                        "currency": currency,
                        "direction":direction,
                        "wallet_id":wallet_id,
                    })
                    
                    rdata = r.json()
                    print(rdata)
                    if r.status_code == 200:
                        success = True
                        break
                    elif r.status_code == 204:
                        success = True
                        # Handle error
                        logger.info("Failed to complete a request for FundTransfer...")
                        logger.error(rdata)
                        return Response(rdata)
                    elif r.status_code == 500:
                        logger.info("Request failed {} time(s)'.format(x+1)")
                        logger.info("Waiting for %s seconds before retrying again")
                        sleep(delay)
                
                if not success:
                    return Response(rdata)
                
                if  rdata['error_code'] == 0 and rdata['Data']['status'] == 0 and rdata['message'] == 'Success':
                    amount = Decimal(amount.replace(',',''))
                    if direction == '1':
                        #deposit
                        user.main_wallet = user.main_wallet - amount
                        user.onebook_wallet = user.onebook_wallet + amount
                    elif direction == '0':
                        #withdraw
                        user.main_wallet = user.main_wallet + amount
                        user.onebook_wallet = user.onebook_wallet - amount
                    user.save()
                    
                    return Response(rdata)
                elif rdata['Data']['status'] == 1 :
                    message = rdata['message']
                    return Response({"error":"Failed", "message": message})    
                elif rdata['Data']['status'] == 2:  #call checkFundTransfer api
                    for x in range(3):
                        rr = requests.post(ONEBOOK_API_URL + "CheckFundTransfer/", headers=headers, data={
                            "vendor_id": ONEBOOK_VENDORID,
                            "vendor_trans_id": trans_id,  
                            "wallet_id": wallet_id,
                        })
                        rrdata = rr.json()
                        if rr.status_code == 200:
                            try:
                                rcode = rrdata['error_code']
                                if rcode == 0:  #transfer success, will update user's balance
                                    return Response(rrdata)
                                    break
                                elif rcode == (1 or 2 or 7 or 10) : #transfer failed, will not update user's balance
                                    return Response(rrdata)
                                    break
                                elif rcode == 3:
                                    logger.info("Request failed {} time(s)'.format(x+1)")
                                    logger.info("Waiting for %s seconds before retrying again")
                                    sleep(300) #wait for 5 minites then try again  
                            except NameError as error:
                                logger.error(error)          
                        elif rr.status_code == 204:
                            # Handle error
                            logger.info("Failed to complete a request for check fund transfer...")
                            logger.error(rrdata)
                            return Response(rrdata)
                else:    
                    return Response({"error":"Request failed"})      
        except ObjectDoesNotExist:
            return Response({"error":"The user is not existed."}) 



class GetBetDetail(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        headers =  {'Content-Type': 'application/x-www-form-urlencoded'}
        delay = kwargs.get("delay", 2)
        success = False
        version_key = GameProvider.objects.get(provider_name='Onebook').notes
        print(version_key)
        for x in range(0,3000):
            r = requests.post(ONEBOOK_API_URL + "GetBetDetail/", headers=headers, data={
                "vendor_id": ONEBOOK_VENDORID,
                "version_key": version_key,
            })
            rdata = r.json()
            print(rdata)
            version_key = rdata["Data"]["last_version_key"]
            updates = GameProvider.objects.get(provider_name='Onebook')
            updates.notes = version_key
            updates.save()
            if  "BetDetails" in rdata['Data']:
                # print(rdata["Data"]["BetDetails"])
                

                for i in range(len(rdata["Data"]["BetDetails"])):
                    username = str(rdata["Data"]["BetDetails"][i]["vendor_member_id"]).split('_')[0]
                    cate = Category.objects.get(name='SPORTS')
                    if rdata["Data"]["BetDetails"][i]["settlement_time"] == None:
                        
                        GameBet.objects.get_or_create(provider=PROVIDER,
                                                    category=cate,
                                                    username=CustomUser.objects.get(username=username),
                                                    odds=rdata["Data"]["BetDetails"][i]["odds"],
                                                    amount_wagered=rdata["Data"]["BetDetails"][i]["stake"],
                                                    currency=convertCurrency[rdata["Data"]["BetDetails"][i]["currency"]],
                                                    bet_type=rdata["Data"]["BetDetails"][i]["bet_type"],
                                                    amount_won=rdata["Data"]["BetDetails"][i]["winlost_amount"],
                                                    outcome=outcomeConversion[rdata["Data"]["BetDetails"][i]["ticket_status"]],
                                                    market=ibetCN,
                                                    )
                    else:
                        resolve = datetime.datetime.strptime(rdata["Data"]["BetDetails"][i]["settlement_time"], '%Y-%m-%dT%H:%M:%S.%f')
                        
                        GameBet.objects.get_or_create(provider=PROVIDER,
                                                    category=cate,
                                                    username=CustomUser.objects.get(username=username),
                                                    odds=rdata["Data"]["BetDetails"][i]["odds"],
                                                    amount_wagered=rdata["Data"]["BetDetails"][i]["stake"],
                                                    currency=convertCurrency[rdata["Data"]["BetDetails"][i]["currency"]],
                                                    bet_type=rdata["Data"]["BetDetails"][i]["bet_type"],
                                                    amount_won=rdata["Data"]["BetDetails"][i]["winlost_amount"],
                                                    outcome=outcomeConversion[rdata["Data"]["BetDetails"][i]["ticket_status"]],
                                                    resolved_time=utcToLocalDatetime(resolve),
                                                    market=ibetCN,
                                                    )
                sleep(delay)    
            else:
                print("BetDetails is not existed.")
                break
        return Response(rdata)   

class Login(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        try:
            user = CustomUser.objects.get(username=username)
            headers =  {'Content-Type': 'application/x-www-form-urlencoded'}
            delay = kwargs.get("delay", 5)
            success = False
            for x in range(3):
                r = requests.post(ONEBOOK_API_URL + "Login/", headers=headers, data={
                    "vendor_id": ONEBOOK_VENDORID,
                    "vendor_member_id": username + '_test',
                })
                rdata = r.json()
                print(rdata)
                if r.status_code == 200:
                    success = True
                    break
                elif r.status_code == 204:
                    success = True
                    # Handle error
                    logger.info("Failed to complete a request for createMember...")
                    logger.error(rdata)
                    return Response(rdata)
                elif r.status_code == 500:
                    logger.info("Request failed {} time(s)'.format(x+1)")
                    logger.info("Waiting for %s seconds before retrying again")
                    sleep(delay)
            if not success:
                return Response(rdata)
            try:
                code = rdata['error_code']
                return Response(rdata)
            except NameError as e:
                logger.error(e)
                return Response({"error": "Cannot find the code."})

        except ObjectDoesNotExist as e:
            logger.error(e)
            return Response({"error": "Cannot find the user."})

def CheckMemberOnline(request):
    if request.method == "POST":
        secret_key = request.POST.get("secret_key")
        vendor_member_id = request.POST.get("vendor_member_id")
        op = request.POST.get("op")
        username = vendor_member_id.split('_')[0]  #will need to remove this line when go production mode
        try:
            user = CustomUser.objects.get(username=username)
            
            try:
                token = Token.objects.get(user=user)
                if secret_key == 'ibetClymore!':
                    root = ET.Element("member_online")
                    tr1 = ET.SubElement(root, "StatusCode")
                    tr1.text = '0'
                    tr2 = ET.SubElement(root, "message")
                    tr2.text = 'User is online'
                else:
                    root = ET.Element("member_online")
                    tr1 = ET.SubElement(root, "StatusCode")
                    tr1.text = '1'
                    tr2 = ET.SubElement(root, "message")
                    tr2.text = 'Secret key is not correct.'
            except ObjectDoesNotExist:
                root = ET.Element("member_online")
                tr1 = ET.SubElement(root, "StatusCode")
                tr1.text = '3'
                tr2 = ET.SubElement(root, "message")
                tr2.text = 'The user is logout.'
                return HttpResponse(ET.tostring(root), content_type="text/xml")
        except ObjectDoesNotExist:
            root = ET.Element("member_online")
            tr1 = ET.SubElement(root, "StatusCode")
            tr1.text = '2'
            tr2 = ET.SubElement(root, "message")
            tr2.text = 'User is not exist.'
            return HttpResponse(ET.tostring(root), content_type="text/xml")
        return HttpResponse(ET.tostring(root), content_type="text/xml")

        


