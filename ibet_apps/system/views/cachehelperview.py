from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.cache import cache
from django.conf import settings
import os
import json
import time
import boto3
from botocore.exceptions import ClientError
import re
import redis
from utils.redisClient import RedisClient
from utils.redisHelper import RedisHelper
import logging
logger = logging.getLogger('django')


# This is just a test example for testing redis functions
class CacheHelperTest(View):

    def post(self, request, *args, **kwargs):

        try:
            data = json.loads(request.body)
            user_id = data['user_id']
            device_id = data['device_id']
            bonus_id = data['bonus_id']

            r = RedisClient().connect()

            redis = RedisHelper()
            if redis.can_claim_bonus(bonus_id, device_id):
                print("Can claim bonus")
            else:
                print("Can not claim bonus")
            
            redis.set_bonus_by_device(bonus_id, device_id)
            redis.set_device_by_user(user_id, device_id)
            redis.set_user_by_device(user_id, device_id)
            print(redis.get_bonuses_by_device(device_id))
            print(redis.get_devices_by_user(user_id))
            print(redis.get_users_by_device(device_id))

            data = {}

            return HttpResponse(json.dumps(data), content_type='application/json', status=200)
        except Exception as e:
            logger.error("Error connect to AWS redis: {}".format(str(e)))
            return HttpResponse(status=400)
