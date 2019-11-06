import redis
from utils.redisClient import RedisClient


REDIS_KEY_PREFIX_BONUS_BY_DEVICE = 'bonuses_by_device:'
REDIS_KEY_PREFIX_DEVICES_BY_USER = 'devices_by_user:'
REDIS_KEY_PREFIX_USERS_BY_DEVICE = 'users_by_device:'
REDIS_KEY_PREFIX_ONEBOOK_BET_DETAILS = 'onebook_history:'

def getBonusByDeviceRedisKey(device_id):
    return REDIS_KEY_PREFIX_BONUS_BY_DEVICE + str(device_id)

def getDevicesByUserRedisKey(user_id):
    return REDIS_KEY_PREFIX_DEVICES_BY_USER + str(user_id)

def getUsersByDeviceRedisKey(device_id):
    return REDIS_KEY_PREFIX_USERS_BY_DEVICE + str(device_id)

def getOnebookBetDetailsRedisKey():
    return REDIS_KEY_PREFIX_ONEBOOK_BET_DETAILS




class RedisHelper():
    
    def __init__(self):
        self.r = RedisClient().connect()

    def can_claim_bonus(self, bonus_id, device_id):
        bonus_by_device_key = getBonusByDeviceRedisKey(device_id)
        return not self.r.sismember(bonus_by_device_key, bonus_id)

    def set_bonus_by_device(self, bonus_id, device_id):
        bonus_by_device_key = getBonusByDeviceRedisKey(device_id)
        return self.r.sadd(bonus_by_device_key, bonus_id)

    def set_device_by_user(self, user_id, device_id):
        devices_by_user_key = getDevicesByUserRedisKey(user_id)
        return self.r.sadd(devices_by_user_key, device_id)
    
    def set_user_by_device(self, user_id, device_id):
        users_by_device_key = getUsersByDeviceRedisKey(device_id)
        return self.r.sadd(users_by_device_key, user_id)

    def get_bonuses_by_device(self, device_id):
        bonus_by_device_key = getBonusByDeviceRedisKey(device_id)
        return self.r.smembers(bonus_by_device_key)

    def get_devices_by_user(self, user_id):
        devices_by_user_key = getDevicesByUserRedisKey(user_id)
        return self.r.smembers(devices_by_user_key)

    def get_users_by_device(self, device_id):
        users_by_device_key = getUsersByDeviceRedisKey(device_id)
        return self.r.smembers(users_by_device_key)

    def set_onebook_bet_details(self, onebook_run):
        onebook_bet_details = getOnebookBetDetails()
        return self.r.sadd(onebook_bet_details, onebook_run)

    def check_onebook_bet_details(self, onebook_run):
        onebook_bet_details = getOnebookBetDetails()
        return self.r.sismember(onebook_bet_details, onebook_run)

    def remove_onebook_bet_details(self, onebook_run):
        onebook_bet_details = getOnebookBetDetails()
        return self.r.spop(onebook_bet_details, onebook_run)