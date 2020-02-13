import redis
from utils.redisClient import RedisClient


REDIS_KEY_PREFIX_BONUS_BY_DEVICE = 'bonuses_by_device:'
REDIS_KEY_PREFIX_DEVICES_BY_USER = 'devices_by_user:'
REDIS_KEY_PREFIX_USERS_BY_DEVICE = 'users_by_device:'
REDIS_KEY_PREFIX_ONEBOOK_BET_DETAILS = 'onebook_history:'
REDIS_KEY_PREFIX_AG_FILES = 'AG_files:'
REDIS_KEY_PREFIX_EA_BET_HISTORY = 'ea_last_game_file:'

REDIS_KEY_PREFIX_PT_BET_SET = 'pt_starttime: game_bet'
REDIS_KEY_PREFIX_KY_BET_DETAILS = 'ky_bets:'
REDIS_KEY_PREFIX_GPI_BET_DETAILS = 'gpi_bets:'



def getBonusByDeviceRedisKey(device_id):
    return REDIS_KEY_PREFIX_BONUS_BY_DEVICE + str(device_id)

def getDevicesByUserRedisKey(user_id):
    return REDIS_KEY_PREFIX_DEVICES_BY_USER + str(user_id)

def getUsersByDeviceRedisKey(device_id):
    return REDIS_KEY_PREFIX_USERS_BY_DEVICE + str(device_id)

def getOnebookBetDetailsRedisKey():
    return REDIS_KEY_PREFIX_ONEBOOK_BET_DETAILS

def getAGFileHistoryRedisKey():
    return REDIS_KEY_PREFIX_AG_FILES

def getEABetHistroyRedisKey():
    return REDIS_KEY_PREFIX_EA_BET_HISTORY


def getPTStarttimeKey():
    return REDIS_KEY_PREFIX_PT_BET_SET

def getKYBetDetailsRedisKey():
    return REDIS_KEY_PREFIX_KY_BET_DETAILS

def getGPIBetDetailsRedisKey():
    return REDIS_KEY_PREFIX_GPI_BET_DETAILS


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
        onebook_bet_details = getOnebookBetDetailsRedisKey()
        return self.r.sadd(onebook_bet_details, onebook_run)

    def check_onebook_bet_details(self, onebook_run):
        onebook_bet_details = getOnebookBetDetailsRedisKey()
        return self.r.sismember(onebook_bet_details, onebook_run)

    def remove_onebook_bet_details(self, onebook_run):
        onebook_bet_details = getOnebookBetDetailsRedisKey()
        return self.r.srem(onebook_bet_details, onebook_run)

    def set_latest_timestamp(self, key, timestamp):
        return self.r.set(key, timestamp)

    def get_latest_timestamp(self, key):
        return self.r.get(key)

    def set_pt_starttime(self, timestamp):
        pt_key = getPTStarttimeKey()
        return self.r.set(pt_key, timestamp)

    def get_pt_starttime(self):
        pt_key = getPTStarttimeKey()
        return self.r.get(pt_key)


    def set_ag_added_file(self, ftp_file):
        ag_file = getAGFileHistoryRedisKey()
        return self.r.set(ag_file, ftp_file)
    
    def get_ag_added_file(self):
        ag_file = getAGFileHistoryRedisKey()
        return self.r.get(ag_file)

    def set_ea_last_file(self, file_name):
        ea_bet_history = getEABetHistroyRedisKey()
        return self.r.set(ea_bet_history, file_name)

    def get_ea_last_file(self):
        ea_bet_history = getEABetHistroyRedisKey()
        return self.r.get(ea_bet_history)

    def set_ky_bets_timestamp(self, timestamp):
        ky_bet_details = getKYBetDetailsRedisKey()
        return self.r.set(ky_bet_details, timestamp)

    def get_ky_bets_timestamp(self):
        ky_bet_details = getKYBetDetailsRedisKey()
        return self.r.get(ky_bet_details)

    def set_gpi_bets_starttime(self, starttime):
        gpi_bet_starttime = getGPIBetDetailsRedisKey()
        return self.r.set(gpi_bet_starttime, starttime)

    def get_gpi_bets_starttime(self):
        gpi_bet_starttime = getGPIBetDetailsRedisKey()
        return self.r.get(gpi_bet_starttime)
