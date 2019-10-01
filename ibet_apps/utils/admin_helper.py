from django.utils import timezone
from django.utils.timezone import timedelta, localtime, now
from dateutil.relativedelta import relativedelta
from users.models import *
from accounting.models import Transaction
from utils.constants import *
from django.db.models.query import QuerySet


import logging

logger = logging.getLogger('django')


users = CustomUser.objects.all()

# date
today = localtime(now()).date()
yesterday = today - timezone.timedelta(days=1)
this_month = today.replace(day=1)
last_month = this_month + relativedelta(months=-1)
before_last_month = this_month + relativedelta(months=-2)

# transaction filter
deposit_tran = Transaction.objects.filter(
    transaction_type=TRANSACTION_DEPOSIT)
withdrawal_tran = Transaction.objects.filter(
    transaction_type=TRANSACTION_WITHDRAWAL)
bonus_tran = Transaction.objects.filter(
    transaction_type=TRANSACTION_BONUS)
commission_tran = Transaction.objects.filter(
    transaction_type=TRANSACTION_COMMISSION)
bet_tran = Transaction.objects.filter(
            transaction_type=TRANSACTION_BET_PLACED)

# get downline list for affiliate or affiliates
def getDownline(affiliates):
    downline_list = []
    # corner case
    if affiliates in [None, '']:
        logger.info("Error input for getting downline list!")
        return []
    elif isinstance(affiliates, QuerySet):
        for affiliate in affiliates:
            downline = users.filter(referred_by=affiliate)
            if downline:
                downline_list.append(users.filter(referred_by=affiliate))
    else:
        downline_list = users.filter(referred_by=affiliates)
    return downline_list


def calculateActiveDownlineNumber(affiliate_id):
    # check affiliate_id first
    downlines = affiliate_id.referees.all()
    affiliate_active_users = 0
    if downlines is not None:
        for tran in bet_tran:
            if tran.user_id in downlines:
                affiliate_active_users += 1
    return affiliate_active_users

# calculate ftd user number in certain user_group within certain time range
def calculateFTD(user_group, start_date, end_date):
    # calculate this user_group's(downline list group or user group) within end_date ftd
    # user_group has to be objects group, end_date should be datetime format
    ftd = user_group.filter(Q(ftd_time__gte=start_date)
                            & Q(ftd_time__lte=end_date)).count()
    return ftd


def calculateTurnover(user):
    return 0