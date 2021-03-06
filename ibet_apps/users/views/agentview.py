from django.contrib.postgres.aggregates import ArrayAgg
from django.core import serializers
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse

from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Count, Sum, Q, F
from django.db.models.functions import TruncMonth, TruncYear, TruncDate, Coalesce
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from decimal import Decimal

from rest_framework import status
from rest_framework.response import Response
from xadmin.views import CommAdminView

from games.models import Category
from users.models import CustomUser, UserAction, PersonalCommissionLevel, UserActivity, ReferChannel, SystemCommissionLevel
from operation.models import Notification, NotificationToUsers
from utils.admin_helper import *

import logging
import simplejson as json
import datetime

from utils.redisClient import RedisClient
from utils.redisHelper import getDevicesByUserRedisKey, getUsersByDeviceRedisKey, RedisHelper

logger = logging.getLogger('django')


class AgentView(CommAdminView):
    def get(self, request):
        get_type = request.GET.get("type")

        if get_type == "getCommissionHistory":
            date = request.GET.get("date")
            start_date = utcToLocalDatetime(datetime.datetime.strptime(date, '%b %Y'))
            end_date = start_date + relativedelta(months=1)
            commission_transaction_this_month = getCommissionTrans().filter(
                Q(request_time__gte=start_date) & Q(request_time__lte=end_date))

            commission_this_month_record = []
            for tran in commission_transaction_this_month:
                user = tran.user_id
                downlines = getDownlines(user)

                tranDict = {'id': user.pk,
                            'trans_pk': tran.pk,
                            'active_players': filterActiveUser(downlines, start_date,
                                                               end_date, True, None).count(),
                            'downline_ftd': calculateFTD(downlines, start_date, end_date),
                            'commission_rate': getCommissionRate(user, start_date, end_date),
                            'deposit': getTransactionAmount(user, start_date, end_date, TRANSACTION_DEPOSIT, None)[1],
                            'withdrawal': getTransactionAmount(user, start_date, end_date, TRANSACTION_WITHDRAWAL, None)[1],
                            'bonus': getTransactionAmount(user, start_date, end_date, TRANSACTION_BONUS, None)[1],

                            'winorloss': calculateNGR(user, start_date, end_date, None),
                            'commission': tran.amount,
                            'status': "Released" if tran.status == TRAN_SUCCESS_TYPE else "Pending",
                            'release_time': str(utcToLocalDatetime(tran.arrive_time)),
                            'operator': tran.release_by.username if tran.release_by else "",
                            'operator_pk': tran.release_by.pk if tran.release_by else "",
                            }
                commission_this_month_record.append(tranDict)
            return HttpResponse(json.dumps(commission_this_month_record), content_type='application/json')

        elif get_type == "getAffiliateApplicationDetail":
            try:
                user_id = request.GET.get("user_id")
                user_obj = CustomUser.objects.get(pk=user_id)
                user_detail = {
                    'id': user_id,
                    'username': user_obj.username,
                    'first_name': user_obj.first_name or '',
                    'last_name': user_obj.last_name or '',
                    'email': user_obj.email or '',
                    'birthday': user_obj.date_of_birth or '',
                    'phone': user_obj.phone or '',
                    'address': user_obj.get_user_address(),
                    'email_verified': user_obj.email_verified,
                    'phone_verified': user_obj.phone_verified,
                    'address_verified': user_obj.address_verified,
                }
            except Exception as e:
                user_detail = {}
                logger.error("Error getting user detail " + str(e))

            return HttpResponse(json.dumps(user_detail), content_type='application/json')

        else:
            context = super().get_context()
            context['time'] = timezone.now()
            title = "Affiliate overview"
            context["breadcrumbs"].append({'url': '/affiliate_overview/', 'title': title})
            context["title"] = title


            # Commission Table
            # commission transaction group by month

            # filter out valid transaction(the affiliate needs to meet at least lowest commission level)
            valid_commission_tran = getCommissionTrans()
            for trans in getCommissionTrans():
                start_time = trans.request_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end_time = start_time + relativedelta(months=1)

                if getCommissionRate(trans.user_id, start_time, end_time) == 0:
                    valid_commission_tran = valid_commission_tran.exclude(pk=trans.pk)

            commission_group = valid_commission_tran.annotate(commission_release_month=TruncMonth('request_time', tzinfo=timezone.utc))

            # for each affiliate, will only generate one commission transaction per month
            commission_transactions = commission_group.values('commission_release_month') \
                .annotate(
                total_commission=Sum('amount'),
                total_count=Count('pk'),
                pending_num=Count('pk', filter=Q(status=TRAN_PENDING_TYPE)),
                aff_list=ArrayAgg('user_id')
            ).order_by('-commission_release_month')

            commission = []
            for trans in commission_transactions:
                active_downline = 0
                start_time = trans['commission_release_month']
                end_time = trans['commission_release_month'] + relativedelta(months=1)

                for aff in trans['aff_list']:
                    aff_obj = CustomUser.objects.get(pk=aff)
                    active_downline += filterActiveUser((getDownlines(aff_obj)), start_time, end_time, True, None).count()

                commission_dict = {
                    'commission_release_month': end_time,  # month
                    'affiliate_number': trans['total_count'],  # only one transaction per affiliate
                    'active_downline': active_downline,
                    'total_commission': trans['total_commission'],
                    'commission_status': "All released" if trans['pending_num'] == 0
                    else str(trans['pending_num']) + " Pending"
                }
                commission.append(commission_dict)
            context["commission_transaction"] = commission

            # Affiliate Application Table
            # users have not become agent, but alreay applied
            affiliate_application_list = users.filter(Q(user_to_affiliate_time=None) & ~Q(
                user_application_time=None)).order_by('-user_application_time')
            affiliate_application = []
            for user in affiliate_application_list:
                affiliate_application_dict = {
                    'pk': user.pk,
                    'user_application_time': utcToLocalDatetime(user.user_application_time)
                }
                affiliate_application.append(affiliate_application_dict)
            context["affiliate_application_list"] = affiliate_application

            # SYSTEM COMMISSION
            system_commission = SystemCommissionLevel.objects.all()
            # if there is no system commission, will set up a default one
            if len(system_commission) == 0:
                default_sc_level = SystemCommissionLevel(
                    commission_level=1,
                )
                default_sc_level.save()
            context["system_commission_type"] = system_commission.order_by('commission_level')
            context['operation_fee'] = 0.00
            context['payment_fee'] = 0.00
            if system_commission:
                context['operation_fee'] = system_commission.first().operation_fee
                context['payment_fee'] = system_commission.first().payment_fee
            return render(request, 'agent_list.html', context)

    def post(self, request):
        post_type = request.POST.get("type")

        # TODO: needs update after figuring operation fee and payment fee
        if post_type == "releaseCommission":
            # transaction pk list need to be released
            commissionList = request.POST.getlist("list[]")
            admin = request.POST.get("admin")
            if commissionList is not []:
                for trans_id in commissionList:
                    try:
                        with transaction.atomic():
                            current_trans = Transaction.objects.get(pk=trans_id)
                            admin_user = CustomUser.objects.get(username=admin)
                            user = current_trans.user_id
                            user.main_wallet += current_trans.amount
                            current_trans.status = TRAN_SUCCESS_TYPE
                            current_trans.review_status = REVIEW_APP
                            current_trans.arrive_time = timezone.now()
                            current_trans.release_by = admin_user
                            current_trans.save()
                            user.save()
                    except Exception as e:
                        logger.error("Error releasing Commission " + str(trans_id) + " " + str(e))

            return HttpResponse(status=200)

        elif post_type == "affiliateApplication":
            result = request.POST.get("result")
            remark = request.POST.get("remark")
            userID = request.POST.get("user_id")

            admin_user = request.POST.get("admin_user")
            try:
                user = CustomUser.objects.get(pk=userID)
                admin_user = CustomUser.objects.get(username=admin_user)
            except ObjectDoesNotExist as e:
                logger.error("Error getting user or admin " + str(e))

            try:
                with transaction.atomic():
                    if result == "Yes":
                        user.user_to_affiliate_time = timezone.now()
                        user.affiliate_status = 'Active'
                        # if this user was an affiliate or he/she referred other people before he/she becomes an affiliate
                        if user.referral_path:
                            referral_path = str(user.referral_path) + '/' + str(user.pk) + '/'
                        else:
                            referral_path = str(user.pk) + '/'

                        if user.referred_by:
                            try:
                                referral_path = str(user.referred_by.referral_path) + referral_path
                            except Exception as e:
                                logger.error("Error getting referrer's referral_path " + str(e))
                        user.referral_path = referral_path
                        user.save()
                        affiliate_default_commission = PersonalCommissionLevel.objects.create(
                            user_id=user,
                            commission_level=1,
                        )
                        logger.info(
                            "Auto add commission level 1 for new affiliate " + user.username)
                    else:
                        user.user_application_time = None
                    user.save()
                    if remark:
                        activity = UserActivity.objects.create(
                            user=user,
                            admin=admin_user,
                            message=remark,
                            activity_type=ACTIVITY_REMARK,
                        )

            except IntegrityError as e:
                logger.error("Error handling affiliate application " + str(e))

            return HttpResponse(status=200)

        elif post_type == 'systemCommissionChange':
            level_details = request.POST.get('level_details')
            admin_user = request.POST.get('admin_user')
            comments = request.POST.get('comments')
            operation_fee = request.POST.get('operation_fee')
            payment_fee = request.POST.get('payment_fee')

            level_details = json.loads(level_details)

            try:
                admin_user_obj = CustomUser.objects.get(username=admin_user)
                # add system commission change log
                admin_activity = UserActivity(
                    user=admin_user_obj,
                    admin=admin_user_obj,
                    message=comments,
                    activity_type=ACTIVITY_SYSTEM,
                )
                admin_activity.save()
            except Exception as e:
                logger.error('Error getting admin user object: ' + str(e))

            try:
                with transaction.atomic():

                    commission_list = []
                    # update commission levels
                    for i in level_details:
                        if i['pk'] == '':
                            current_commission = SystemCommissionLevel.objects.create(
                                commission_percentage=i['rate'],
                                downline_commission_percentage=i['downline_rate'],
                                commission_level=i['level'],
                                active_downline_needed=i['active_downline'],
                                monthly_downline_ftd_needed=i['downline_ftd'],
                                ngr=i['downline_ngr'],
                                operation_fee=operation_fee,
                                payment_fee=payment_fee,
                            )
                            current_commission.save()
                            commission_list.append(current_commission.pk)
                            logger.info(str(admin_user) + " create new system commission level " + i['level'])
                        else:
                            current_commission = SystemCommissionLevel.objects.filter(pk=int(i['pk']))
                            current_commission.update(
                                commission_percentage=i['rate'],
                                downline_commission_percentage=i['downline_rate'],
                                commission_level=i['level'],
                                active_downline_needed=i['active_downline'],
                                monthly_downline_ftd_needed=i['downline_ftd'],
                                ngr=i['downline_ngr'],
                                operation_fee=operation_fee,
                                payment_fee=payment_fee,
                            )
                            logger.info(str(admin_user) + "update commission level " + i['level'])
                            commission_list.append(i['pk'])

                    deleted_commission_levels = SystemCommissionLevel.objects.exclude(pk__in=commission_list)
                    deleted_list = deleted_commission_levels.values_list('commission_level', flat=True)
                    if deleted_list.count() > 0:
                        logger.info("Admin user " + admin_user + " delete commission level " + str(
                            deleted_list))
                        deleted_commission_levels.delete()

            except IntegrityError as e:
                logger.info('Error updating system commission setting: ' + str(e))
            return HttpResponse(status=200)

        # affiliate datatable
        elif post_type == "getAffiliateInfo":
            result = {}
            # the filter for affiliate
            length = int(request.GET.get('length', 20))
            start = int(request.GET.get('start', 0))
            search_value = request.GET.get('search', None)
            min_date = request.GET.get('minDate')
            max_date = request.GET.get('maxDate')
            min_date = dateToDatetime(min_date)
            max_date = dateToDatetime(max_date)

            # get affiliates
            queryset = CustomUser.objects.exclude(user_to_affiliate_time=None).order_by('pk')

            # TOTAL ENTRIES
            total = queryset.count()

            if min_date and max_date:
                queryset = filterActiveUser(queryset, min_date, max_date, False, None).order_by('pk')

            if search_value:
                queryset = queryset.filter(Q(pk__contains=search_value) | Q(username__icontains=search_value))

            # Commission Transaction filter by month
            commission_transaction_last_month = getCommissionTrans().filter(
                Q(arrive_time__gte=month_before_last) & Q(arrive_time__lte=last_month))

            commission_transaction_last_month_dict = dict(commission_transaction_last_month.values_list('user_id')
                                                          .annotate(total_commission=Coalesce(Sum('amount'), 0)))

            count = queryset.count()

            queryset = queryset[start:start + length]

            affiliate_list = []
            for affiliate in queryset:
                # downline list
                downlines = getPlayers(affiliate) or []
                downlines_all = getDownlines(affiliate) or []
                downlines_total_deposit = 0
                downlines_total_withdrawal = 0
                downlines_regis = calculateRegistrations(downlines, min_date, max_date)
                downlines_all_regis = calculateRegistrations(downlines_all, min_date, max_date)
                downlines_ftds = calculateFTD(downlines, min_date, max_date)
                downlines_all_ftds = calculateFTD(downlines_all, min_date, max_date)

                for downline in downlines:
                    downline_deposit_count, downline_deposit = getTransactionAmount(downline, min_date, max_date, TRANSACTION_DEPOSIT, None)
                    downline_withdrawal_count, downline_withdrawal = getTransactionAmount(downline, min_date,
                                                                                         max_date, TRANSACTION_WITHDRAWAL, None)
                    downlines_total_deposit += downline_deposit
                    downlines_total_withdrawal += downline_withdrawal

                deposit_count, deposit_amount = getTransactionAmount(affiliate, min_date, max_date, TRANSACTION_DEPOSIT, None)
                withdrawal_count, withdrawal_amount = getTransactionAmount(affiliate, min_date, max_date, TRANSACTION_WITHDRAWAL, None)
                active_players = filterActiveUser(downlines_all, min_date, max_date, True, None)
                active_players_without_freebets = filterActiveUser(downlines, min_date, max_date, False, None)
                sports_actives = filterActiveUser(downlines, min_date, max_date, True, "Sports")
                casino_actives = filterActiveUser(downlines, min_date, max_date, True, "Casino")
                live_casino_actives = filterActiveUser(downlines, min_date, max_date, True, "Live Casino")
                lottery_actives = filterActiveUser(downlines, min_date, max_date, True, "Lottery")
                active_downlines = filterActiveUser(downlines, min_date, max_date, True, None)
                downline_active_players = filterActiveUser(downlines_all, min_date, max_date, True, None)

                # Todo: needs update the data
                affiliates_dict = {'affiliate_id': affiliate.pk,
                                   'affiliate_username': affiliate.username,
                                   'balance': affiliate.main_wallet + affiliate.other_game_wallet,
                                   'status': affiliate.affiliate_status,
                                   'commission_last_month': commission_transaction_last_month_dict.get(affiliate.pk,
                                                                                                       0),
                                   'registrations': downlines_all_regis,
                                   'ftds': downlines_all_ftds,
                                   'active_players': active_players.count() if active_players else 0,
                                   'active_players_without_freebets':active_players_without_freebets.count()
                                   if active_players_without_freebets else 0,
                                   'turnover': calculateTurnover(affiliate, min_date, max_date, None),
                                   'ggr': calculateGGR(affiliate, min_date, max_date, None),
                                   'bonus_cost': getTransactionAmount(affiliate, min_date, max_date, TRANSACTION_BONUS, None)[1],
                                   'ngr': calculateNGR(affiliate, min_date, max_date, None),

                                   'deposit': deposit_amount,
                                   'withdrawal': withdrawal_amount,

                                   'sports_actives': sports_actives.count() if sports_actives else 0,
                                   'sports_ggr': calculateGGR(affiliate, min_date, max_date, "Sports"),
                                   'sports_bonus': getTransactionAmount(affiliate, min_date, max_date, TRANSACTION_BONUS, GAME_TYPE_SPORTS)[1],
                                   'sports_ngr': calculateNGR(affiliate, min_date, max_date, "Sports"),

                                   'casino_actives': casino_actives.count() if casino_actives else 0,
                                   'casino_ggr': calculateGGR(affiliate, min_date, max_date, "Casino"),
                                   'casino_bonus': getTransactionAmount(affiliate, min_date, max_date, TRANSACTION_BONUS, GAME_TYPE_GAMES)[1]
                                                   + getTransactionAmount(affiliate, min_date, max_date, TRANSACTION_BONUS, GAME_TYPE_TABLE_GAMES)[1],
                                   'casino_ngr': calculateNGR(affiliate, min_date, max_date, "Casino"),

                                   'live_casino_actives': live_casino_actives.count() if live_casino_actives else 0,
                                   'live_casino_ggr': calculateGGR(affiliate, min_date, max_date, "Live Casino"),
                                   'live_casino_bonus': getTransactionAmount(affiliate, min_date, max_date,
                                                                       TRANSACTION_BONUS, GAME_TYPE_LIVE_CASINO),
                                   'live_casino_ngr': calculateNGR(affiliate, min_date, max_date, GAME_TYPE_LIVE_CASINO),

                                   'lottery_actives': lottery_actives.count() if lottery_actives else 0,
                                   'lottery_ggr': calculateGGR(affiliate, min_date, max_date, "Lottery"),
                                   'lottery_bonus': getTransactionAmount(affiliate, min_date, max_date, TRANSACTION_BONUS, GAME_TYPE_LOTTORY)[1],
                                   'lottery_ngr': calculateNGR(affiliate, min_date, max_date, "Lottery"),

                                   'active_downlines': active_downlines.count() if active_downlines else 0,
                                   'downline_registration': downlines_all_regis - downlines_regis,
                                   'downline_ftds': downlines_all_ftds - downlines_ftds,
                                   'downline_new_players': calculateNewPlayer(downlines_all, min_date, max_date,
                                                                              True),
                                   'downline_active_players': downline_active_players.count() if downline_active_players else 0,

                                   'downline_turnover': -1,
                                   'downline_ggr': -1,
                                   'downline_bonus_cost': -1,
                                   'downline_ngr': -1,

                                   'downline_deposit': -1,
                                   'downline_withdrawal': -1,
                                   }
                affiliate_list.append(affiliates_dict)

            result['data'] = affiliate_list
            result['recordsTotal'] = total
            result['recordsFiltered'] = count
            return HttpResponse(json.dumps(result), content_type="application/json")


def getDownlineList(queryset, start_time, end_time):
    downline_list = []

    for downline in queryset:
        downline_dict = {
            'player_id': downline.pk,
            'channel': str(downline.referred_by_channel or ''),
            'ftd': str(downline.ftd_time),
            'registration_date': str(utcToLocalDatetime(downline.time_of_registration)),
            'last_login': str(lastLogin(downline)),
            'total_deposit': getTransactionAmount(downline, start_time, end_time, TRANSACTION_DEPOSIT, None)[1],
            'total_withdrawal': getTransactionAmount(downline, start_time, end_time, TRANSACTION_WITHDRAWAL, None)[1],
            'total_bonus': getTransactionAmount(downline, start_time, end_time, TRANSACTION_BONUS, None)[1],
            'total_adjustment': getTransactionAmount(downline, start_time, end_time, TRANSACTION_ADJUSTMENT, None)[1],
            'balance': downline.main_wallet,
            'turnover': calculateTurnover(downline, start_time, end_time, None),
        }

        downline_list.append(downline_dict)

    return downline_list


class AgentDetailView(CommAdminView):

    def get(self, request, *args, **kwargs):
        get_type = request.GET.get("type")

        if get_type == 'search_affiliate_manager':
            text = request.GET.get('text')
            manager_id_list = CustomUser.objects.values('managed_by').distinct()
            manager_name_list = CustomUser.objects.filter(
                pk__in=manager_id_list).values('username')
            recontents = CustomUser.objects.filter(
                pk__in=manager_id_list).filter(username__startswith=text)
            rejson = []
            for recontent in recontents:
                rejson.append(recontent.username)
            return HttpResponse(json.dumps(rejson), content_type='application/json')

        elif get_type == 'downlinePerformance':

            draw = int(request.GET.get('draw', 1))
            length = int(request.GET.get('length', 20))
            start = int(request.GET.get('start', 0))
            # user member status
            account_type = int(request.GET.get('accountType', -1))
            channel = request.GET.get('channel', -1)
            min_date = request.GET.get('minDate', None)
            max_date = request.GET.get('maxDate', None)
            affiliate_id = request.GET.get('affiliateId')
            try:
                affiliate = CustomUser.objects.get(pk=affiliate_id)
            except Exception as e:
                logger.error("Error getting User object: ", e)

            queryset = getPlayers(affiliate)

            #  TOTAL ENTRIES
            total = queryset.count()

            if min_date and max_date:
                queryset = filterActiveUser(queryset, dateToDatetime(min_date),
                                            dateToDatetime(max_date), True, None).order_by('-created_time')

            # -1 is All Type for filter
            if account_type != -1:
                queryset = queryset.filter(member_status=account_type)

            if channel != '-1':
                queryset = queryset.filter(referred_by_channel__refer_channel_name=channel)

            #  TOTAL ENTRIES AFTER FILTERED
            count = queryset.count()

            queryset = queryset.order_by('-time_of_registration')
            queryset = queryset[start:start + length]

            queryset = getDownlineList(queryset, min_date, max_date)

            result = {
                'data': queryset,
                'draw': draw,
                'recordsTotal': total,
                'recordsFiltered': count,
            }
            return HttpResponse(json.dumps(result), content_type='application/json')

        else:
            context = super().get_context()
            export_title = request.GET.get('tableHead')

            affiliate = CustomUser.objects.get(pk=self.kwargs.get('pk'))
            title = "Affiliate " + affiliate.username

            downline = getDownlines(affiliate)
            downline_deposit = Transaction.objects.filter(Q(transaction_type=TRANSACTION_DEPOSIT) &
                                                          Q(user_id__in=downline) & Q(status=TRAN_SUCCESS_TYPE)).\
                aggregate(total_deposit=Coalesce(Sum('amount'), 0))

            user_transaction = Transaction.objects.filter(user_id=affiliate)
            affiliate_commission_tran = user_transaction.filter(
                Q(transaction_type=TRANSACTION_COMMISSION) & Q(status=TRAN_SUCCESS_TYPE))

            context["title"] = title
            context["breadcrumbs"].append({'url': '/cwyadmin/', 'title': title})
            context['time'] = timezone.now()

            # AFFILIATE DETAILS
            context["affiliate"] = affiliate
            context["name"] = affiliate.username
            context["id"] = affiliate.id
            context["manager"] = affiliate.affiliate_managed_by.username if affiliate.affiliate_managed_by else ""
            context["balance"] = affiliate.main_wallet
            # context["affiliate_referee"] = downline
            context["affiliate_level"] = affiliate.affiliate_level
            context["affiliate_status"] = affiliate.affiliate_status
            context["transerfer_between_levels"] = affiliate.transerfer_between_levels

            # COMMISSION
            context["commission_this_month"] = affiliate_commission_tran.filter(arrive_time__gte=
                this_month).aggregate(amount=Coalesce(Sum('amount'), 0))

            context["commission_last_month"] = affiliate_commission_tran.filter(
                Q(arrive_time__lte=this_month)
                & Q(arrive_time__gte=last_month)).aggregate(amount=Coalesce(Sum('amount'), 0))

            context["commission_before_last"] = affiliate_commission_tran.filter(
                Q(request_time__lte=last_month)
                & Q(request_time__gte=month_before_last)).aggregate(amount=Coalesce(Sum('amount'), 0))

            context["commission_set"] = affiliate.commission_setting
            context["transfer_between_levels"] = affiliate.transerfer_between_levels

            # COMMISSION POP UP
            commission_history = []
            commission_history_export = []
            for commission in affiliate_commission_tran:
                commission_detail = commission.other_data
                commission_month = commission.arrive_time - relativedelta(month=1)

                commission_start_time = utcToLocalDatetime(commission_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0))
                commission_end_time = commission_start_time + relativedelta(months=1)
                commission_dict = {
                    'month': datetime.datetime.strftime(commission_month, '%b %Y'),
                    'active_players': commission_detail.get('active_players') or 0,
                    'downline_ftds': commission_detail.get('downline_ftds') or 0,
                    'commission_rate': commission_detail.get('commission_rate') or 0,
                    'deposit': getTransactionAmount(affiliate, commission_start_time, commission_end_time, TRANSACTION_DEPOSIT, None)[1],
                    'withdrawal': getTransactionAmount(affiliate, commission_start_time, commission_end_time, TRANSACTION_WITHDRAWAL, None)[1],
                    'bonus': getTransactionAmount(affiliate, commission_start_time, commission_end_time, TRANSACTION_BONUS, None)[1],
                    'total_winloss': calculateTurnover(affiliate, commission_start_time, commission_end_time, None),
                    'commission': commission.amount,
                    'release_time': datetime.datetime.strftime(commission.arrive_time, '%b %d %Y, %H:%M'),
                    'operator': commission.release_by
                }
                commission_history.append(commission_dict)
                if export_title:
                    commission_history_export.append(list(commission_dict.values()))
            context['commission_trans'] = commission_history

            if export_title:
                export_title = json.loads(export_title)
                commission_history_export.insert(0, export_title)
                return streamingExport(commission_history_export, 'Affiliate ' + str(affiliate.username) + ' Monthly Commission History')

            # COMMISSION LEVELS
            context["system_commission_levels"] = SystemCommissionLevel.objects.all().order_by('commission_level')
            context["personal_commission_levels"] = PersonalCommissionLevel.objects.filter(user_id=affiliate).order_by('commission_level')

            # DOWNLINE STATUS
            context["downline_number"] = getDownlines(affiliate).count()
            context["active_users"] = filterActiveUser(getDownlines(affiliate), None, None, True, None).count()
            context["downline_deposit"] = downline_deposit['total_deposit'] or 0
            context["downline_turnover"] = calculateTurnover(affiliate, None, None, None)
            context["downline_ggr"] = calculateGGR(affiliate, None, None, None)
            context["click_number"] = 0     ## TODO: track link
            context['domain'] = LETOU_DOMAIN
            context['referral_code'] = affiliate.referral_code

            try:
                context["promotion_link"] = ReferChannel.objects.get(
                    user_id=affiliate, refer_channel_name="default").pk
            except ObjectDoesNotExist:
                context["promotion_link"] = ""
            context["promotion_link_list"] = ReferChannel.objects.filter(
                user_id=affiliate)

            try:
                RedisClient().connect()
                redis = RedisHelper()
            except Exception as e:
                logger.error("There is something wrong with redis connection: " + str(e))

            # related affiliates: share the same device
            try:
                device = redis.get_devices_by_user(affiliate)
                related_user_list = None
                related_affiliates_data = []
                if device:
                    related_user_list = redis.get_users_by_device(device.pop().decode('utf-8'))

                while related_user_list:
                    username = related_user_list.pop().decode('utf-8')
                    related_user = CustomUser.objects.get(username=username)
                    if related_user == affiliate or related_user.user_to_affiliate_time is None:
                        continue
                    related_affiliates_info = {'member_id': related_user.pk,
                                               'balance': related_user.main_wallet}
                    related_affiliates_data.append(related_affiliates_info)
                context["related_affiliates"] = related_affiliates_data
            except Exception as e:
                logger.error("Error getting related affiliates: " + str(e))

            # DETAIL PAGE
            manager = affiliate.affiliate_managed_by
            if manager is None:
                context["manager"] = ""
            else:
                context["manager"] = manager

            #=====================================================

            # ACTIVITY
            user_activities = UserActivity.objects.filter(user=affiliate)
            user_activities_list = []
            for key, value in ACTIVITY_TYPE:
                user_activities_list.append(value)
            context["user_activities"] = user_activities
            context["user_activities_list"] = user_activities_list

            # DOWNLINE LIST TABLE
            downline_list_table = []
            for i in affiliate.referees.all():
                downline_info = {}
                affiliate_tran = Transaction.objects.filter(user_id=i)
                downline_info['affiliate_id'] = i.pk
                downline_info['username'] = i.username
                downline_info['time_of_registration'] = i.time_of_registration
                if i.last_login_time is None:
                    downline_info['last_login_time'] = ""
                else:
                    downline_info['last_login_time'] = i.last_login_time

                if i.ftd_time is None:
                    downline_info['ftd_time'] = ""
                else:
                    downline_info['ftd_time'] = utcToLocalDatetime(i.ftd_time)

                downline_info['channel'] = ""
                downline_info['deposit'] = affiliate_tran.filter(
                    transaction_type=TRANSACTION_DEPOSIT).aggregate(sum_deposit=Coalesce(Sum('amount'), 0))
                downline_info['withdraw'] = affiliate_tran.filter(
                    transaction_type=TRANSACTION_WITHDRAWAL).aggregate(sum_withdraw=Coalesce(Sum('amount'), 0))
                downline_info['bouns'] = affiliate_tran.filter(
                    transaction_type=TRANSACTION_BONUS).aggregate(sum_bouns=Coalesce(Sum('amount'), 0))
                downline_info['adjustment'] = affiliate_tran.filter(
                    transaction_type=TRANSACTION_ADJUSTMENT).aggregate(sum_adjustment=Coalesce(Sum('amount'), 0))
                downline_info['turnover'] = calculateTurnover(i, None, None, None)
                downline_info['balance'] = i.main_wallet
                downline_list_table.append(downline_info)
            context["downline_list"] = downline_list_table

            # CHANNEL REPORT TABLE
            channel_repost = []
            user_channel = ReferChannel.objects.filter(
                user_id=affiliate).values_list('pk').distinct()
            user_channel_list = ReferChannel.objects.filter(pk__in=user_channel)
            # DOWNLINE LIST - FILTER
            context["account_types"] = MEMBER_STATUS
            # TODO: needs to change to risk status
            # affiliate refer channels
            context["channel_list"] = ReferChannel.objects.filter(user_id=affiliate) \
                .values_list('refer_channel_name', flat=True)

            # Total commission
            context["total_commission"] = getCommissionTrans().aggregate(
                total_commission=Coalesce(Sum('amount'), 0))['total_commission']

            context["managers"] = getManagerList("Affiliate")
            context["empty_manager_group"] = "Please create Affiliate Manager group in System Admin. "
            return render(request, "agent_detail.html", context)

    def post(self, request):
        post_type = request.POST.get("type")
        affiliate_id = request.POST.get("affiliate_id")
        admin_user = request.POST.get('admin_user')
        if post_type == 'activity_filter':
            activity_type = request.POST.get('activity_type')
            for key, value in ACTIVITY_TYPE:
                if value == activity_type:
                    activity_type = key
            if activity_type == 'All':
                activities = UserActivity.objects.filter(
                    user=affiliate_id).order_by('-created_time')
            else:
                activities = UserActivity.objects.filter(Q(user=affiliate_id) & Q(
                    activity_type=activity_type)).order_by('-created_time')
            activities = serializers.serialize('json', activities)
            activities = json.loads(activities)
            response = []
            for act in activities:
                actDict = {}
                try:
                    time = datetime.datetime.strptime(
                        act['fields']['created_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    time = datetime.datetime.strptime(
                        act['fields']['created_time'], "%Y-%m-%dT%H:%M:%SZ")
                time = time.strftime("%B %d, %Y, %I:%M %p")
                actDict['time'] = time
                adminUser = CustomUser.objects.get(pk=act['fields']['admin'])
                actDict['adminUser'] = str(adminUser.username)
                actDict['message'] = act['fields']['message']
                response.append(actDict)

            return HttpResponse(json.dumps(response), content_type='application/json')

        elif post_type == 'update_message':
            message = request.POST.get('message')

            UserActivity.objects.create(
                user=CustomUser.objects.filter(pk=affiliate_id).first(),
                admin=CustomUser.objects.filter(username=admin_user).first(),
                message=message,
                activity_type=3,
            )
            logger.info('Finished create activity to DB')
            return HttpResponse(status=200)

        elif post_type == 'make_adjustment':
            admin_user = CustomUser.objects.get(username=admin_user)
            affiliate_id = CustomUser.objects.get(pk=affiliate_id)
            remark = request.POST.get('remark')
            amount = request.POST.get('amount')
            amount = Decimal(amount)
            send = request.POST.get('send')
            subject = request.POST.get('subject')
            text = request.POST.get('text')

            with transaction.atomic():
                new_adjustment = Transaction.objects.create(
                    user_id=affiliate_id,
                    amount=amount,
                    status=TRAN_SUCCESS_TYPE,
                    transaction_type=TRANSACTION_ADJUSTMENT,
                    remark=remark,
                    release_by=admin_user,
                )
                new_adjustment.save()
                affiliate_id.main_wallet += amount
                affiliate_id.save()
                logger.info(admin_user.username + " creates a new adjustment for affiliate " +
                            affiliate_id.username + " with the amount " + str(amount))
            if send == "true":
                with transaction.atomic():
                    # create a message
                    new_notication = Notification.objects.create(
                        subject=subject,
                        content_text=text,
                        creator=admin_user,
                    )
                    new_notication.save()
                    # send it to affilite
                    new_log = NotificationToUsers.objects.create(
                        notification_id=new_notication.pk,
                        notifier_id=affiliate_id,
                    )
                    logger.info(admin_user.username + " send a message to affiliate " +
                                affiliate_id.username + " with the subject " + subject)
            return HttpResponse(status=200)

        elif post_type == 'remove_refer_link':
            link_id = request.POST.get('refer_link')
            link_obj = ReferChannel.objects.get(pk=link_id)
            if link_obj:
                link_obj.delete()
            logger.info(str(admin_user) + " delete channel " +
                        str(link_obj.refer_channel_name) + " for affiliate " + str(affiliate_id))

            return HttpResponse(status=200)

        elif post_type == 'affiliate_audit':
            affiliate_id = request.POST.get('affiliate_id')
            affiliate_detail = request.POST.getlist('affiliate_detail[]')
            admin_user = request.POST.get('admin_user')
            level_detail = request.POST.get('level_details')
            manager = request.POST.get('manager')
            level_details = json.loads(level_detail)
            affiliate = CustomUser.objects.get(pk=affiliate_id)

            try:
                manager = CustomUser.objects.get(username=manager)
                affiliate.affiliate_managed_by = manager
            except CustomUser.DoesNotExist:
                manager = affiliate.affiliate_managed_by

            commission_list = []

            if affiliate_detail[3] == 'System':
                # update commission levels
                for i in level_details:
                    if i['pk'] == '':
                        current_commission = SystemCommissionLevel.objects.create(
                            commission_percentage=i['rate'],
                            downline_commission_percentage=i['downline_rate'],
                            commission_level=i['level'],
                            active_downline_needed=i['active_downline'],
                            monthly_downline_ftd_needed=i['downline_ftd'],
                            ngr=i['downline_ngr']
                        )
                        current_commission.save()
                        commission_list.append(current_commission.pk)
                        logger.info("Create new system commission level " + i['level'])
                    else:
                        current_commission = SystemCommissionLevel.objects.filter(pk=i['pk'])
                        current_commission.update(
                            commission_percentage=i['rate'],
                            downline_commission_percentage=i['downline_rate'],
                            commission_level=i['level'],
                            active_downline_needed=i['active_downline'],
                            monthly_downline_ftd_needed=i['downline_ftd']
                        )
                        logger.info("Update system commission level " + i['level'])
                        commission_list.append(i['pk'])
                deleted_commission_levels = SystemCommissionLevel.objects.exclude(
                    pk__in=commission_list)
                deleted_list = deleted_commission_levels.values_list('commission_level', flat=True)
                if deleted_list.count() > 0:
                    logger.info("Admin user " + str(admin_user) + " delete system commission level " + str(
                        deleted_list))
                deleted_commission_levels.delete()

            else:
                # update commission levels
                for i in level_details:
                    if i['pk'] == '':
                        current_commission = PersonalCommissionLevel.objects.create(
                            user_id=affiliate,
                            commission_percentage=i['rate'],
                            downline_commission_percentage=i['downline_rate'],
                            commission_level=i['level'],
                            active_downline_needed=i['active_downline'],
                            monthly_downline_ftd_needed=i['downline_ftd'],
                            ngr=i['downline_ngr']
                        )
                        current_commission.save()
                        commission_list.append(current_commission.pk)
                        logger.info("Create new commission level " +
                                    i['level'] + " for affiliate " + affiliate.username)
                    else:
                        current_commission = PersonalCommissionLevel.objects.filter(pk=i['pk'])
                        current_commission.update(
                            commission_percentage=i['rate'],
                            downline_commission_percentage=i['downline_rate'],
                            commission_level=i['level'],
                            active_downline_needed=i['active_downline'],
                            monthly_downline_ftd_needed=i['downline_ftd']
                        )
                        logger.info("Update commission level " +
                                    i['level'] + " for affiliate " + affiliate.username)
                        commission_list.append(i['pk'])
                deleted_commission_levels = PersonalCommissionLevel.objects.filter(user_id=affiliate).exclude(pk__in=commission_list)
                deleted_list = deleted_commission_levels.values_list('commission_level', flat=True)
                if deleted_list.count() > 0:
                    logger.info("Admin user " + str(admin_user) + " delete commission level " + str(
                        deleted_list) + " for affiliate " + str(affiliate.username))
                deleted_commission_levels.delete()





            # ['wluuuu', 'Normal', 'Enable', 'System', 'No']
            # update affilite attributes
            manager = affiliate_detail[0]
            affiliate.affiliate_level = affiliate_detail[1]
            if affiliate_detail[2] == "Enable":
                affiliate.affiliate_status = "Active"
            else:
                affiliate.affiliate_status = "Deactivated"
            affiliate.commission_setting = affiliate_detail[3]
            if affiliate_detail[4] == "Yes":
                affiliate.transerfer_between_levels = True
            else:
                affiliate.transerfer_between_levels = False
            affiliate.save()
            logger.info("Update info for affiliate " + affiliate.username)
            return HttpResponse(status=200)

        elif post_type == 'send_message':
            admin_user = CustomUser.objects.get(username=admin_user)
            affiliate_id = CustomUser.objects.get(pk=affiliate_id)
            subject = request.POST.get('subject')
            text = request.POST.get('text')
            return HttpResponse(status=200)

        elif post_type == 'add_referral_channel':
            affiliate_id = request.POST.get('affiliate_id')
            new_channel_name = request.POST.get('new_channel_name')
            affiliate = CustomUser.objects.get(pk=affiliate_id)
            try:
                new_channel = ReferChannel.objects.create(
                    user_id=affiliate,
                    refer_channel_name=new_channel_name
                )
                response = {
                    'pk': new_channel.pk,
                    'link': str(LETOU_DOMAIN) + str(affiliate.referral_code) + '/' + str(new_channel.pk),
                    'time': str(new_channel.generated_time),
                    'name': new_channel_name
                }
                logger.info("Create new refer channel {} for affiliate {}".format(new_channel_name, affiliate.username))
                return HttpResponse(json.dumps(response))
            except IntegrityError as e:
                logger.info("Duplicate Refer Channel Name " + str(e))
                response = JsonResponse({"error": "Duplicate Refer Channel Name, Please Try Again!"})
                response.status_code = 400
                return response
