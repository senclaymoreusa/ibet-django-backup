from django.utils import timezone
from django.utils.timezone import timedelta, localtime, now
from django.db.models.query import QuerySet
from django.db.models import Q, ObjectDoesNotExist
from django.http import HttpResponse
from dateutil.relativedelta import relativedelta

from operation.models import Campaign
from users.models import CustomUser
from accounting.models import Transaction
from games.models import GameBet
from system.models import UserGroup, UserToUserGroup
from utils.constants import *

import logging
import uuid
import csv


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

'''
@param date: mm/dd/yyyy
@return: timezone datetime
'''
def dateToDatetime(date):
    if date:
        date = date.split('/')
        date = datetime.datetime(int(date[2]), int(date[0]), int(date[1]))
        current_tz = timezone.get_current_timezone()
        date = date.astimezone(current_tz)
    return date

'''
@param queryset: users
@return: queryset of active users between start_time and end_time
'''
def filterActiveUser(queryset, start_time, end_time):
    # get bet transaction in this period
    if start_time and end_time:
        game_bet_tran = GameBet.objects.filter(Q(bet_time__gte=start_time) & Q(bet_time__lte=end_time))
    elif start_time:
        game_bet_tran = GameBet.objects.filter(bet_time__gte=start_time)
    elif end_time:
        game_bet_tran = GameBet.objects.filter(bet_time__lte=end_time)
    else:
        game_bet_tran = GameBet.objects.all()

    active_user_list = game_bet_tran.values_list('username', flat=True)
    if queryset:
        queryset = queryset.filter(pk__in=active_user_list)
    return queryset


# calculate ftd user number in certain user_group within certain time range
def calculateFTD(user_group, start_time, end_time):
    # calculate this user_group's(downline list group or user group) within end_date ftd
    # user_group has to be objects group, end_date should be datetime format
    ftd = user_group.filter(Q(ftd_time__gte=start_time)
                            & Q(ftd_time__lte=end_time)).count()
    return ftd


def calculateTurnover(user, start_time, end_time):
    return 0


def calculateGGR(user, start_time, end_time):
    return 0


def calculateDeposit(user, start_time, end_time):
    count = 0
    amount = 0
    return count, amount


def calculateWithdrawal(user, start_time, end_time):
    count = 0
    amount = 0
    return count, amount


def calculateBonus(user, start_time, end_time):
    return 0


def calculateNGR(user, start_time, end_time):
    return 0


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


# Return a list of user in VIP Manager Group
def getManagerList(list_type):
    if list_type == "VIP":
        group_name = "VIP Manager"
    elif list_type == "Affiliate":
        group_name = "Affiliate Manager"
    else:
        group_name = ""

    try:
        manager_group = UserGroup.objects.get(groupType=PERMISSION_GROUP, name=group_name)
    except Exception as e:
        logger.info("Error getting {} group ".format(group_name) + str(e))
        return None

    managers = []
    manager_group = UserToUserGroup.objects.filter(group=manager_group).distinct()
    if manager_group:
        for manager in manager_group:
            managers.append(manager.user.username)
    return managers

'''
@param date: utc timezone datetime
@return: local timezone datetime
'''
def utcToLocalDatetime(date):
    if date:
        current_tz = timezone.get_current_timezone()
        date = date.astimezone(current_tz)
    return date


def displayChoiceValue(bonuses):
    # display SmallIntegerField value for read
    bonuses['status'] = BONUS_STATUS_CHOICES[bonuses['status']][1]
    bonuses['type'] = BONUS_TYPE_CHOICES[bonuses['type']][1]
    bonuses['campaign'] = Campaign.objects.get(pk=int(bonuses['campaign'])).name
    return bonuses


'''
@param date: filename, table header, table body data
@return: response
'''
def exportCSV(filename, row_title, data):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=filename'

    writer = csv.writer(response)
    writer.writerow(row_title)
    for i in data:
        writer.writerow(i)

    return response