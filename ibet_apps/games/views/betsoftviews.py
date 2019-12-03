from django.views import View
from django.db import DatabaseError
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.db import transaction
from users.views.helper import checkUserBlock
from users.models import CustomUser
import simplejson as json
from decimal import Decimal
import requests
from utils.constants import *
import random
import hashlib 
import logging
import datetime
from datetime import date
from django.utils import timezone
import uuid
from games.models import *
from accounting.models import * 
from utils.constants import *
from time import gmtime, strftime, strptime
import decimal
from django.core.exceptions import ObjectDoesNotExist
import xmltodict

logger = logging.getLogger("django")

key = "7HaBRQrlV8WqTmKJ"

gameId = 256
free_game_API: "https://claymoreasia-gp3.discreetgaming.com/free/en/launch.jsp?gameId={}&GAMESERVERURL=games-gp3.discreetgaming.com&autoplayAllowed=true&ShellPath=%252Ffree%252Fflash%252Fdefault%252Ftemplate.jsp&GAMESERVERID=1&LANG=en&BANKID=4542&SID=1_73d53af63e7b452140660000016ea4b2_VlAXUABRXl1VUEZRX1MLCQMCWFkcQ1lFVV5fSxdRAFwaBgYNCg".format(gameId)

def MD5(code):
    res = hashlib.md5(code.encode()).hexdigest()
    return res


class BetSoftAuthenticate(View):

    def get(self, request, *args, **kwargs):
        
        try:
            token = request.GET.get('token', '')
            hash = request.GET.get('hash', '')

            # print(str(token), str(hash))

            user = Token.objects.get(key=token).user
            
            user_id = user.username
            balance = int(user.main_wallet * 100)
            # print(user.username)
            if user.currency == CURRENCY_CNY:
                currency = "CNY"
            elif user.currency == CURRENCY_THB:
                currency == "THB"
            elif user.currency == CURRENCY_VND:
                currency == "VND"
            else:
                currency == "CNY"

            if hash == MD5(str(token) + key):
            
                response = {
                    "EXTSYSTEM": {
                        "REQUEST": {
                            "TOKEN": str(token),
                            "HASH": MD5(str(token) + key)
                        },
                        "TIME": strftime("%d %b %Y %H:%M:%S"),
                        "RESPONSE": {
                            "RESULT": "OK",
                            "USERID": user_id,
                            "USERNAME": user_id,
                            "FIRSTNAME": user.first_name,
                            "LASTNAME": user.last_name,
                            "EMAIL": user.email,
                            "CURRENCY": currency,
                            "BALANCE": balance
                        }
                    } 
                }
                response = xmltodict.unparse(response, pretty=True)
                # print(response) 
                return HttpResponse(response, content_type='text/xml')

            else:
                response = {
                    "EXTSYSTEM": {
                        "REQUEST": {
                            "TOKEN": str(token),
                            "HASH": MD5(str(token) + key)
                        },
                        "TIME": strftime("%d %b %Y %H:%M:%S"),
                        "RESPONSE": {
                            "RESULT": "ERROR",
                            "CODE": str(500)
                        }
                    } 
                }
                response = xmltodict.unparse(response, pretty=True)
                return HttpResponse(response, content_type='text/xml')

        except ObjectDoesNotExist as e:
            logger.error("Betsoft authenticate error: ", e)

            response = {
                "EXTSYSTEM": {
                    "REQUEST": {
                        "TOKEN": str(token),
                        "HASH": MD5(str(token) + key)
                    },
                    "TIME": strftime("%d %b %Y %H:%M:%S"),
                    "RESPONSE": {
                        "RESULT": "ERROR",
                        "CODE": str(400)
                    }
                } 
            }
            response = xmltodict.unparse(response, pretty=True)
            return HttpResponse(response, content_type='text/xml')
    

        except Exception as e:
            logger.error("Betsoft authenticate error: ", e)
            response = {
                "EXTSYSTEM": {
                    "REQUEST": {
                        "TOKEN": str(token),
                        "HASH": MD5(str(token) + key)
                        # "HASH": str(hash)+"7HaBRQrlV8WqTmKJ"
                    },
                    "TIME": strftime("%d %b %Y %H:%M:%S"),
                    "RESPONSE": {
                        "RESULT": "ERROR",
                        "CODE": str(399)
                    }
                } 
            }
            response = xmltodict.unparse(response, pretty=True)
            return HttpResponse(response, content_type='text/xml')
            


class BetSoftBetResult(View):


    def get(self, request, *args, **kwargs):

        user_id = request.GET.get('userId', '')
        bet = request.GET.get('bet', '')
        win = request.GET.get('win', '')
        round_id = request.GET.get('roundId', '')
        game_id = request.GET.get('gameId', '')
        is_round_finished = request.GET.get('isRoundFinished', '')
        hash = request.GET.get('hash', '')
        game_session_id = request.GET.get('gameSessionId', '')
        negative_bet = request.GET.get('negativeBet', '')
        client_type = request.GET.get('clientType', '')

        # print(user_id, bet, win, round_id, game_id, hash, game_session_id, negative_bet, client_type)

        response = {
            "EXTSYSTEM": {
                "REQUEST": {
                    "USERID": user_id,
                    "BET": bet,
                    "WIN": win,
                    "ROUNDID": round_id,
                    "GAMEID": game_id,
                    "ISROUNDFINISHED": is_round_finished,
                    "HASH": hash
                },
                "TIME": strftime("%d %b %Y %H:%M:%S"),
                "RESPONSE": {
                    "RESULT": "",
                    # "EXTSYSTEMTRANSACTIONID": "",
                    # "BALANCE": ""
                    # "BONUSBET": "bonusbet",
                    # "BONUSWIN": "bonuswin",
                }
            } 
        }

        win_amount = 0
        bet_amount = 0
        ref_id = ""

        try:

            user = CustomUser.objects.get(username=user_id)
            trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

            if win:
                win_list = win.split("|")
                win_amount = win_list[0]
                ref_id = win_list[1]
                with transaction.atomic():
                    user.main_wallet = decimal.Decimal((user.main_wallet * 100 + decimal.Decimal(win_amount)) / 100)
                    user.save()
                    GameBet.objects.get_or_create(provider=GameProvider.objects.get(provider_name="Betsoft"),
                                                    category=Category.objects.get(name='Slots'),
                                                    username=user,
                                                    amount_wagered=0.00,
                                                    currency=user.currency,
                                                    amount_won=decimal.Decimal(int(win_amount)/100),
                                                    market=ibetCN,
                                                    ref_no=ref_id,
                                                    transaction_id=trans_id
                                                    ) 


            if bet:
                bet_list = bet.split("|")
                bet_amount = bet_list[0]
                ref_id = bet_list[1]
                amount = bet_amount
                if int(bet_amount) > 1000000:
                    response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "FAILED"
                    response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(501)
                    response = xmltodict.unparse(response, pretty=True)
                    return HttpResponse(response, content_type='text/xml')

                if decimal.Decimal(user.main_wallet) * 100 < decimal.Decimal(bet_amount):
                    response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "FAILED"
                    response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(300)
                    response = xmltodict.unparse(response, pretty=True)
                    return HttpResponse(response, content_type='text/xml')

                with transaction.atomic():
                    user.main_wallet = decimal.Decimal((user.main_wallet * 100 - decimal.Decimal(bet_amount)) / 100)
                    user.save()
                    GameBet.objects.get_or_create(provider=GameProvider.objects.get(provider_name="Betsoft"),
                                                    category=Category.objects.get(name='Slots'),
                                                    username=user,
                                                    amount_wagered=decimal.Decimal(int(bet_amount)/100),
                                                    currency=user.currency,
                                                    amount_won=0.00,
                                                    market=ibetCN,
                                                    ref_no=ref_id,
                                                    transaction_id=trans_id
                                                    )
            
            if hash == MD5(user_id + bet + win + is_round_finished + round_id + game_id + key):

                # if win:
                #     win = win.split("|")
                #     win_amount = win[0]
                #     ref_id = win[1]
                #     with transaction.atomic():
                #         user.main_wallet = decimal.Decimal((user.main_wallet * 100 + decimal.Decimal(win_amount)) / 100)
                #         user.save()
                #         GameBet.objects.get_or_create(provider=GameProvider.objects.get(provider_name="Betsoft"),
                #                                         category=Category.objects.get(name='Slots'),
                #                                         username=user,
                #                                         amount_wagered=0.00,
                #                                         currency=user.currency,
                #                                         amount_won=decimal.Decimal(int(win_amount)/100),
                #                                         market=ibetCN,
                #                                         ref_no=ref_id,
                #                                         transaction_id=trans_id
                #                                         ) 


                # if bet:
                #     bet = bet.split("|")
                #     bet_amount = bet[0]
                #     ref_id = bet[1]
                #     amount = bet_amount
                #     if decimal.Decimal(user.main_wallet) * 100 < decimal.Decimal(bet_amount):
                #         response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "FAILED"
                #         response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(300)
                #         return HttpResponse(response, content_type='text/xml')

                #     with transaction.atomic():
                #         user.main_wallet = decimal.Decimal((user.main_wallet * 100 - decimal.Decimal(bet_amount)) / 100)
                #         user.save()
                #         GameBet.objects.get_or_create(provider=GameProvider.objects.get(provider_name="Betsoft"),
                #                                         category=Category.objects.get(name='Slots'),
                #                                         username=user,
                #                                         amount_wagered=decimal.Decimal(int(bet_amount)/100),
                #                                         currency=user.currency,
                #                                         amount_won=0.00,
                #                                         market=ibetCN,
                #                                         ref_no=ref_id,
                #                                         transaction_id=trans_id
                #                                         )
                
                response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "OK"
                response["EXTSYSTEM"]["RESPONSE"]["EXTSYSTEMTRANSACTIONID"] = trans_id
                response["EXTSYSTEM"]["RESPONSE"]["BALANCE"] = int(user.main_wallet * 100)
                response = xmltodict.unparse(response, pretty=True)
                return HttpResponse(response, content_type='text/xml')

            else:
                logger.info("Betsoft bet/result error with wrong hash validation")
                response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "FAILED"
                response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(500)
                response = xmltodict.unparse(response, pretty=True)
                return HttpResponse(response, content_type='text/xml')


        
        except ObjectDoesNotExist as e:
            logger.error("Betsoft bet/result error: ", e)
            response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "FAILED"
            response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(310)
            response = xmltodict.unparse(response, pretty=True)
            return HttpResponse(response, content_type='text/xml')

        except Exception as e:
            logger.error("Betsoft bet/result error: ", e)
            response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "FAILED"
            response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(399)
            response = xmltodict.unparse(response, pretty=True)
            return HttpResponse(response, content_type='text/xml')



class BetSoftBetRefund(View):

    def get(self, request, *args, **kwargs):

        user_id = request.GET.get('userId', '')
        casino_transaction_id = request.GET.get('casinoTransactionId', '')
        hash = request.GET.get('hash', '')

        # print(user_id, casino_transaction_id, hash)

        response = {
            "EXTSYSTEM": {
                "REQUEST": {
                    "USERID": user_id,
                    "CASINOTRANSACTIONID": casino_transaction_id,
                    "HASH": hash
                },
                "TIME": strftime("%d %b %Y %H:%M:%S"),
                "RESPONSE": {
                    "RESULT": ""
                }
            } 
        }

        try:
            user = CustomUser.objects.get(username=user_id)
            prev_bet = GameBet.objects.get(ref_no=casino_transaction_id)

            trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
            # user.amount
            # print(MD5(user_id + casino_transaction_id + key))

            if hash == MD5(user_id + casino_transaction_id + key):
                GameBet.objects.get_or_create(provider=GameProvider.objects.get(provider_name="Betsoft"),
                                                category=prev_bet.category,
                                                username=user,
                                                amount_wagered=0.00,
                                                currency=user.currency,
                                                amount_won=prev_bet.amount_wagered,
                                                market=ibetCN,
                                                ref_no=casino_transaction_id,
                                                transaction_id=trans_id
                                                )
                user.main_wallet = decimal.Decimal(((user.main_wallet + prev_bet.amount_wagered) * 100) / 100)
                user.save()
        
                response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "OK"
                response["EXTSYSTEM"]["RESPONSE"]["EXTSYSTEMTRANSACTIONID"] = trans_id

            else:

                response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "FAILED"
                response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(500)
            
            response = xmltodict.unparse(response, pretty=True)
            return HttpResponse(response, content_type='text/xml')

        except ObjectDoesNotExist as e:
            logger.error("Betsoft refund bet error invalid user: ", e)

            response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "FAILED"
            response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(310)
            response = xmltodict.unparse(response, pretty=True)
            return HttpResponse(response, content_type='text/xml')

        except Exception as e:
            logger.error("Betsoft refund bet error: ", e)
            response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "FAILED"
            response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(399)
            response = xmltodict.unparse(response, pretty=True)
            return HttpResponse(response, content_type='text/xml')



# class BetBalance(View):

#     def get(self, request, *args, **kwargs):
        
#         user_id = request.GET.get('userId', '')
#         response = {
#             "EXTSYSTEM": {
#                 "REQUEST": {
#                     "USERID": user_id
#                 },
#                 "TIME": strftime("%d %b %Y %H:%M:%S"),
#                 "RESPONSE": {
#                     "RESULT": ""
#                 }
#             } 
#         }
        
#         try:
#             user = CustomUser.objects.get(username=user_id)
#             balance = user.main_wallet

#             response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "OK"
#             response["EXTSYSTEM"]["RESPONSE"]["BALANCE"] = balance

#             response = xmltodict.unparse(response, pretty=True)
#             return HttpResponse(response, content_type='text/xml')
            

#         except ObjectDoesNotExist as e:
#             logger.info("Betsoft get balance error invalid user: ", e)


#             response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "FAILED"
#             response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(310)
#             response = xmltodict.unparse(response, pretty=True)
#             return HttpResponse(response, content_type='text/xml')

#         except Exception as e:
#             logger.error("Betsoft get balance error: ", e)

#             response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "FAILED"
#             response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(399)
#             response = xmltodict.unparse(response, pretty=True)
#             return HttpResponse(response, content_type='text/xml')



class BetSoftGetInfo(View):

    def get(self, request, *args, **kwargs):

        user_id = request.GET.get('userId', '')
        hash = request.GET.get('hash', '')

        response = {
            "EXTSYSTEM": {
                "REQUEST": {
                    "USERID": user_id,
                    "HASH": hash

                },
                "TIME": strftime("%d %b %Y %H:%M:%S"),
                "RESPONSE": {
                    "RESULT": ""
                }
            } 
        }

        try:
            user = CustomUser.objects.get(username=user_id)
            trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

            if user.currency == CURRENCY_CNY:
                currency = "CNY"
            elif user.currency == CURRENCY_THB:
                currency == "THB"
            elif user.currency == CURRENCY_VND:
                currency == "VND"
            else:
                currency == "CNY"


            if hash == MD5(user_id + key):

                response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "OK"
                response["EXTSYSTEM"]["RESPONSE"]["USERNAME"] = user.username
                response["EXTSYSTEM"]["RESPONSE"]["FIRSTNAME"] = user.first_name
                response["EXTSYSTEM"]["RESPONSE"]["LASTNAME"] = user.last_name
                response["EXTSYSTEM"]["RESPONSE"]["EMAIL"] = user.email
                response["EXTSYSTEM"]["RESPONSE"]["CURRENCY"] = currency

            else:

                response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "ERROR"
                response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(500)
            
            response = xmltodict.unparse(response, pretty=True)
            return HttpResponse(response, content_type='text/xml')

        
        except ObjectDoesNotExist as e:
            logger.error("Betsoft get info error invalid user: ", e)
            response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "ERROR"
            response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(310)
            response = xmltodict.unparse(response, pretty=True)
            return HttpResponse(response, content_type='text/xml')

        except Exception as e:
            logger.error("Betsoft refund bet error: ", e)
            response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "ERROR"
            response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(399)
            response = xmltodict.unparse(response, pretty=True)
            return HttpResponse(response, content_type='text/xml')



# class BonusRelease(View):

#     def get(self, request, *args, **kwargs):

#         user_id = request.GET.get('userId', '')
#         bonus_id = request.GET.get('bonusId', '')
#         amount = request.GET.get('amount', '')
#         hash = request.GET.get('hash', '')

#         # print(user_id, bonus_id, amount, hash)

#         response = {
#             "EXTSYSTEM": {
#                 "REQUEST": {
#                     "USERID": user_id,
#                     "BONUSID": bonus_id,
#                     "AMOUNT": amount,
#                     "HASH": hash
#                 },
#                 "TIME": strftime("%d %b %Y %H:%M:%S"),
#                 "RESPONSE": {
#                     "RESULT": ""
#                 }
#             } 
#         }

#         try:
#             user = CustomUser.objects.get(username=user_id)
#             trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

#             if hash == MD5(user_id + bonus_id + amount + key):
#                 response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "OK"
#             else:

#                 response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "ERROR"
#                 response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(500)
            
#             response = xmltodict.unparse(response, pretty=True)
#             return HttpResponse(response, content_type='text/xml')

#         except ObjectDoesNotExist as e:
#             logger.info("Betsoft release bonus error invalid user: ", e)
#             response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "ERROR"
#             response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(310)
#             response = xmltodict.unparse(response, pretty=True)
#             return HttpResponse(response, content_type='text/xml')

#         except Exception as e:
#             logger.error("Betsoft release bonus error: ", e)
#             response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "ERROR"
#             response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(399)
#             response = xmltodict.unparse(response, pretty=True)
#             return HttpResponse(response, content_type='text/xml')



# class BonusWin(View):

#     def get(self, request, *args, **kwargs):

#         user_id = request.GET.get('userId', '')
#         bonus_id = request.GET.get('bonusId', '')
#         amount = request.GET.get('amount', '')
#         transaction_id = request.GET.get('transactionId', '')
#         hash = request.GET.get('hash', '')

#         response = {
#             "EXTSYSTEM": {
#                 "REQUEST": {
#                     "USERID": user_id,
#                     "BONUSID": bonus_id,
#                     "AMOUNT": amount,
#                     "TRANSACTIONID": transaction_id,
#                     "HASH": hash
#                 },
#                 "TIME": strftime("%d %b %Y %H:%M:%S"),
#                 "RESPONSE": {
#                     "RESULT": ""
#                 }
#             } 
#         }

#         try:
#             user = CustomUser.objects.get(username=user_id)
#             trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

#             if hash == MD5(user_id + key):
#                 new_amount = user.main_wallet + amount
#                 user.main_wallet = new_amount
#                 user.save()

#                 response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "OK"
#                 response["EXTSYSTEM"]["RESPONSE"]["BALANCE"] = new_amount

#             else:

#                 response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "ERROR"
#                 response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(500)
            
#             response = xmltodict.unparse(response, pretty=True)
#             return HttpResponse(response, content_type='text/xml')

#         except ObjectDoesNotExist as e:
#             logger.info("Betsoft release bonus error invalid user: ", e)
#             response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "ERROR"
#             response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(310)
#             response = xmltodict.unparse(response, pretty=True)
#             return HttpResponse(response, content_type='text/xml')

#         except Exception as e:
#             logger.error("Betsoft release bonus error: ", e)
#             response["EXTSYSTEM"]["RESPONSE"]["RESULT"] = "ERROR"
#             response["EXTSYSTEM"]["RESPONSE"]["CODE"] = str(399)
#             response = xmltodict.unparse(response, pretty=True)
#             return HttpResponse(response, content_type='text/xml')

            

            




LAUNCH_URL = "https://claymoreasia-gp3.discreetgaming.com/cwstartgamev2.do?bankId={}&gameId={}&mode=real&token={}&lang=en"
# LAUNCH_URL = "https://claymoreasia-gp3.discreetgaming.com/cwstartgamev2.do?bankId=4542&gameId=514&mode=real&token=4a898cf9e3715eb771f7542b61d03f05d18833b2&lang=en"
BANKID="4542"
# GAMEID = "514"
# TOKEN = "4a898cf9e3715eb771f7542b61d03f05d18833b2"
# print(LAUNCH_URL.format(BANKID, GAMEID, TOKEN))

LAUNCH_GUST_URL = "https://claymoreasia-gp3.discreetgaming.com/cwguestlogin.do?bankId={}&gameId={}&lang=en"



# called by frontend
class BetsoftGameLaunch(View):

    def get(self, request, *args, **kwargs):

        try:
            gameId = request.GET.get('gameId', '')
            token = request.GET.get('token', '')

            if token:

                url = LAUNCH_URL.format(BANKID, gameId, token)
                rr = requests.get(url)
            
            else:

                url = LAUNCH_GUST_URL.format(BANKID, gameId)
                rr = requests.get(url)
            
            rr = rr.text    
            return HttpResponse(rr)

        except:
            logger.error("There is something wrong when lunch the BETSOFT game")
            return HttpResponse(status=400)