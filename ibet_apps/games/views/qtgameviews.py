from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import HttpResponse

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from utils.constants import *
from users.models import CustomUser
from games.models import *

import logging

logger = logging.getLogger("django")


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
                    qt_session = QTSession.objects.get(Q(user=user)&Q(session_key=str(session)))
                    if qt_session.valid:
                        status_code = 200
                        response = {
                            'balance': round(user.main_wallet, 2),
                            # TODO: needs to handle if user.currency is bitcoin
                            'currency': CURRENCY_CHOICES[user.currency][1],
                        }
                        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json', status=status_code)

            except Exception as e:
                status_code = 400
                code = QT_STATUS_CODE[QT_STATUS_INVALID_TOKEN][1]
                message = "Missing, invalid or expired player (wallet) session token."
                logger.info("Error getting user or user session " + str(e))

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
                    'balance': round(user.main_wallet, 2),
                    # TODO: needs to handle if user.currency is bitcoin
                    'currency': CURRENCY_CHOICES[user.currency][1],
                }
                return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json', status=status_code)

            except Exception as e:
                status_code = 400
                code = QT_STATUS_CODE[QT_STATUS_REQUEST_DECLINED][1]
                message = "General error. If request could not be processed."
                logger.info("Error getting user " + str(e))

        response = {
            "code": code,
            "message": message,
        }
        return HttpResponse(json.dumps(response), content_type='application/json', status=status_code)
