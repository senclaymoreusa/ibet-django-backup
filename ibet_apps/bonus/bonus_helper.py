import datetime
import logging

from django.db.models import Q
from django.utils import timezone

from accounting.models import Transaction
from bonus.models import UserBonusEvent, Bonus, Requirement
from utils.constants import TRANSACTION_DEPOSIT, TRAN_SUCCESS_TYPE, BONUS_ACTIVE, BONUS_TYPE_DEPOSIT, \
    BONUS_VALID_DEPOSIT, BONUS_START, BONUS_TYPE_TURNOVER, BONUS_COMPLETED

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


def checkAndUpdateFTD(deposit):
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

    user = deposit.user_id
    user.ftd_time = deposit.arrive_time
    user.save()
    logger.info("Update player {}'s first deposit time {}".format(user.username, deposit.arrive_time))
    return True


def getValidFTD(user, deposit_amount, current_time):
    active_ube = UserBonusEvent.objects.filter(Q(owner=user)
                                               & Q(status=BONUS_START)
                                               & Q(completion_time__isnull=True))
    valid_ube = None
    valid_ube_wager = False
    deposit_tiered_parents = getTieredBonusParent(BONUS_TYPE_DEPOSIT)

    for ube in active_ube:

        bonus = ube.bonus
        wager_reqs = False  # bonus event has wager requirements or not
        amount_threshold = 0  # the minimum deposit money to receive this bonus
        ube_amount = 0  # bonus amount for this transaction
        reqs = Requirement.objects.filter(bonus=bonus)

        # skip invalid ube which bonus is not matched
        if bonus.start_time > current_time \
                or getBonusExpiredTime(bonus) < current_time \
                or bonus.status != BONUS_ACTIVE \
                or bonus.type != BONUS_TYPE_DEPOSIT \
                or reqs.filter(must_have=BONUS_VALID_DEPOSIT).exsit() \
                or (bonus in deposit_tiered_parents):
            continue

        for req in reqs:
            # skip must have reqs
            if req.must_have:
                continue

            if amount_threshold == 0:
                amount_threshold = req.amount_threshold
            if req.turnover_multiplier and req.turnover_multiplier != -1:
                wager_reqs = True
                break

        if deposit_amount < amount_threshold:
            continue

        # compare bonus amount and percentage, return a max_amount one
        if not valid_ube:
            valid_ube = ube
        else:
            if bonus.amount and bonus.amount > ube_amount:
                ube_amount = bonus.amount
                valid_ube = ube
                valid_ube_wager = wager_reqs

            if bonus.percentage:
                bonus_amount = float(bonus.percentage) * 0.01 * deposit_amount
                if bonus_amount > ube_amount:
                    ube_amount = bonus_amount
                    valid_ube = ube
                    valid_ube_wager = wager_reqs

    # find a valid first deposit bonus for user
    if valid_ube:
        completed_time = timezone.now()
        if not valid_ube_wager:
            # can be released
            new_ube = UserBonusEvent.objects.create(
                owner=user,
                bonus=valid_ube.bonus,
                amount=ube_amount,
                status=BONUS_COMPLETED,
                delivery_time=completed_time,
                completed_time=completed_time,
            )
            logger.info("{} first deposit bonus {} status changed to completed".format(user.username, new_ube.bonus.name))
        else:
            new_ube = UserBonusEvent.objects.create(
                owner=user,
                bonus=valid_ube.bonus,
                amount=ube_amount,
                status=BONUS_ACTIVE,
                delivery_time=completed_time,
                completed_time=completed_time
            )
            logger.info("{} first deposit bonus {} status changed to completed".format(user.username, new_ube.bonus.name))
        return valid_ube.bonus

    return None


# type: BONUS_TYPE_DEPOSIT or BONUS_TYPE_TURNOVER
def getTieredBonusParent(bonus_type):
    parent_list = list()
    bonuses = Bonus.objects.filter(type=bonus_type)
    for bonus in bonuses:
        if bonus.parent and bonus.parent not in parent_list:
            parent_list.append(bonus.parent)

    return parent_list
