from games.helper import transferRequest
from django.views import View
from django.db import DatabaseError
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
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


class PaymentSetting(View):

    def post(self, request, *args, **kwargs):
        
        try:
            data = json.loads(request.body)
            user_id = data["user_id"]
            payment_id = data["payment_id"]

            user = CustomUser.objects.get(pk=user_id)
            # print(user)
            DepositAccessManagement.objects.filter(user_id=user).update(deposit_favorite_method=False)
            DepositAccessManagement.objects.filter(user_id=user, deposit_channel_id=payment_id).update(deposit_favorite_method=True)

            response = {
                'status_code': CODE_SUCCESS,
                'message': "Successfully set favorite deposit method"
            }

            logger.info("Save {} to favorite deposit method for user: {}".format(payment_id, user.username))
            return HttpResponse(json.dumps(response), content_type="application/json")

        except Exception as e:
            logger.error("Setting favorite deposit method error: ", e)
            return HttpResponse(status=400)

