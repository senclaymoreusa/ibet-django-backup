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

logger = logging.getLogger('django')


class CreateMember(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        username = request.POST['username']
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
            oddsType = request.POST['oddsType']
            headers =  {'Content-Type': 'application/json'}
            delay = kwargs.get("delay", 5)
            success = False
            for x in range(3):
                r = requests.post(ONEBOOK_API_URL + "FundTransfer/", headers=headers, data={
                    "vendor_id": ONEBOOK_VENDORID,
                    "Vendor_Member_ID": username + "_test",  #will remove _test when go production
                    # "vendor_trans_id": ,
                    # "amount":,
                    # "currency":,
                    # "direction":,
                    # "wallet_id":,
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
        




