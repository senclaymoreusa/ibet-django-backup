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
            logger.info('Deleting loss limit for interval type: ' + str(intervalType))
            # Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_LOSS, interval=intervalType).delete()
            Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_LOSS, interval=intervalType).update(amount=None)

    # insert or update
    for i in range(len(lossLimit)):
        if Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_LOSS, interval=lossLimitInterval[i]).exists():
            logger.info('Update loss limit for interval type: ' + str(user))
            Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_LOSS, interval=lossLimitInterval[i]).update(amount=lossLimit[i])
        else:
            logger.info('Create new bet limit for product type for ' + str(user))
            limitation = Limitation(
                user= user,
                limit_type=LIMIT_TYPE_LOSS,
                amount=lossLimit[i],
                interval=lossLimitInterval[i],
            )
            limitation.save()

def set_deposit_limitation(userId, depositLimit, depositLimitInterval, oldLimitMap, user):
    # user = CustomUser.objects.get(pk=userId)
    # if depositLimitInterval:
    # delete
    for intervalType in oldLimitMap[LIMIT_TYPE_DEPOSIT]:
        if intervalType not in depositLimitInterval:
            logger.info('Deleting deposit limit for interval type: ' + str(intervalType))
            # Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_DEPOSIT, interval=intervalType).delete()
            Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_DEPOSIT, interval=intervalType).update(amount=None)

    # insert or update
    for i in range(len(depositLimitInterval)):
        # print("index: " + str(i))
        if Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_DEPOSIT, interval=depositLimitInterval[i]).exists():
            logger.info('Update deposit limit for interval type: ' + str(user))
            Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_DEPOSIT, interval=depositLimitInterval[i]).update(amount=depositLimit[i])
        else:
            logger.info('Create new bet limit for product type for' + str(user))
            limitation = Limitation(
                user= user,
                limit_type=LIMIT_TYPE_DEPOSIT,
                amount=depositLimit[i],
                interval=depositLimitInterval[i],
            )
            limitation.save()




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