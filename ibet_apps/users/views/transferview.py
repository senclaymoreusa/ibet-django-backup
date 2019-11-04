
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


class Transfer(View):

    def post(self, request, *args, **kwargs):
        
        try:
            body = json.loads(request.body)
            user_id = body["user_id"]
            from_wallet = body["from_wallet"]
            to_wallet = body["to_wallet"]
            amount = body["amount"]

            user = CustomUser.objects.get(pk=user_id)

            transferRequest(user, amount, from_wallet, to_wallet)
            response = {
                "status_code": CODE_SUCCESS,
                "error_message": "Successfully transfer"
            }

            logger.info("Successfully transfer money from" + str(from_wallet) + " " + str(to_wallet))
            return HttpResponse(json.dumps(response), content_type='application/json')

        except Exception as e:
            logger.error("Request transfer error: ", e)
            return HttpResponse(status=400)