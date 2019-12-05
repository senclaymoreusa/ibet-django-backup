
from games.helper import transferRequest
from django.views import View
from django.db import DatabaseError
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder  
from django.conf import settings
from django.db import transaction
from users.views.helper import checkUserBlock
from users.models import CustomUser
import simplejson as json
import xmltodict
from decimal import Decimal
import requests
import logging
import datetime
from datetime import date
from django.utils import timezone
import uuid
from games.models import *
from accounting.models import * 
from utils.constants import *


logger = logging.getLogger('django')


class Transfer(View):

    def post(self, request, *args, **kwargs):
        try:
            body = json.loads(request.body)
            
            user_id = body["user_id"]
            from_wallet = body["from_wallet"]
            to_wallet = body["to_wallet"]
            amount = body["amount"]

            user = CustomUser.objects.get(pk=user_id)

            from_wallet_field_name = from_wallet + '_wallet'
            current_from_wallet_amount = getattr(user, from_wallet_field_name)

            if float(current_from_wallet_amount) < float(amount):

                response = {
                    "status_code": ERROR_CODE_FAIL,
                    "error_message": "Balance is not enough"
                }

                logger.info("Balance is not enough => transfer money from" + str(from_wallet) + " " + str(to_wallet))

            elif transferRequest(user, amount, from_wallet, to_wallet):
                response = {
                    "status_code": CODE_SUCCESS,
                    "error_message": "Successfully transfer"
                }

                logger.info("Successfully transfer money from" + str(from_wallet) + " " + str(to_wallet))

            else:

                response = {
                    "status_code": ERROR_CODE_FAIL,
                    "error_message": "Transfer fail"
                }

                logger.info("Fail to transfer money from" + str(from_wallet) + " " + str(to_wallet))

            
            return HttpResponse(json.dumps(response), content_type='application/json')

        except Exception as e:
            logger.error("Request transfer error: ", e)
            return HttpResponse(status=400)




class EachWalletAmount(View):

    def get(self, request, *args, **kwargs):

        response = []
        
        try:
            user_id = request.GET.get('user_id')
            user = CustomUser.objects.get(pk=user_id)
            response = [
                {
                    "code": "main",
                    "amount":  "%.2f" % user.main_wallet,
                    "isMain": "true"
                },
                {
                    "code": "ea",
                    "amount":  "%.2f" % user.ea_wallet,
                    "isMain": "false"
                },
                {
                    "code": "onebook",
                    "amount":  "%.2f" % user.onebook_wallet,
                    "isMain": "false"
                },
                {
                    "code": "ky",
                    "amount":  "%.2f" % user.ky_wallet,
                    "isMain": "false"
                },
                # {
                #     "code": "ag",
                #     "amount":  "%.2f" % user.ag_wallet,
                #     "isMain": "false"
                # },
                # {
                #     "code": "opus",
                #     "amount":  "%.2f" % user.opus_wallet,
                #     "isMain": "false"
                # },
                # {
                #     "code": "gpi",
                #     "amount":  "%.2f" % user.gpi_wallet,
                #     "isMain": "false"
                # },
                # {
                #     "code": "bbin",
                #     "amount":  "%.2f" % user.bbin_wallet,
                #     "isMain": "false"
                # },
                # {
                #     "code": "pt",
                #     "amount":  "%.2f" % user.pt_wallet,
                #     "isMain": "false"
                # }
            ]

            # response["ag"] = user.ag_wallet
            # response["opus"] = user.opus_wallet
            # response["gpi"] = user.gpi_wallet
            # response["bbin"] = user.bbin_wallet
            # response["pt"] = user.pt_wallet

            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json')
        
        except ObjectDoesNotExist as e:
            logger.error("The user does not exist ", e)
            response["error_code"] = ERROR_CODE_INVALID_INFO
            response["error_msg"] = "Cannot find the user"
            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json')

        
        except Exception as e:
            logger.error("Get amount of each wallet by a user error: ", e)
            return HttpResponse(status=400)


        