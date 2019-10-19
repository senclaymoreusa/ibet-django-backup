from django.utils import timezone
from django.utils.timezone import timedelta, localtime, now
from django.db.models.query import QuerySet
from django.db.models import Q
from dateutil.relativedelta import relativedelta

from users.models import CustomUser
from accounting.models import Transaction
from utils.constants import *

import logging
import uuid

logger = logging.getLogger('django')

users = CustomUser.objects.all()

# date
today = timezone.now()
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


current_tz = timezone.get_current_timezone()

def convertToTimezone(input_time):
    input_time = input_time.astimezone(current_tz)
    return input_time


# USER SYSTEM
# create unique refer code for both user and affiliate
limit_digit = 6
source_string = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
limit_user = 36 ** limit_digit


# encode
def generate_unique_referral_code(user_id):
    code = ''
    if user_id in range(0, limit_user):
        i = 0
        while i in range(0, limit_digit):
            mod = int(user_id % 36)
            code += str(source_string[mod])
            user_id /= 36
            i += 1
        return code

    else:
        logger.error("Error create referral code for user")
        raise ValueError("Please enter an integer bigger than 0 and smaller than 36^%s" % limit_digit)


# decode
def decode_user_id_from_referral_code(code):
    user_id = 0
    code = code.upper()
    if len(code) != limit_digit:
        logger.error("Error referral code format")
        raise ValueError("Please enter a valid referral code")
    else:
        i = 0
        while i in range(0, limit_digit):
            index = source_string.find(code[i])
            user_id += (36 ** i * index)
            i += 1
        return user_id
