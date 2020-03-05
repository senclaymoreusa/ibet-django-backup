from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import HttpResponse
from decimal import Decimal
from django.db import IntegrityError, DatabaseError, transaction
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from utils.aws_helper import getThirdPartyKeys
from utils.constants import *
from users.models import CustomUser
from games.models import *
import datetime
from datetime import date
from django.utils import timezone

import os
import json
import math
import uuid
import logging
import requests

logger = logging.getLogger("django")

apiUrl = qt["API"]["url"]

class VerifySession(APIView):
    permission_classes = (AllowAny,)

    """
    This API is to validate and verify the player session every time the player launches a game.
    """

    def get(self, request, *args, **kwargs):
        session = request.META.get('HTTP_WALLET_SESSION')
        pass_key = request.META.get('HTTP_PASS_KEY')
        username = self.kwargs.get('playerId')
        status_code = 500
        code = QT_STATUS_CODE[QT_STATUS_UNKNOWN_ERROR][1]
        message = "Unexpected error"

        if pass_key != QT_PASS_KEY:
            status_code = 401
            code = QT_STATUS_CODE[QT_STATUS_LOGIN_FAILED][1]
            message = "The given pass-key is incorrect"
            logger.error("Incorrect pass key")
            
            response = {
                "code": code,
                "message": message,
            }
            return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
            
        
        is_not_varified = False
        
        try:
            user = CustomUser.objects.get(username=username)
            
            if user.block:
                is_not_varified = True
                status_code = 403
                code = QT_STATUS_CODE[QT_STATUS_ACCOUNT_BLOCKED][1]
                message = "The player account is blocked"
                
                logger.error("Player {} is blocked".format(username))
            
        except Exception as e:
            is_not_varified = True
            status_code = 401
            code = QT_STATUS_CODE[QT_STATUS_LOGIN_FAILED][1]
            message = "The player, {}, does not exist".format(username)
            
            logger.error(message + ": " + str(e))
        
        if is_not_varified:
            response = {
                "code": code,
                "message": message,
            }
            return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
        
        try:
            qt_session = QTSession.objects.get(Q(user=user) & Q(session_key=session))
            
            if not qt_session.valid:
                is_not_varified = True
                status_code = 400
                code = QT_STATUS_CODE[QT_STATUS_INVALID_TOKEN][1]
                message = "Session-token is invalid!"
                logger.error("Session-token is invalid!")
            
        except Exception as e:
            is_not_varified = True
            status_code = 400
            code = QT_STATUS_CODE[QT_STATUS_INVALID_TOKEN][1]
            message = "Session-token is expired or missing"
            logger.error(message + ": " + str(e))
        
        if is_not_varified:
            response = {
                "code": code,
                "message": message,
            }
            return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
        
        
        status_code = 200
        n_float = int(user.main_wallet * 100) / 100.0
        bal = Decimal(n_float)
        
        response = {
            'balance': round(bal),
            'currency': CURRENCY_CHOICES[user.currency][1],
        }
        
        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder),
                            content_type='application/json', status=status_code)
                
            
class GetBalance(APIView):
    permission_classes = (AllowAny,)

    """
    This API is for QT wallet to get user balance.
    """

    def get(self, request, *args, **kwargs):
        http_session = request.META.get('HTTP_WALLET_SESSION')
        pass_key = request.META.get('HTTP_PASS_KEY')
        username = self.kwargs.get('playerId')
        status_code = 500
        code = QT_STATUS_CODE[QT_STATUS_UNKNOWN_ERROR][1]
        message = "Unexpected error"
        
        if pass_key != QT_PASS_KEY:
            status_code = 401
            code = QT_STATUS_CODE[QT_STATUS_LOGIN_FAILED][1]
            message = "The given pass-key is incorrect"
            logger.error("Incorrect pass key")
            
            response = {
                "code": code,
                "message": message,
            }
            return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
        
        try:
            prov = GameProvider.objects.get(provider_name="QTech")
            cat = Category.objects.get(name='Games')
            user = CustomUser.objects.get(username=username)
            
            status_code = 200
            n_float = int(user.main_wallet * 100) / 100.0
            bal = Decimal(n_float)
            response = {
                'balance': round(bal),
                'currency': CURRENCY_CHOICES[user.currency][1],
            }
            
            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json',
                                status=status_code)
            
        except Exception as e:
            status_code = 400
            code = QT_STATUS_CODE[QT_STATUS_REQUEST_DECLINED][1]
            message = "General error. Request could not be processed."
            logger.error("Error getting game category/provider/user: " + str(e))
        
            response = {
                "code": code,
                "message": message,
            }
            return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
        

class GameLaunch(APIView):

    permission_classes = (AllowAny, )
    
    
    def post(self, request, *args, **kwargs):
        # headers = {'Content-Type': 'x-www-form-urlencoded'}
        
        try:
            tr = requests.post(apiUrl + "v1/auth/token", params={
                'grant_type': 'password',
                'response_type': 'token',
                'username': qt['API']['username'],
                'password': qt['API']['password'],
            })
            
            authData = tr.json()
            
            if tr.status_code == 200:
                logger.info("Authentication granted!")
                access_token = authData['access_token']
                 
                headers = {
                    'Authorization': 'Bearer ' + access_token,
                    'Content-Type': 'application/json'   
                }
                
                gameId = request.GET.get('gameId')
                mode = request.GET.get('mode')
                
                if mode == 'real':
                    username = request.GET.get('playerId')
                    
                    try: 
                        user = CustomUser.objects.get(username=username)
                        
                        newKey = uuid.uuid4()
                        try:
                            valSess = QTSession.objects.get(Q(user=user) & Q(valid=True)) 
                            previousKey = valSess.session_key
                            valSess.session_key = newKey
                            valSess.save()
                            logger.info("Assign a new valid session key for " + username)
                            
                            try:
                                falseSess = QTSession.objects.get(Q(user=user) & Q(valid=False)) 
                                falseSess.session_key = previousKey
                                falseSess.save()
                            except:
                                QTSession.objects.create(user=user,session_key=previousKey,valid=False)
                                
                            logger.info("Update previous session to invalid!")
                        except:
                            logger.info("Create a new session for " + username)
                            QTSession.objects.create(user=user,session_key=newKey,valid=True)
                        
                        body = {
                            "playerId": username,
                            "currency": CURRENCY_CHOICES[user.currency][1],
                            "walletSessionId": str(newKey),
                            "country": "CN", # user.country
                            "lang": "zh_CN", # user.language,
                            "mode": 'real',
                            "device": "desktop", 
                        }
                        
                    except Exception as e: 
                        logger.error("Failed in getting user " + str(e))
                        
                else: 
                    body = {
                        "country": "CN", 
                        "lang": "zh_CN",
                        "mode": 'demo',
                        "currency": 'CNY',
                        "device": "desktop", 
                    }
                
                url = apiUrl + "v1/games/" + gameId + "/launch-url"
                #url = apiUrl + "v1/games/TK-froggrog/launch-url"
                r = requests.post( url, headers=headers, data=json.dumps(body) )
                launchData = r.json()  
                
                if r.status_code != 200:
                    logger.error(launchData)
                
                return HttpResponse(r, content_type='application/json', status=r.status_code)
                    
            else:
                logger.error(authData)
                return HttpResponse(tr)
            
        except Exception as e:
            logger.error("Error: " + str(e))
            return HttpResponse(tr)
            
#         except requests.exceptions.HTTPError as he:
#             logger.error("HTTP Error: " + str(he))
#         except requests.exceptions.ConnectionError as ce:
#             logger.error("Connection Error: " + str(ce))
#         except requests.exceptions.Timeout as te:
#             logger.error("Timeout: " + str(te))
#         except requests.exceptions.RequestException as err:
#             logger.error("Oops: " + str(err))
    

class ProcessTransactions(APIView):

    permission_classes = (AllowAny, )
    
    
    def post(self, request, *args, **kwargs):
        """
        Transactions: Deposit and Withdraw
        """
        status_code = 500
        code = QT_STATUS_CODE[QT_STATUS_UNKNOWN_ERROR][1]
        message = "Unexpected error"
        
        http_session = request.META.get('HTTP_WALLET_SESSION')
        pass_key = request.META.get('HTTP_PASS_KEY')
        
        if pass_key != QT_PASS_KEY:
            status_code = 401
            message = 'The given pass-key is incorrect'
            logger.error(message) 
            
            response = {
                "code": QT_STATUS_CODE[QT_STATUS_LOGIN_FAILED][1],
                "message": message
            }
            
            return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
        
        body = json.loads(request.body)
        for i in ['category','device']:
            if not i in body:
                body[i] = ''
        
        try:
            playerId = body['playerId']
            txnId = body['txnId']
            gameId = body["gameId"]
            roundId = body['roundId']
            transType = body["txnType"]
            currency = body["currency"]
            created = body['created'] # timestamp
            completed = body['completed'] # true / false
            amount = body["amount"]
            amount = Decimal(amount)
        except:
            status_code = 400
            message = 'One or more required payload parameters are missing'
            logger.error(message) 
            
            response = {
                "code": "REQUEST_DECLINED",
                "message": "General error: " + message
            }
            
            return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
        
        try:
            user = CustomUser.objects.get(username=playerId)
            qt_session = QTSession.objects.get(Q(user=user) & Q(session_key=http_session))
            prov = GameProvider.objects.get(provider_name="QTech")
            cat = Category.objects.get(name='Games')
            
            if transType == "DEBIT" and not qt_session.valid:
                status_code = 400
                message = 'Invalid player (wallet) session-token'
                logger.error(message) 
                
                response = {
                    "code": QT_STATUS_CODE[QT_STATUS_INVALID_TOKEN][1],
                    "message": message
                }
                
                return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)

            elif user.block:
                status_code = 403
                message = "The player account is blocked"
                logger.error("Blocked user {} trying to access QT Game".format(username))
                
                response = {
                    "code": QT_STATUS_CODE[QT_STATUS_ACCOUNT_BLOCKED][1],
                    "message": message
                }
                
                return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
                
        except Exception as e:
            status_code = 401
            message = 'Missing user or session-token'
            logger.error(message + ": " + str(e)) 
            
            response = {
                "code": QT_STATUS_CODE[QT_STATUS_LOGIN_FAILED][1],
                "message": message
            }
            
            return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
        
        try:
            #
            # try to find if the txnId exists
            #
            rows = GameBet.objects.filter(  provider=prov,
                                            category=cat,
                                            user=user,
                                            user_name = user.username,
                                            currency=user.currency,
                                            market=ibetCN,
                                            ref_no=txnId
                                            )
            
            if rows.count() > 0:
                n_float = int(user.main_wallet * 100) / 100.0
                bal = Decimal(n_float)
                record = rows[0]
                
                response = {
                    'balance': round(bal),
                    "referenceId": record.transaction_id
                }
                logger.info("No transaction for ref_no, {}, for reason of idempotency".format(txnId))
                
                return HttpResponse(json.dumps(response), content_type='application/json', status=201)
        
        except:
            logger.warning('Filter gamebet exception: ' + str(e))
        
        logger.info("ref_no, {}, is a new transaction".format(txnId))        
        trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
        
        if transType == "DEBIT":
            bal = user.main_wallet - amount
            
            if bal > 0: 
                # user has enough funds
                try:
                    with transaction.atomic():
                        bet = GameBet(
                            provider=prov,
                            category=cat,
                            user=user,
                            user_name = user.username,
                            ref_no=txnId,
                            amount_wagered=amount,
                            transaction_id=trans_id,
                            currency=user.currency,
                            market=ibetCN,
                            other_data={
                                'txnType': transType,
                                'completed': completed, 
                                'roundId': roundId, 
                                'category': body['category'],
                                'device': body['device']
                            }
                        )
                        user.main_wallet = bal
                        bet.save()
                        user.save()
                        
                    n_float = int(bal * 100) / 100.0
                    bal = Decimal(n_float)
                    
                    response = {
                        'balance': round(bal),
                        "referenceId": trans_id
                    }
                    
                    status_code = 201
                    
                except (DatabaseError, IntegrityError) as e:
                    logger.error(repr(e))
                
                    response = {
                        "code": "UNKNOWN_ERROR",
                        "message": "DEBIT unexpected error"
                    }
            else: 
                response = {
                    "code": "INSUFFICIENT_FUNDS",
                    "message": "Not enough funds for the debit operation"
                }
                status_code = 400
                
            logger.info("Done processing DEBIT")
        elif transType == "CREDIT":
            user.main_wallet += amount
            
            try:
                with transaction.atomic():
                    bet = GameBet(
                        provider=prov,
                        category=cat,
                        user=user,
                        user_name = user.username,
                        ref_no=txnId,
                        amount_won=amount,
                        resolved_time=timezone.now(),
                        outcome=0,
                        transaction_id=trans_id,
                        currency=user.currency,
                        market=ibetCN,
                        other_data={
                            'txnType': transType,
                            'completed': completed, 
                            'roundId': roundId, 
                            'category': body['category'],
                            'device': body['device']
                        }
                    )
                    bet.save()
                    user.save()
                    
                n_float = int(user.main_wallet * 100) / 100.0
                bal = Decimal(n_float)
                
                response = {
                    'balance': round(bal),   
                    "referenceId": trans_id
                }
                
                status_code = 201
                
            except (DatabaseError, IntegrityError) as e:
                logger.error(repr(e))
            
                response = {
                    "code": "UNKNOWN_ERROR",
                    "message": "CREDIT unexpected error"
                }
                
            logger.info("Done processing CREDIT")
        else:
            response = {
                "code": "REQUEST_DECLINED",
                "message": "Invalid transaction type: " + transType
            }
            status_code = 400
            
        return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
    

class ProcessRollback(APIView):

    permission_classes = (AllowAny, )
    
    
    def post(self, request, *args, **kwargs):
        """
        Transactions: Deposit and Withdraw
        """
        status_code = 500
        message = ''
        
        http_session = request.META.get('HTTP_WALLET_SESSION')
        pass_key = request.META.get('HTTP_PASS_KEY')
        
        if pass_key != QT_PASS_KEY:
            status_code = 401
            message = 'The given pass-key is incorrect'
            logger.error(message) 
            
            response = {
                "code": QT_STATUS_CODE[QT_STATUS_LOGIN_FAILED][1],
                "message": message
            }
            
            return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
        
        body = json.loads(request.body)
        for i in ['category','device']:
            if not i in body:
                body[i] = ''
        
        try:
            playerId = body['playerId']
            txnId = body['txnId']
            gameId = body["gameId"]
            currency = body["currency"]
            created = body['created'] # timestamp
            completed = body['completed'] # true / false
            amount = body["amount"]
            amount = Decimal(amount)
            orig_txnId = body['betId']
            
        except:
            status_code = 400
            message = 'One or more required payload parameters are missing'
            logger.error(message) 
            
            response = {
                "code": "REQUEST_DECLINED",
                "message": message
            }
            
            return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
        
        try:
            user = CustomUser.objects.get(username=playerId)
            prov = GameProvider.objects.get(provider_name="QTech")
            cat = Category.objects.get(name='Games')
            
            if user.block:
                status_code = 403
                message = "The player account is blocked"
                logger.error("Blocked user {} trying to access QT Game".format(username))
                
                response = {
                    "code": QT_STATUS_CODE[QT_STATUS_ACCOUNT_BLOCKED][1],
                    "message": message
                }
                
                return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
            
            try: 
                qt_session = QTSession.objects.get(Q(user=user) & Q(session_key=http_session))
                
                if not qt_session.valid:
                    message = 'Expired (wallet) session being used for rollback!'
                    logger.info(message) 
                
            except Exception as e:
                message = 'Player (wallet) session Missing but proceed with rollback!'
                logger.info(message) 
            
        except:
            status_code = 400
            message = 'PLAYER_NOT_FOUND'
            logger.error(message) 
            
            response = {
                "code": QT_STATUS_CODE[QT_STATUS_INVALID_TOKEN][1],
                "message": message
            }
            
            return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
        
        try:
            #
            # try to find if the txnId exists
            #
            rows = GameBet.objects.filter(  provider=prov,
                                            category=cat,
                                            user=user,
                                            user_name = user.username,
                                            currency=user.currency,
                                            market=ibetCN,
                                            ref_no=txnId
                                            )
            if rows.count() > 0:
                n_float = int(user.main_wallet * 100) / 100.0
                bal = Decimal(n_float)
                record = rows[0]
                
                response = {
                    'balance': round(bal),
                    "referenceId": record.transaction_id
                }
                logger.info("No transaction for ref_no, {}, for reason of idempotency".format(txnId))
                
                return HttpResponse(json.dumps(response), content_type='application/json', status=201)
        
        except Exception as e:
            logger.warning('Filter gamebet exception: ' + str(e))
            
        logger.info("ref_no, {}, is a new transaction".format(txnId))
        
        trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))  
        
        
        try:
            #
            # try to find the original QT txnId for rollback
            #
            rows = GameBet.objects.filter(  provider=prov,
                                            category=cat,
                                            user=user,
                                            user_name = user.username,
                                            currency=user.currency,
                                            market=ibetCN,
                                            ref_no=orig_txnId
                                            )
            
            if rows.count() > 0:
                logger.info("Rollback from original txnId=" + orig_txnId)
                
                user.main_wallet += amount
                n_float = int(user.main_wallet * 100) / 100.0
                bal = Decimal(n_float)
                
                response = {
                    'balance': round(bal),
                    "referenceId": trans_id
                }
            else:
                logger.warning("No rollback due to original txnId, {}, NOT found".format(orig_txnId))
                
                n_float = int(user.main_wallet * 100) / 100.0
                bal = Decimal(n_float)
                response = {
                    'balance': round(bal)
                }
                
                return HttpResponse(json.dumps(response), content_type='application/json', status=201)
                 
            
        except Exception as e:
            logger.warning('No rollback: Filter gamebet exception: ' + str(e))
            
            n_float = int(user.main_wallet * 100) / 100.0
            bal = Decimal(n_float)
            response = {
                "balance": round(bal)
            }
            
            return HttpResponse(json.dumps(response), content_type='application/json', status=201)
        
        try:
            with transaction.atomic():
                bet = GameBet(
                    provider=prov,
                    category=cat,
                    user=user,
                    user_name = user.username,
                    ref_no=txnId,
                    amount_wagered=0.00,
                    amount_won=amount,
                    transaction_id=trans_id,
                    outcome=3,
                    resolved_time=timezone.now(),
                    currency=user.currency,
                    market=ibetCN,
                    other_data={
                        'transactionType': "RollBack",
                        'rollBackFrom': orig_txnId,
                        'completed': completed, 
                        'category': body['category'],
                        'device': body['device']
                    }
                )
                bet.save()
                user.save()
            
            status_code = 200
            
        except (DatabaseError, IntegrityError) as e:
            logger.error(repr(e))
        
            response = {
                "code": "UNKNOWN_ERROR",
                "message": "Unexpected error"
            }
        
        
        
        return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
        
        
