from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.cache import cache
from django_redis import get_redis_connection
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

class CacheHelperTest(View):

    def post(self, request, *args, **kwargs):

        try:
            data = json.loads(request.body)
            userId = data['userId']
            deviceId = data['deviceId']
            bonusId = data['bonusId']

            r = RedisClient().connect()

            redis = RedisHelper()
            if redis.can_claim_bonus(bonusId, deviceId):
                print("Can claim bonus")
            else:
                print("Can not claim bonus")
            
            redis.set_bonus_by_device(bonusId, deviceId)
            redis.set_device_by_user(userId, deviceId)
            redis.set_user_by_device(userId, deviceId)
            print(redis.get_bonuses_by_device(deviceId))
            print(redis.get_devices_by_user(userId))
            print(redis.get_users_by_device(deviceId))

            data = {}

            return HttpResponse(json.dumps(data), content_type='application/json', status=200)
        except Exception as e:
            return HttpResponse(status=400)
