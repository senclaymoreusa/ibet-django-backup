
from games.helper import transferRequest
from django.views import View
from django.db import DatabaseError
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder  
from django.conf import settings
from django.db import transaction
from users.views.helper import checkUserBlock
from users.models import CustomUser, UserWallet
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
from games.transferwallet import CheckTransferWallet


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

            if from_wallet == "main":
                current_from_wallet_amount = user.main_wallet
            else:
                from_provider = GameProvider.objects.get(provider_name=from_wallet)
                current_from_wallet_obj, created = UserWallet.objects.get_or_create(user=user, provider=from_provider)
                current_from_wallet_amount = current_from_wallet_obj.wallet_amount
                # print(current_from_wallet_obj.wallet_amount)
                # current_from_wallet_amount = current_from_wallet_obj.wallet_amount
                # current_from_wallet_amount = user.main_wallet
                # wallet = UserWallet.objects.get_or_create(user=user, provider=GameProvider(provider_name=to_wallet))

            # from_wallet_field_name = from_wallet + '_wallet'
            # current_from_wallet_amount = getattr(user, from_wallet_field_name)

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

        response = {}
        
        try:   

            user_id = request.GET.get('user_id')
            user = CustomUser.objects.get(pk=user_id)

            transfer_providers = GameProvider.objects.filter(is_transfer_wallet=True)

            updateWallet(transfer_providers, user)

            for provider in transfer_providers:
                provider_name = str(provider.provider_name)
                response[provider_name] = Decimal('0.00')

            # print(response)

            all_wallets = UserWallet.objects.filter(user=user)
            for wallet in all_wallets:
                response[wallet.provider.provider_name] =  "%.2f" % wallet.wallet_amount
            

            data = []
            data.append({
                "code": "main",
                "amount":  "%.2f" % user.main_wallet,
                "isMain": True
            })

            for code, amount in response.items(): 
                data.append({
                    "code": code,
                    "amount": amount,
                    "isMain": False
                })

            return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')
        
        except ObjectDoesNotExist as e:
            logger.error("The user does not exist ", e)
            response["error_code"] = ERROR_CODE_INVALID_INFO
            response["error_msg"] = "Cannot find the user"
            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json')

        
        except Exception as e:
            logger.error("Get amount of each wallet by a user error: ", e)
            return HttpResponse(status=400)


def updateWallet(all_trans_wallet, user):

    for i in all_trans_wallet:
        wallet_class = CheckTransferWallet(user)
        function_name = i.provider_name + 'CheckAmount'
        balance = getattr(wallet_class, function_name)()
        if balance >= 0:
            UserWallet.objects.filter(user=user, provider=i).update(wallet_amount=balance)

    print("finished update all the wallet")