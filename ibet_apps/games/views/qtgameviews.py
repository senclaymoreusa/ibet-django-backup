from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import HttpResponse

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from utils.aws_helper import getThirdPartyKeys
from utils.constants import *
from users.models import CustomUser
from games.models import *

import os
import json
import logging
import requests

logger = logging.getLogger("django")

# connect AWS S3
bucket = 'ibet-admin-apdev'
if 'ENV' in os.environ and os.environ["ENV"] == 'approd':
    bucket = 'ibet-admin-approd'
third_party_keys = getThirdPartyKeys(bucket, "config/thirdPartyKeys.json")
QT_PASS_KEY = third_party_keys["QTGAMES"]["PASS_KEY"]

qt = third_party_keys["QTGAMES"]
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
        message = ""

        if pass_key != QT_PASS_KEY:
            status_code = 401
            code = QT_STATUS_CODE[QT_STATUS_LOGIN_FAILED][1]
            message = "The given pass-key is incorrect."
            logger.info("Error given pass key from QT wallet!")
        else:
            try:
                user = CustomUser.objects.get(username=username)
                if user.block:
                    status_code = 403
                    code = QT_STATUS_CODE[QT_STATUS_ACCOUNT_BLOCKED][1]
                    message = "The player account is blocked."
                    logger.info("Blocked user {} trying to access QT Game".format(username))
                else:
                    qt_session = QTSession.objects.get(Q(user=user) & Q(session_key=session))

                    if qt_session.valid:
                        status_code = 200
                        response = {
                            'balance': "{0:0.2f}".format(int(user.main_wallet * 100)/100.0),
                            # TODO: needs to handle if user.currency is bitcoin
                            'currency': CURRENCY_CHOICES[user.currency][1],
                        }
                        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder),
                                            content_type='application/json', status=status_code)
                    else:
                        status_code = 400
                        code = QT_STATUS_CODE[QT_STATUS_INVALID_TOKEN][1]
                        message = "Missing, invalid or expired player (wallet) session token."

            except Exception as e:
                logger.error("Error getting user or user session " + str(e))

        response = {
            "code": code,
            "message": message,
        }
        return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)


class GetBalance(APIView):
    permission_classes = (AllowAny,)

    """
    This API is for QT wallet to get user balance.
    """

    def get(self, request, *args, **kwargs):
        pass_key = request.META.get('HTTP_PASS_KEY')
        username = self.kwargs.get('playerId')
        status_code = 500
        code = QT_STATUS_CODE[QT_STATUS_UNKNOWN_ERROR][1]
        message = ""

        if pass_key != QT_PASS_KEY:
            status_code = 401
            code = QT_STATUS_CODE[QT_STATUS_LOGIN_FAILED][1]
            message = "The given pass-key is incorrect."
            logger.info("Error given pass key from QT wallet!")
        else:
            try:
                user = CustomUser.objects.get(username=username)
                status_code = 200
                response = {
                    'balance': "{0:0.2f}".format(int(user.main_wallet * 100)/100.0),
                    # TODO: needs to handle if user.currency is bitcoin
                    'currency': CURRENCY_CHOICES[user.currency][1],
                }
                return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json',
                                    status=status_code)

            except Exception as e:
                status_code = 400
                code = QT_STATUS_CODE[QT_STATUS_REQUEST_DECLINED][1]
                message = "General error. If request could not be processed."
                logger.error("Error getting user " + str(e))

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
                username = request.GET.get('playerId')
                mode = request.GET.get('mode')
                
                try: 
                    user = CustomUser.objects.get(username=username)
                    session = QTSession.objects.get(user=user)
                except Exception as e: 
                    logger.error("Failed in getting user/session " + str(e))
                    mode = 'demo'
                
                if mode == 'real':
                    body = {
                        "playerId": username,
                        "currency": CURRENCY_CHOICES[user.currency][1],
                        "walletSessionId": str(session.session_key),
                        "country": "CN", # user.country
                        "lang": "zh_CN", # user.language,
                        "mode": mode,
                        "device": "desktop", 
                    }
                else: 
                    body = {
                        "country": "CN", 
                        "lang": "zh_CN",
                        "mode": mode,
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
                return Response(tr)
            
        except Exception as e:
            logger.error("Error: " + str(e))
            return Response(tr)
            
#         except requests.exceptions.HTTPError as he:
#             logger.error("HTTP Error: " + str(he))
#         except requests.exceptions.ConnectionError as ce:
#             logger.error("Connection Error: " + str(ce))
#         except requests.exceptions.Timeout as te:
#             logger.error("Timeout: " + str(te))
#         except requests.exceptions.RequestException as err:
#             logger.error("Oops: " + str(err))
    
     
