from django.http import HttpResponse, StreamingHttpResponse
from django.utils import timezone
from django.utils.timezone import timedelta, localtime, now
from django.db.models.query import QuerySet
from django.db.models import Q, ObjectDoesNotExist
from django.http import HttpResponse
from dateutil.relativedelta import relativedelta
from datetime import date

from users.models import CustomUser, UserAction, SystemCommissionLevel, PersonalCommissionLevel
from operation.models import Campaign
from users.models import CustomUser
from accounting.models import Transaction
from games.models import GameBet, Category
from system.models import UserGroup, UserToUserGroup
from utils.constants import *

import logging
import uuid
import csv

logger = logging.getLogger('django')

users = CustomUser.objects.all()

# date
today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
yesterday = today - timezone.timedelta(days=1)
this_month = today.replace(day=1)
last_month = this_month + relativedelta(months=-1)
before_last_month = this_month + relativedelta(months=-2)


# transaction filter

def getCommissionTrans():
    commission_tran = Transaction.objects.filter(
        Q(transaction_type=TRANSACTION_COMMISSION) & Q(channel=None))
    return commission_tran


'''
@param affiliates: affiliate object or queryset
@return: players list(users referred by affiliates)
'''


# get player list for affiliate or affiliates
def getPlayers(affiliates):
    player_list = None
    if affiliates in [None, '']:
        logger.info("Warning input for getting downline list!")
        return []
    elif isinstance(affiliates, QuerySet):
        for affiliate in affiliates:
            affiliate_referral_path = affiliate.referral_path
            player_list |= CustomUser.objects.filter(
                Q(referral_path__contains=affiliate_referral_path) & ~Q(pk=affiliate.pk))
    else:
        affiliate_referral_path = affiliates.referral_path
        player_list = CustomUser.objects.filter(
            Q(referral_path__contains=affiliate_referral_path) & ~Q(pk=affiliates.pk))

    return player_list


'''
@param affiliates: affiliate object or queryset
@return: downline list(affiliates referred by affiliates)
'''


# get downline list for affiliate or affiliates
def getDownlines(affiliates):
    downline_list = None
    if affiliates in [None, '']:
        logger.info("Invalid input for getting affiliates' downline list.")
        return []
    elif isinstance(affiliates, QuerySet):
        for affiliate in affiliates:
            affiliate_referral_path = affiliate.referral_path
            downline_list |= CustomUser.objects.filter(
                Q(referral_path__contains=affiliate_referral_path) & Q(user_to_affiliate_time__isnull=False) & ~Q(
                    pk=affiliate.pk))
    else:
        affiliate_referral_path = affiliates.referral_path
        downline_list = CustomUser.objects.filter(
            Q(referral_path__contains=affiliate_referral_path) & Q(user_to_affiliate_time__isnull=False) & ~Q(
                pk=affiliates.pk))

    return downline_list


'''
@param queryset: users queryset, start time, end time, include free bets or not
@return: queryset of active users between start_time and end_time
'''


def filterActiveUser(queryset, start_time, end_time, free_bets, cate):
    # get bet transaction in this period
    active_filter = Q()
    if not free_bets:
        active_filter &= ~Q(other_data__is_free=True)

    if cate:
        active_filter &= Q(category__name=cate)

    if start_time and end_time:
        active_filter &= Q(bet_time__gte=start_time)
        active_filter &= Q(bet_time__lte=end_time)
    elif start_time:
        active_filter &= Q(bet_time__gte=start_time)
    elif end_time:
        active_filter &= Q(bet_time__lte=end_time)

    active_user_list = GameBet.objects.filter(active_filter).values_list('user', flat=True)
    if queryset:
        queryset = queryset.filter(pk__in=active_user_list)
    return queryset


'''
@return: users who made first time deposit within this time range
'''


def calculateFTD(queryset, start_time, end_time):
    # calculate this user_group's(downline list group or user group) within end_date ftd
    # user_group has to be objects group, end_date should be datetime format
    ftd_filter = Q()
    if start_time and end_time:
        ftd_filter &= Q(ftd_time__gte=start_time)
        ftd_filter &= Q(ftd_time__lte=end_time)
    elif start_time:
        ftd_filter &= Q(ftd_time__gte=start_time)
    elif end_time:
        ftd_filter &= Q(ftd_time__lte=end_time)

    ftd_count = queryset.filter(ftd_filter).count()
    return ftd_count


# calculate newly registered players referred by the affiliate within certain time range
def calculateRegistrations(user_group, start_time, end_time):
    # calculate this user_group's(downline list group or user group) within end_date ftd
    # user_group has to be objects group, end_date should be datetime format
    regis_filter = Q()
    if start_time and end_time:
        regis_filter &= Q(time_of_registration__gte=start_time)
        regis_filter &= Q(time_of_registration__lte=end_time)
    elif start_time:
        regis_filter &= Q(time_of_registration__gte=start_time)
    elif end_time:
        regis_filter &= Q(time_of_registration__lte=end_time)

    registered_count = user_group.filter(regis_filter).count()
    return registered_count


# calculate new players referred by the affiliate place first bet during certain time range
def calculateNewPlayer(user_group, start_time, end_time, free_bets):
    new_player_count = 0
    new_player_filter = Q()

    if free_bets:
        new_player_filter &= Q(other_data__is_free=False)

    for user in user_group:
        bet = GameBet.objects.filter(Q(user=user) & new_player_filter).order_by("bet_time")
        if bet:
            first_bet = bet[0]
            if start_time <= first_bet.bet_time <= end_time:
                new_player_count += 1

    return new_player_count


def getCommissionRate(user, start_time, end_time):
    if not user:
        return 0

    downlines = getDownlines(user)
    active_downline = filterActiveUser(downlines, start_time, end_time, True, None).count()
    downline_ftd = calculateFTD(downlines, start_time, end_time)
    ngr = 0
    for downline in downlines:
        ngr += calculateNGR(downline, start_time, end_time, None)
    if user.commission_setting == 'System':
        commissions = SystemCommissionLevel.objects.all().order_by('-commission_percentage')
    else:
        commissions = PersonalCommissionLevel.objects.filter(user_id=user).order_by('-commission_percentage')

    if commissions:
        for level in commissions:
            if active_downline >= level.active_downline_needed \
                    and downline_ftd >= level.monthly_downline_ftd_needed and ngr >= level.ngr:
                return level.commission_percentage
    return 0


# TODO: functions need to be updated
def calculateTurnover(user, start_time, end_time, cate):
    return 0


def calculateGGR(user, start_time, end_time, cate):
    return 0


def calculateDeposit(user, start_time, end_time):
    count = 0
    amount = 0
    return count, amount


def calculateWithdrawal(user, start_time, end_time):
    count = 0
    amount = 0
    return count, amount


def calculateBonus(user, start_time, end_time, cate):
    return 0


def calculateNGR(user, start_time, end_time, cate):
    return 0


def calculateAdjustment(user, start_time, end_time):
    return 0


def getUserBalance(user):
    return user.main_wallet


# USER SYSTEM
# create unique refer code for both user and affiliate
limit_digit = 6
source_string = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
limit_user = 36 ** limit_digit


# Encode Referral Code
def generateUniqueReferralCode(user_id):
    code = ''
    if user_id in range(0, limit_user):
        i = 0
        while i in range(0, limit_digit):
            mod = int(user_id % 36)
            code += str(source_string[mod])
            user_id /= 36
            i += 1

    else:
        logger.error("FATAL__ERROR creating referral code for user")
    return code


# Decode Referral Code
def decodeReferralCode(code):
    user_id = 0
    code = code.upper()
    # Invalid Referral Code
    if len(code) != limit_digit:
        logger.info("Error referral code length")
        return None
    else:
        i = 0
        while i in range(0, limit_digit):
            index = source_string.find(code[i])
            user_id += (36 ** i * index)
            i += 1
        return user_id


'''
@param user: user object
@return: time of last login time
'''


def lastLogin(user):
    action = UserAction.objects.filter(Q(user=user) &
                                       Q(event_type=EVENT_CHOICES_LOGIN)).order_by('-created_time')
    if action:
        return action[0].created_time
    return None


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
@param date: utc timezone datetime
@return: local timezone datetime
'''


def utcToLocalDatetime(date):
    if date:
        current_tz = timezone.get_current_timezone()
        date = date.astimezone(current_tz)
    return date


'''
@param date: utc timezone datetime
@return: local timezone datetime
'''


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


# for bonus admin display
def bonusValueToKey(bonuses):
    try:
        cap = Campaign.objects.get(pk=bonuses['campaign']).name
    except ObjectDoesNotExist:
        cap = ""
    # display SmallIntegerField value for read
    bonuses['status'] = BONUS_STATUS_CHOICES[bonuses['status']][1]
    bonuses['type'] = BONUS_TYPE_CHOICES[bonuses['type']][1]
    bonuses['campaign'] = cap
    if bonuses['start_time']:
        bonuses['start_time'] = datetime.datetime.strptime(bonuses['start_time'], '%Y-%m-%dT%H:%M:%SZ')
        bonuses['start_time'] = utcToLocalDatetime(bonuses['start_time'])
        bonuses['start_time'] = datetime.datetime.strftime(bonuses['start_time'], '%b %m %Y')
    if bonuses['end_time']:
        bonuses['end_time'] = datetime.datetime.strptime(bonuses['end_time'], '%Y-%m-%dT%H:%M:%SZ')
        bonuses['end_time'] = utcToLocalDatetime(bonuses['end_time'])
        bonuses['end_time'] = datetime.datetime.strftime(bonuses['end_time'], '%b %m %Y')
    return bonuses


def ubeValueToKey(ube):
    ube['status'] = USER_BONUS_EVENT_TYPE_CHOICES[ube['status']][1]
    if ube['delivery_time']:
        ube['delivery_time'] = datetime.datetime.strptime(ube['delivery_time'],
                                                          '%Y-%m-%dT%H:%M:%S.%fZ')  # for auto add field
        ube['delivery_time'] = utcToLocalDatetime(ube['delivery_time'])
        ube['delivery_time'] = datetime.datetime.strftime(ube['delivery_time'], '%b %m %Y')
    if ube['completion_time']:
        ube['completion_time'] = datetime.datetime.strptime(ube['completion_time'], '%Y-%m-%dT%H:%M:%SZ')
        ube['completion_time'] = utcToLocalDatetime(ube['completion_time'])
        ube['completion_time'] = datetime.datetime.strftime(ube['completion_time'], '%b %m %Y')
    return ube


BONUS_TYPE_VALUE_DICT = {
    "manual": BONUS_TYPE_MANUAL,
    "deposit": BONUS_TYPE_DEPOSIT,
    "turnover": BONUS_TYPE_TURNOVER,
    "verification": BONUS_TYPE_VERIFICATION
}

BONUS_DELIVERY_VALUE_DICT = {
    "push": BONUS_DELIVERY_PUSH,
    "site": BONUS_DELIVERY_SITE,
}

# hard code for deposit tiered amount setting
# deposit amount upper bound, bonus rate, max bonus amount, turnover multiple
DEPOSIT_TIERED_AMOUNTS = [[100, 20, 2000, 12, 12, 12, 12], [10000, 25, 12500, 13, 13, 13, 13],
                          [50000, 30, 60000, 16, 16, 16, 16], [200000, 35, 100000, 20, 20, 20, 20]]

# game category match
## TODO: NEEDS CONFIRM
BONUS_GAME_CATEGORY = {
    'casino': ['Games', 'Table Games'],
    'sports': ['Sports'],
    'live-casino': ['Live Casino'],
    'lottery': ['Lotteries'],
}


def calBonusCompletion(user, bonus, timestamp):
    return 0


# Helper function for file export to csv
# def exportCSV(body, filename):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename=' + filename + '.csv'
#
#     writer = csv.writer(response)
#     for i in body:
#         writer.writerow(i)
#
#     return response

class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def streamingExport(body, filename):
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in body),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=' + filename + '.csv'
    return response
