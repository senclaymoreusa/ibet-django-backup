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

logger = logging.getLogger('django')


class CreateMember(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        try :
            user = CustomUser.objects.get(username=username)
            currency = request.POST['currency']
            oddsType = request.POST['oddsType']
            headers =  {'Content-Type': 'application/json'}
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
                print(r)
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
            amount = request.POST['amount']
            direction = request.POST['direction']
            oddsType = request.POST['oddsType']
            wallet_id = request.POST['wallet_id']
            trans_id = username + strftime("%Y%m%d%H%M%S", gmtime())+str(random.randint(0,10000000))
            headers =  {'Content-Type': 'application/json'}
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
                print(r)
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
            try: 
                code = rdata.error_code
                if code == '0':
                    return Response(rdata)
                elif code == '1':
                    return Response({"error":"Failed", "message": "some parameter is wrong, please try again."})    
                elif code == '2':  #call checkFundTransfer api
                    for x in range(3):
                        rr = requests.post(ONEBOOK_API_URL + "CheckFundTransfer/", headers=headers, data={
                            "vendor_id": ONEBOOK_VENDORID,
                            "vendor_trans_id": trans_id,  
                            "wallet_id": wallet_id,
                        })
                        rrdata = rr.json()
                        if rr.status_code == 200:
                            try:
                                rcode = rrdata.error_code
                                if rcode == '0':  #transfer success, will update user's balance
                                    return Response(rrdata)
                                    break
                                elif rcode == ('1' or '2' or '7' or '10') : #transfer failed, will not update user's balance
                                    return Response(rrdata)
                                    break
                                elif rcode == '3':
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
             
            except NameError as error:
                logger.error(error)
        except ObjectDoesNotExist:
            return Response({"error":"The user is not existed."}) 

class GetBetDetail(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        headers =  {'Content-Type': 'application/json'}
        delay = kwargs.get("delay", 5)
        success = False
        for x in range(3):
            r = requests.post(ONEBOOK_API_URL + "GetBetDetail/", headers=headers, data={
                "vendor_id": ONEBOOK_VENDORID,
                "version_key": '0',
            })
            
            rdata = r.json()
            if r.status_code == 200:
                success = True
                break
            elif r.status_code == 204:
                success = True
                # Handle error
                logger.info("Failed to complete a request for GetBetDetail...")
                logger.error(rdata)
                return Response(rdata)
            elif r.status_code == 500:
                logger.info("Request failed {} time(s)'.format(x+1)")
                logger.info("Waiting for %s seconds before retrying again")
                sleep(delay)
        if not success:
            return Response(rdata)
        try:
            error_code = rdata.error_code
            version_key = rdata.Data.last_version_key
            if error_code == '0':
                
                try:
                    bet_history = rdata.Data.BetDetails

                except ObjectDoesNotExist:

                    return Response(rdata)


            return Response(rdata)
        except NameError as error:
            logger.error(error)
class Login(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        try:
            user = CustomUser.objects.get(username=username)
            headers =  {'Content-Type': 'application/json'}
            delay = kwargs.get("delay", 5)
            success = False
            for x in range(3):
                r = requests.post(ONEBOOK_API_URL + "Login/", headers=headers, data={
                    "vendor_id": ONEBOOK_VENDORID,
                    "vendor_member_id": username + '_test',
                })
                rdata = r.json()
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
                code = rdata.error_code
                return Response(rdata)
            except NameError as e:
                logger.error(e)

        except ObjectDoesNotExist as e:
            logger.error(e)
        return Response(rdata)


