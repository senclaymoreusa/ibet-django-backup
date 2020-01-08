import datetime
import logging

from django.db.models import Q

from accounting.models import Transaction
from bonus.models import UserBonusEvent, Bonus, Requirement
from utils.constants import TRANSACTION_DEPOSIT, TRAN_SUCCESS_TYPE, BONUS_ACTIVE, BONUS_TYPE_DEPOSIT, \
    BONUS_VALID_DEPOSIT

logger = logging.getLogger('django')


def getBonusExpiredTime(bonus):
    expired_time = bonus.end_time
    if bonus.expiration_days:
        expired_time = min(expired_time, bonus.start_time + datetime.timedelta(days=bonus.expiration_days))
    return expired_time


'''
@param date: user object, transaction of deposit object
@return: true if this is the user's first time deposit
'''


def checkFTD(deposit):
    if not deposit:
        logger.info("Invalid input for checking user First Deposit Time")
        return False

    user = deposit.user_id

    # check if user's ftd_time already has value
    if not user.ftd_time:
        return True

    # check if this is the user's first time deposit
    if Transaction.objects.filter(Q(arrive_time__lt=deposit.arrive_time)
                                  & Q(transaction_type=TRANSACTION_DEPOSIT)
                                  & Q(status=TRAN_SUCCESS_TYPE)).exsit():
        return False

    return True


def getValidFirstDepositBonus(user, deposit_amount, current_time):

    active_ube = UserBonusEvent.objects.filter(Q(owner=user)
                                               & Q(status=BONUS_ACTIVE)
                                               & Q(completion_time__isnull=True))

    deposit_tiered_parent = getTieredBonusParent(BONUS_TYPE_DEPOSIT)

    valid_ube = None

    for ube in active_ube:
        bonus = ube.bonus
        reqs = Requirement.objects.filter(bonus=bonus)

        # bonus is not valid
        if bonus.start_time > current_time \
                or getBonusExpiredTime(bonus) < current_time \
                or bonus.status != BONUS_ACTIVE \
                or bonus.type != BONUS_TYPE_DEPOSIT \
                or reqs.filter(must_have=BONUS_VALID_DEPOSIT).exsit() \
                or bonus in deposit_tiered_parent:
            continue

        # deposit amount not achieved threshold
        # check requirements, skip must have


        # 要返回一个ube amount最大的bonus

    return None


# type: BONUS_TYPE_DEPOSIT or BONUS_TYPE_TURNOVER
def getTieredBonusParent(type):
    parent_list = list()
    bonuses = Bonus.objects.filter(type=type)
    for bonus in bonuses:
        if bonus.parent and bonus.parent not in parent_list:
            parent_list.append(bonus.parent)

    return parent_list


def checkValidNextDepositBonus(user, current_time, bonus_type):
    return False
