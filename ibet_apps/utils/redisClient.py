import redis
from django.conf import settings
redisConfig = settings.REDIS

class RedisClient(object):
    def connect(self):
        connection_pool = redis.ConnectionPool(host=redisConfig['HOST'], port=redisConfig['PORT'], ssl_cert_reqs=None)
        return redis.StrictRedis(connection_pool=connection_pool)