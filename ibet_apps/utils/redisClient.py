import redis
from django.conf import settings
import fakeredis
import os
redisConfig = settings.REDIS
isTest = settings.TESTING

class RedisClient(object):
    def connect(self):
        if not isTest and os.getenv("ENV") == 'apdev':
            connection_pool = redis.ConnectionPool(host=redisConfig['HOST'], port=redisConfig['PORT'])
            return redis.StrictRedis(connection_pool=connection_pool)
        else:   
            return fakeredis.FakeStrictRedis()