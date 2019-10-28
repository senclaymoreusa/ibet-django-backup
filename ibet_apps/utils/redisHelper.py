import redis
from utils.redisClient import RedisClient


REDIS_KEY_PREFIX_BONUS_BY_DEVICE = 'bonuses_by_device:'
REDIS_KEY_PREFIX_DEVICES_BY_USER = 'devices_by_user:'
REDIS_KEY_PREFIX_USERS_BY_DEVICE = 'users_by_device:'


def getBonusByDeviceRedisKey(deviceId):
    return REDIS_KEY_PREFIX_BONUS_BY_DEVICE + str(deviceId)

def getDevicesByUserRedisKey(userId):
    return REDIS_KEY_PREFIX_DEVICES_BY_USER + str(userId)

def getUsersByDeviceRedisKey(deviceId):
    return REDIS_KEY_PREFIX_USERS_BY_DEVICE + str(deviceId)


class RedisHelper():
    
    def __init__(self):
        self.r = RedisClient().connect()

    def can_claim_bonus(self, bonus_id, device_id):
        bonusByDeviceKey = getBonusByDeviceRedisKey(device_id)
        return not self.r.sismember(bonusByDeviceKey, bonus_id)

    def set_bonus_by_device(self, bonus_id, device_id):
        bonusByDeviceKey = getBonusByDeviceRedisKey(device_id)
        return self.r.sadd(bonusByDeviceKey, bonus_id)

    def set_device_by_user(self, user_id, device_id):
        devicesByUserKey = getDevicesByUserRedisKey(user_id)
        return self.r.sadd(devicesByUserKey, device_id)
    
    def set_user_by_device(self, user_id, device_id):
        usersByDeviceKey = getUsersByDeviceRedisKey(device_id)
        return self.r.sadd(usersByDeviceKey, user_id)

    def get_bonuses_by_device(self, device_id):
        bonusByDeviceKey = getBonusByDeviceRedisKey(device_id)
        return self.r.smembers(bonusByDeviceKey)

    def get_devices_by_user(self, user_id):
        devicesByUserKey = getDevicesByUserRedisKey(user_id)
        return self.r.smembers(devicesByUserKey)

    def get_users_by_device(self, device_id):
        usersByDeviceKey = getUsersByDeviceRedisKey(device_id)
        return self.r.smembers(usersByDeviceKey)