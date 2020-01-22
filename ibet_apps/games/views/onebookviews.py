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
# from background_task import background
import redis
from utils.redisClient import RedisClient
from utils.redisHelper import RedisHelper
from django.db import DatabaseError, transaction
import datetime
from datetime import date
from django.utils import timezone
import random
from rest_framework.decorators import api_view, permission_classes
logger = logging.getLogger('django')



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
    "draw":2,
    "half lose":0,
    "half won" : 0,
    "reject": 3,
    "void": 3,
    "refund": 3
}
def createMember(username, oddsType):
    try:
        user = CustomUser.objects.get(username=username)
        
        if user.currency == CURRENCY_CNY:
            currency = 13
        elif user.currency == CURRENCY_USD:
            currency = 3
        elif user.currency == CURRENCY_THB:
            currency = 4
        elif user.currency == CURRENCY_EUR:
            currency = 6
        elif user.currency == CURRENCY_IDR:
            currency = 15
        elif user.currency == CURRENCY_VND:
            currency = 51
        elif user.currency == CURRENCY_TEST:
            currency = 20

        headers =  {'Content-Type': 'application/x-www-form-urlencoded'}
        delay = 5
        success = False
        for x in range(3):
            r = requests.post(ONEBOOK_API_URL + "CreateMember/", headers=headers, data={
                "vendor_id": ONEBOOK_VENDORID,
                "Vendor_Member_ID": username,  #will remove _test when go production, + "_test"
                "OperatorId": ONEBOOK_OPERATORID,
                "UserName": username ,  #will remove _test when go production, + "_test"
                "OddsType": oddsType,
                "Currency": currency,
                "MaxTransfer": ONEBOOK_MAXTRANSFER,
                "MinTransfer": ONEBOOK_MINTRANSFER,
            })
            rdata = r.json()
            logger.info(rdata)
            if r.status_code == 200:
                success = True
                break
            elif r.status_code == 204:
                success = True
                # Handle error
                logger.info("Failed to complete a request for onebook createMember...")
                logger.error(rdata)
                return ERROR_CODE_FAIL
            elif r.status_code == 500:
                logger.info("Request failed {} time(s)'.format(x+1)")
                logger.info("Waiting for %s seconds before retrying again")
                sleep(delay)
        if not success:
            return ERROR_CODE_FAIL
        
        if rdata['error_code'] == 0 or rdata['error_code'] == 6:
            return CODE_SUCCESS
        else:
            return ERROR_CODE_FAIL
        
    except ObjectDoesNotExist as e:
        logger.error(e)
        return ERROR_CODE_FAIL
        
             

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
                    "Vendor_Member_ID": username,  #will remove _test when go production, + "_test"
                    "OperatorId": ONEBOOK_OPERATORID,
                    "UserName": username,  #will remove _test when go production, + "_test"
                    "OddsType": oddsType,
                    "Currency": currency,
                    "MaxTransfer": ONEBOOK_MAXTRANSFER,
                    "MinTransfer": ONEBOOK_MINTRANSFER,
                })
                rdata = r.json()
                logger.info(rdata)
                if r.status_code == 200:
                    success = True
                    break
                elif r.status_code == 204:
                    success = True
                    # Handle error
                    logger.info("Failed to complete a request for onebook createMember...")
                    logger.error(rdata)
                    return Response(rdata)
                elif r.status_code == 500:
                    logger.info("Request failed {} time(s)'.format(x+1)")
                    logger.info("Waiting for %s seconds before retrying again")
                    sleep(delay)
            if not success:
                return Response(rdata)
            logger.info(rdata)
            if rdata['error_code'] == 0:
                return Response({"success":"The user is created successful in onebook CreateMember."})
            else:
                message = rdata['message']
                return Response({"failed": message})
            
            return Response(rdata)
        except ObjectDoesNotExist as e:
            return Response({"error":"The user does not exist in onebook CreateMember."}) 

def createMember(user,currency,oddsType):

    headers =  {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(ONEBOOK_API_URL + "CreateMember/", headers=headers, data={
        "vendor_id": ONEBOOK_VENDORID,
        "Vendor_Member_ID": user.username,  #will remove _test when go production,  + "_test"
        "OperatorId": ONEBOOK_OPERATORID,
        "UserName": user.username,  #will remove _test when go production,  + "_test"
        "OddsType": oddsType,
        "Currency": currency,
        "MaxTransfer": ONEBOOK_MAXTRANSFER,
        "MinTransfer": ONEBOOK_MINTRANSFER, #ONEBOOK_MINTRANSFER
    })
    
    rdata = r.json()
    logger.info(rdata)
    # print(rdata)
    if r.status_code == 200:
        if rdata['error_code'] == 0 or rdata['error_code'] == 6:
            return CODE_SUCCESS
        else:
            return ERROR_CODE_FAIL
    else: 
        return ERROR_CODE_FAIL
    
    
    

def fundTransfer(user, amount, fund_wallet, direction, wallet_id, oddsType):
    
    trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))  
    
    
    if user.currency == CURRENCY_CNY:
        currency = 13
    elif user.currency == CURRENCY_USD:
        currency = 3
    elif user.currency == CURRENCY_THB:
        currency = 4
    elif user.currency == CURRENCY_EUR:
        currency = 6
    elif user.currency == CURRENCY_IDR:
        currency = 15
    elif user.currency == CURRENCY_VND:
        currency = 51
    elif user.currency == CURRENCY_TEST or (user.currency == CURRENCY_TTC):
        currency = 20
    else:
        currency = 20
    
    # wallet_name = fund_wallet + "_wallet"  #for example: onebook_wallet
    # wallet = getattr(user, wallet_name)
    # if direction == '1' and wallet - amount < 0:
    # #deposit
    #     logger.info('balance is not enough.')
    # else: 
    headers =  {'Content-Type': 'application/x-www-form-urlencoded'}
    delay = 5
    success = False
    username = user.username
    if createMember(user, currency,oddsType) == CODE_SUCCESS:  #check if user is a member ,if not create a new member
        for x in range(3):
            r = requests.post(ONEBOOK_API_URL + "FundTransfer/", headers=headers, data={
                "vendor_id": ONEBOOK_VENDORID,
                "Vendor_Member_ID": username,  #will remove _test when go production, + "_test"
                "vendor_trans_id": trans_id,
                "amount": amount,
                "currency": currency,
                "direction":direction,
                "wallet_id":wallet_id,
            })
            rdata = r.json()
            #print(rdata)
            logger.info(rdata)
            if r.status_code == 200:
                success = True
                break
            elif r.status_code == 204:
                success = True
                # Handle error
                logger.info("Failed to complete a request for onebook FundTransfer...")
                logger.error(rdata)
                return ERROR_CODE_FAIL
            elif r.status_code == 500:
                logger.info("Request failed {} time(s)'.format(x+1)")
                logger.info("Waiting for %s seconds before retrying again")
                sleep(delay)
        if not success:
            return ERROR_CODE_FAIL
        if  rdata['error_code'] == 0 and rdata['Data']['status'] == 0 and rdata['message'] == 'Success':
            # amount = Decimal(amount.replace(',',''))
            
            if direction == '1':
                #print("dirction is 1")
                #deposit
                # wallet = wallet - amount
                # user.onebook_wallet = user.onebook_wallet + amount
                try:
                    Transaction.objects.create(transaction_id=trans_id,
                                            user_id=user,
                                            order_id=trans_id,
                                            amount=amount,
                                            currency=user.currency,
                                            transfer_from=fund_wallet,
                                            transfer_to='Onebook',
                                            product=GAME_TYPE_SPORTS,
                                            transaction_type=TRANSACTION_TRANSFER,
                                            channel=None,
                                            status=TRAN_SUCCESS_TYPE)
                    return CODE_SUCCESS
                except Exception as e:
                    logger.error("request transfer to Onebook: ", e)
                    #print("request transfer to Onebook: ", e)
                    return ERROR_CODE_FAIL
            elif direction == '0':                                                            
                #withdraw
                # wallet = wallet + amount
                # user.onebook_wallet = user.onebook_wallet - amount
                try:
                    Transaction.objects.create(transaction_id=trans_id,
                                            user_id=user,
                                            order_id=trans_id,
                                            amount=amount,
                                            currency=user.currency,
                                            transfer_from='Onebook',
                                            transfer_to=fund_wallet,
                                            product=GAME_TYPE_SPORTS,
                                            transaction_type=TRANSACTION_TRANSFER,
                                            channel=None,
                                            status=TRAN_SUCCESS_TYPE)
                    return CODE_SUCCESS
                except Exception as e:
                    logger.error("request transfer from Onebook: ", e)
                    #print("request transfer from Onebook: ", e)
                    return ERROR_CODE_FAIL
            # user.save()
    
            
        elif rdata['Data']['status'] == 1 :
            
            return ERROR_CODE_FAIL   
        elif rdata['Data']['status'] == 2:  #call checkFundTransfer api
            for x in range(3):
                rr = requests.post(ONEBOOK_API_URL + "CheckFundTransfer/", headers=headers, data={
                    "vendor_id": ONEBOOK_VENDORID,
                    "vendor_trans_id": trans_id,  
                    "wallet_id": wallet_id,
                })
                rrdata = rr.json()
                logger.info(rrdata)
                if rr.status_code == 200:
                    try:
                        rcode = rrdata['error_code']
                        if rcode == 0:  #transfer success, will update user's balance
                            
                            if direction == '1':
                            #deposit
                                # wallet = wallet - amount
                                # user.onebook_wallet = user.onebook_wallet + amount
                                try:
                                    Transaction.objects.create(transaction_id=trans_id,
                                                            user_id=user,
                                                            order_id=trans_id,
                                                            amount=amount,
                                                            currency=user.currency,
                                                            transfer_from=fund_wallet,
                                                            transfer_to='Onebook',
                                                            product=GAME_TYPE_SPORTS,
                                                            transaction_type=TRANSACTION_TRANSFER,
                                                            status=TRAN_SUCCESS_TYPE)
                                    return CODE_SUCCESS
                                except Exception as e:
                                    logger.error("request transfer to Onebook: ", e)
                                    #print("request transfer to Onebook: ", e)
                                    return ERROR_CODE_FAIL
                            elif direction == '0':
                                #withdraw
                                # wallet = wallet + amount
                                # user.onebook_wallet = user.onebook_wallet - amount
                                try:
                                    Transaction.objects.create(transaction_id=trans_id,
                                                            user_id=user,
                                                            order_id=trans_id,
                                                            amount=amount,
                                                            currency=user.currency,
                                                            transfer_from='Onebook',
                                                            transfer_to=fund_wallet,
                                                            product=GAME_TYPE_SPORTS,
                                                            transaction_type=TRANSACTION_TRANSFER,
                                                            status=TRAN_SUCCESS_TYPE)
                                    return CODE_SUCCESS
                            # user.save() 
                                except Exception as e:
                                    logger.error("request transfer from Onebook: ", e)
                                    #print("request transfer from Onebook: ", e)
                                    return ERROR_CODE_FAIL      
                            
                            break
                        elif rcode == (1 or 2 or 7 or 10) : #transfer failed, will not update user's balance
                            return ERROR_CODE_FAIL
                            break
                        elif rcode == 3:
                            logger.info("Request failed {} time(s)'.format(x+1)")
                            logger.info("Waiting for %s seconds before retrying again")
                            sleep(300) #wait for 5 minites then try again  
                    except NameError as error:
                        logger.error(error)
                        return  ERROR_CODE_FAIL         
                elif rr.status_code == 204:
                    # Handle error
                    logger.info("Failed to complete a request for onebook check fund transfer...")
                    logger.error(rrdata)
                    return ERROR_CODE_FAIL
        else:    
            return ERROR_CODE_FAIL
    else:
        return ERROR_CODE_FAIL




    
# def test01(request, username):
#     #username = request.GET.get('username')
#     return HttpResponse(username)

class FundTransfer(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        try:
            user = CustomUser.objects.get(username=username)
            currency = request.POST['currency']
            amount = request.POST['amount']
            direction = request.POST['direction']
            wallet_id = request.POST['wallet_id']
            trans_id = username + strftime("%Y%m%d%H%M%S", gmtime())+str(random.randint(0,10000000))
            if direction == '1' and user.main_wallet - Decimal(amount.replace(',','')) < 0:
                #deposit
                return Response({"error":"Your balance is not enough for onebook."})
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
                    logger.info(rdata)
                    if r.status_code == 200:
                        success = True
                        break
                    elif r.status_code == 204:
                        success = True
                        # Handle error
                        logger.info("Failed to complete a request for onebook FundTransfer...")
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
                            logger.info("Failed to complete a request for onebook check fund transfer...")
                            logger.error(rrdata)
                            return Response(rrdata)
                else:    
                    return Response({"error":"Request failed for onebook FundTransfer"})      
        except ObjectDoesNotExist:
            return Response({"error":"The user does not exist onebook FundTransfer."}) 



@transaction.atomic
@api_view(['POST'])
@permission_classes((AllowAny,))      
def getBetDetail(request):
    if request.method == 'POST':
        try:
            PROVIDER = GameProvider.objects.get(provider_name=ONEBOOK_PROVIDER)
        except ObjectDoesNotExist:
            logger.error("PROVIDER AND/OR CATEGORY RELATIONS DO NOT EXIST.")
            raise Exception("PROVIDER AND/OR CATEGORY RELATIONS DO NOT EXIST.")
            
        headers =  {'Content-Type': 'application/x-www-form-urlencoded'}
        delay = 2
        success = False
        version_key = PROVIDER.notes
        
        onebook_run = "run"
        try:
            r = RedisClient().connect()
            redis = RedisHelper()
        except:
            logger.error("There is something wrong with redis connection.")
            return Response({'status': 'There is something wrong with redis connection.'}, status=status.HTTP_400_BAD_REQUEST)

        #print(redis.check_onebook_bet_details(onebook_run))
        if redis.check_onebook_bet_details(onebook_run) is False: #if the key does not exist in redis
            redis.set_onebook_bet_details(onebook_run)  #insert the key to redis
            while(redis.check_onebook_bet_details(onebook_run)): #loop while the key is existed in redis
                try:
                    r = requests.post(ONEBOOK_API_URL + "GetBetDetail/", headers=headers, data={
                        "vendor_id": ONEBOOK_VENDORID,
                        "version_key": version_key,
                    })
                    rdata = r.json()
                except requests.RequestException:
                    logger.error("Connectivity error for onebook GetBetDetail API.")
                    redis.remove_onebook_bet_details(onebook_run)  #remove the key from redis when break the while loop
                    return Response({'error': 'Connectivity error for onebook GetBetDetail API.'})
                except ValueError:
                    logger.error("JSON parsing error for onebook GetBetDetail API.")
                    redis.remove_onebook_bet_details(onebook_run)  #remove the key from redis when break the while loop
                    return Response({'error': 'JSON parsing error for onebook GetBetDetail API.'})
                except (IndexError, KeyError):
                    logger.error("JSON format error for onebook GetBetDetail API.")
                    redis.remove_onebook_bet_details(onebook_run)  #remove the key from redis when break the while loop
                    return Response({'error': 'JSON format error for onebook GetBetDetail API.'})
                if r.status_code == 200:
                    
                    version_key = rdata["Data"]["last_version_key"]        
                    
                    updates = GameProvider.objects.get(provider_name=ONEBOOK_PROVIDER)
                    
                    updates.notes = version_key
                    updates.save()
                        
                    if  "BetDetails" in rdata['Data']:
                        
                        # logger.info(rdata["Data"]["BetDetails"])
                        for i in range(len(rdata["Data"]["BetDetails"])):
                            
                            username = str(rdata["Data"]["BetDetails"][i]["vendor_member_id"]).split('_')[0]
                            # print(username)
                            
                            cate = Category.objects.get(name='Sports')
                            
                            trans_id = rdata["Data"]["BetDetails"][i]["trans_id"]

                            try:
                                user = CustomUser.objects.get(username=username)
                                
                            except ObjectDoesNotExist:     
                                redis.remove_onebook_bet_details(onebook_run)  #remove the key from redis
                                logger.error("The user does not exist.")
                                return Response({'error': 'The user does not exist.'})

                            transid = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
                            outcome = rdata["Data"]["BetDetails"][i]["ticket_status"]
                            if rdata["Data"]["BetDetails"][i]["settlement_time"] == '':
                                    if not GameBet.objects.filter(ref_no=trans_id).exists():
                                    
                                        GameBet.objects.create(provider=PROVIDER,
                                                            category=cate,
                                                            user=user,
                                                            user_name=user.username,
                                                            transaction_id=transid,
                                                            odds=rdata["Data"]["BetDetails"][i]["odds"],
                                                            amount_wagered=rdata["Data"]["BetDetails"][i]["stake"],
                                                            currency=convertCurrency[rdata["Data"]["BetDetails"][i]["currency"]],
                                                            bet_type=rdata["Data"]["BetDetails"][i]["bet_type"],
                                                            ref_no=trans_id,
                                                            market=ibetCN,
                                                            other_data={
                                                                "version_key": version_key
                                                            }
                                                        )
                                
                            else:
                                if (outcome == "won" or outcome == "half won" or outcome == "lose" or outcome == "half lose" or outcome == "draw" or outcome == "reject" or  outcome == "refund" or outcome == "void"):
                                    
                                    resolve = datetime.datetime.strptime(rdata["Data"]["BetDetails"][i]["settlement_time"], '%Y-%m-%dT%H:%M:%S.%f')
                                       
                                    GameBet.objects.create(provider=PROVIDER,
                                                        category=cate,
                                                        transaction_id=transid,
                                                        user=user,
                                                        user_name=user.username,
                                                        odds=rdata["Data"]["BetDetails"][i]["odds"],
                                                        amount_wagered=rdata["Data"]["BetDetails"][i]["stake"],
                                                        currency=convertCurrency[rdata["Data"]["BetDetails"][i]["currency"]],
                                                        bet_type=rdata["Data"]["BetDetails"][i]["bet_type"],
                                                        amount_won=rdata["Data"]["BetDetails"][i]["winlost_amount"],
                                                        outcome=outcomeConversion[outcome],
                                                        resolved_time=utcToLocalDatetime(resolve),
                                                        ref_no=trans_id,
                                                        market=ibetCN,
                                                        other_data={
                                                                "version_key": version_key
                                                            }
                                                    )


                        # sleep(delay)  
                        # print("sleep")  
                    else:
                        redis.remove_onebook_bet_details(onebook_run)  #remove the key from redis
                        break
                else:
                    redis.remove_onebook_bet_details(onebook_run)  #remove the key from redis when break the while loop
                    logger.info("There was something wrong with the onebook getBetDetail result")
                    return Response({'status': 'There was something wrong with the onebook getBetDetail result'}, status=status.HTTP_400_BAD_REQUEST)
            redis.remove_onebook_bet_details(onebook_run)  #remove the key from redis
            #print(redis.check_onebook_bet_details(onebook_run))        
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        else:
            logger.info("skip running this time for onebook getBetDetail.")
            return Response({'status': 'skip running this time onebook getBetDetail.'}, status=status.HTTP_200_OK)
    

    
 

@transaction.atomic
class GetBetDetail(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        try:
            PROVIDER = GameProvider.objects.get(provider_name=ONEBOOK_PROVIDER)
        except ObjectDoesNotExist:
            PROVIDER = GameProvider.objects.create(provider_name=ONEBOOK_PROVIDER,
                                        type=GAME_TYPE_SPORTS,
                                        market='letouCN, letouTH, letouVN',
                                        notes='2004')
            logger.error("PROVIDER AND/OR CATEGORY RELATIONS DO NOT EXIST.")
        headers =  {'Content-Type': 'application/x-www-form-urlencoded'}
        delay = kwargs.get("delay", 2)
        success = False
        version_key = GameProvider.objects.get(provider_name=ONEBOOK_PROVIDER).notes
        
        for x in range(0,3000):
            r = requests.post(ONEBOOK_API_URL + "GetBetDetail/", headers=headers, data={
                "vendor_id": ONEBOOK_VENDORID,
                "version_key": version_key,
            })
            rdata = r.json()
            logger.info(rdata)
            version_key = rdata["Data"]["last_version_key"]
            updates = GameProvider.objects.get(provider_name=ONEBOOK_PROVIDER)
            
            updates.notes = version_key
            updates.save()
            
            if  "BetDetails" in rdata['Data']:
                # logger.info(rdata["Data"]["BetDetails"])
                

                for i in range(len(rdata["Data"]["BetDetails"])):
                    username = str(rdata["Data"]["BetDetails"][i]["vendor_member_id"]).split('_')[0]
                    try:
                        cate = Category.objects.get(name='Sports')
                    except:
                        logger.error("missing sports game category.")
                    user = CustomUser.objects.get(username=username)
                    trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
                    if rdata["Data"]["BetDetails"][i]["settlement_time"] == None:
                        
                        GameBet.objects.get_or_create(provider=PROVIDER,
                                                    category=cate,
                                                    transaction_id=trans_id,
                                                    user=user,
                                                    user_name=user.username,
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
                                                    transaction_id=trans_id,
                                                    user=user,
                                                    user_name=user.username,
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
                logger.info("BetDetails does not exist.")
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
                    "vendor_member_id": username, # + '_test'
                })
                rdata = r.json()
                
                if r.status_code == 200:
                    success = True
                    break
                elif r.status_code == 204:
                    success = True
                    # Handle error
                    logger.info("Failed to complete a request for onebook createMember...")
                    logger.error(rdata)
                    return Response(rdata)
                elif r.status_code == 500:
                    logger.info("Request failed {} time(s)'.format(x+1)")
                    logger.info("Waiting for %s seconds before retrying again")
                    sleep(delay)
            if not success:
                return Response(rdata)
            try:
                Data = rdata['Data']
                if user.language == ('English' or 'en'):
                    lang = 'en'
                elif user.language == ('Chinese' or 'zh'):
                    lang = 'cs'
                elif user.language == ('Thai' or 'th'):
                    lang = 'th'
                elif user.language == ('Vietnamese' or 'vi'):
                    lang = 'vi'
                else:
                    lang = 'en'

                loginUrl = ONEBOOK_IFRAME_URL + 'token=' + Data + '&lang=' + lang
                return Response({"login_url":loginUrl})
            except NameError as e:
                logger.error(e)
                return Response({"error": "Cannot find the code for onebook login data."})

        except ObjectDoesNotExist as e:
            logger.error(e)
            return Response({"error": "Cannot find the user for onebook login."})

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
            tr2.text = 'User is not exist for onebook.'
            return HttpResponse(ET.tostring(root), content_type="text/xml")
        return HttpResponse(ET.tostring(root), content_type="text/xml")

      
def checkUserBalance(user):
    
    headers =  {'Content-Type': 'application/x-www-form-urlencoded'}
    delay = 5
    success = False
    for x in range(3):
        r = requests.post(ONEBOOK_API_URL + "CheckUserBalance/", headers=headers, data={
            "vendor_id": ONEBOOK_VENDORID,
            "vendor_member_ids": user.username, 
            "wallet_id": '1'
        })
        rdata = r.json()
        
        if r.status_code == 200:
            success = True
            break
        elif r.status_code == 204:
            success = True
            # Handle error
            logger.info("Failed to complete a request for onebook createMember...")
            logger.error(rdata)
            return Response(rdata)
        elif r.status_code == 500:
            logger.info("Request failed {} time(s)'.format(x+1)")
            logger.info("Waiting for %s seconds before retrying again")
            sleep(delay)
    if not success:
        return json.dumps(rdata)
    try:
        Data = rdata['Data']  
        balance = Data[0]["balance"]
        return json.dumps({"balance":balance})
    except:
        logger.error("Cannot find the data for onebook check user balance.")
        return json.dump({"error": "Cannot find the data for onebook check user balance."})
    
class test(View):
    def get(self, request, *args, **kwargs):
        user = CustomUser.objects.get(username="testdave123")
        
        #response = createMember(user, 13, "2")
        response = checkUserBalance(user)
        return HttpResponse(response)