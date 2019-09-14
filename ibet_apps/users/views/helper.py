import logging
import json
from utils.constants import *
from users.models import *
from django.utils import timezone
import datetime
import decimal
from django.core.serializers.json import DjangoJSONEncoder


logger = logging.getLogger('django')


def set_loss_limitation(userId, lossLimit, lossLimitInterval, oldLimitMap, user):
    # user = CustomUser.objects.get(pk=userId)
    
    # if lossLimitInterval:
    # delete
    for intervalType in oldLimitMap[LIMIT_TYPE_LOSS]:
        if intervalType not in lossLimitInterval:
            # Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_LOSS, interval=intervalType).delete()
            Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_LOSS, interval=intervalType).update(amount=None)
            logger.info('Deleting loss limit for interval type: ' + str(intervalType))

    # insert or update
    for i in range(len(lossLimit)):
        if Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_LOSS, interval=lossLimitInterval[i]).exists():
            Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_LOSS, interval=lossLimitInterval[i]).update(amount=lossLimit[i])
            logger.info('Update loss limit for interval type: ' + str(user))
        else:
            limitation = Limitation(
                user= user,
                limit_type=LIMIT_TYPE_LOSS,
                amount=lossLimit[i],
                interval=lossLimitInterval[i],
            )
            limitation.save()
            logger.info('Create new bet limit for product type for ' + str(user))

def set_deposit_limitation(userId, depositLimit, depositLimitInterval, oldLimitMap, user):
    # user = CustomUser.objects.get(pk=userId)
    # if depositLimitInterval:
    # delete
    for intervalType in oldLimitMap[LIMIT_TYPE_DEPOSIT]:
        if intervalType not in depositLimitInterval:
            # Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_DEPOSIT, interval=intervalType).delete()
            Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_DEPOSIT, interval=intervalType).update(amount=None)
            logger.info('Deleting deposit limit for interval type: ' + str(intervalType))

    # insert or update
    for i in range(len(depositLimitInterval)):
        # print("index: " + str(i))
        if Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_DEPOSIT, interval=depositLimitInterval[i]).exists():
            Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_DEPOSIT, interval=depositLimitInterval[i]).update(amount=depositLimit[i])
            logger.info('Update deposit limit for interval type: ' + str(user))
        else:
            limitation = Limitation(
                user= user,
                limit_type=LIMIT_TYPE_DEPOSIT,
                amount=depositLimit[i],
                interval=depositLimitInterval[i],
            )
            limitation.save()
            logger.info('Create new bet limit for product type for' + str(user))




def set_temporary_timeout(userId, intervalOption):
    user = CustomUser.objects.get(pk=userId)
    user.temporary_block_time = timezone.now()
    intervalOption = int(intervalOption)
    if intervalOption >= 0:
        user.temporary_block_interval = intervalOption
    else:
        user.temporary_block_interval = None
        user.temporary_block_time = None
        
    # print(user.temporary_block_time)
    # print(user.temporary_block_timespan)
    user.save()
    logger.info("Setting temporary timeout of user: {}, and temporary interval options is {} from ".format(str(user.username), str(intervalOption)))

def set_permanent_timeout(userId, intervalOption):
    user = CustomUser.objects.get(pk=userId)
    user.permanent_block_time = timezone.now()
    intervalOption = int(intervalOption)
    if intervalOption >= 0:
        user.permanent_block_interval = intervalOption
    else:
        user.permanent_block_interval = None
        user.permanent_block_time = None
    user.save()
    logger.info("Setting permanent timeout of user: {}, and permanent interval options is {} from ".format(str(user.username), str(intervalOption)))


def get_old_limitations(userId):
    user = CustomUser.objects.get(pk=userId)
    oldLimitMap = {
        LIMIT_TYPE_BET: {},
        LIMIT_TYPE_LOSS: {},
        LIMIT_TYPE_DEPOSIT: {},
        LIMIT_TYPE_WITHDRAW: {},
        LIMIT_TYPE_ACCESS_DENY: {}
    }

    limitations = Limitation.objects.filter(user=user)
    for limit in limitations:
        limitType = limit.limit_type
        if limitType == LIMIT_TYPE_ACCESS_DENY:
            amount = None if limit.amount is None else decimal.Decimal(limit.amount)
            oldLimitMap[limitType][limit.product] = amount
        else:
            # oldLimitMap[limitType]['amount'] = limit.amount
            amount = None if limit.amount is None else decimal.Decimal(limit.amount)
            oldLimitMap[limitType][limit.interval] = amount
    
    # print(oldLimitMap)
    logger.info("Getting old limitations of user: {}, and limitations are {}".format(str(user.username), json.dumps(oldLimitMap, cls=DjangoJSONEncoder)))
    return oldLimitMap


def checkUserBlock(userId):

    user = CustomUser.objects.get(pk=userId)
    if user.block is True:
        return True
    elif user.temporary_block_time or user.permanent_block_time:
        expried_time = ''
        blocked_time = ''
        if user.temporary_block_time is not None:
            blocked_time =  user.temporary_block_time
            expried_time = user.temporary_block_time
            if user.temporary_block_interval == INTERVAL_PER_DAY:
                expried_time = expried_time + datetime.timedelta(days=1)
            elif user.temporary_block_interval == INTERVAL_PER_WEEK:
                expried_time = expried_time + datetime.timedelta(days=7)
            elif user.temporary_block_interval == INTERVAL_PER_MONTH:
                expried_time = expried_time + datetime.timedelta(days=30)
            
        elif user.permanent_block_time is not None:
            blocked_time =  user.permanent_block_time
            expried_time = user.permanent_block_time
            if user.permanent_block_interval == INTERVAL_PER_SIX_MONTH:
                expried_time = expried_time + datetime.timedelta(6*365/12)
            elif user.permanent_block_interval == INTERVAL_PER_ONE_YEAR:
                expried_time = expried_time + datetime.timedelta(365)
            elif user.permanent_block_interval == INTERVAL_PER_THREE_YEAR:
                expried_time = expried_time + datetime.timedelta(365*3)
            elif user.permanent_block_interval == INTERVAL_PER_FIVE_YEAR:
                expried_time = expried_time + datetime.timedelta(365*5)

        logger.info("Blocked time: " + str(blocked_time))   
        logger.info("Expried time: " + str(expried_time))

        # print(str(timezone.now()))
        if expried_time > timezone.now():
            logger.info("The account is blocked")
            return True
        else:
            # print("No")
            logger.info("The account is not blocked")
            user.temporary_block_time = None
            user.permanent_block_time = None
            return False

    return False
    