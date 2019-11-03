from django.contrib.auth import get_user_model
from django.core import serializers
from django.http import HttpResponse

from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth, TruncYear, TruncDate, Coalesce
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from decimal import Decimal

from xadmin.views import CommAdminView
from users.models import CustomUser, UserAction, Commission, UserActivity, ReferChannel, SystemCommission
from operation.models import Notification, NotificationToUsers
from utils.admin_helper import *

import logging
import simplejson as json
import datetime

logger = logging.getLogger('django')


class AgentView(CommAdminView):
    def get(self, request):
        get_type = request.GET.get("type")

        if get_type == "getCommissionHistory":
            date = request.GET.get("date")
            date = utcToLocalDatetime(datetime.datetime.strptime(date, '%b %Y'))
            commission_transaction_this_month = Transaction.objects.filter(
                Q(transaction_type=TRANSACTION_COMMISSION) & Q(request_time__gte=date) & Q(
                    request_time__lte=date + relativedelta(months=1)))

            commission_this_month_record = []

            for commission_transaction in commission_transaction_this_month:
                tranDict = {}
                user_id = commission_transaction.user_id
                tranDict['id'] = user_id.pk
                tranDict['trans_pk'] = commission_transaction.pk
                tranDict['active_players'] = calculateActiveDownlineNumber(user_id)
                tranDict['downline_ftd'] = calculateFTD(
                    commission_transaction.user_id.referees.all(), date - relativedelta(months=1), date)
                affiliate_last_commission_level = Commission.objects.filter(
                    user_id=commission_transaction.user_id).last()
                if affiliate_last_commission_level in [None, '']:
                    tranDict['commission_rate'] = 0
                else:
                    tranDict['commission_rate'] = str(
                        affiliate_last_commission_level.commission_percentage)

                tranDict['deposit'] = deposit_tran.filter(user_id=user_id).aggregate(
                    total_deposit=Coalesce(Sum('amount'), 0))['total_deposit']
                tranDict['withdrawal'] = withdrawal_tran.filter(user_id=user_id).aggregate(
                    total_withdrawal=Coalesce(Sum('amount'), 0))['total_withdrawal']
                tranDict['bonus'] = bonus_tran.filter(user_id=user_id).aggregate(
                    total_bonus=Coalesce(Sum('amount'), 0))['total_bonus']
                # query from bet history
                tranDict['winorloss'] = 0
                tranDict['commission'] = \
                    commission_tran.filter(Q(user_id=user_id) & Q(request_time__gte=date)).aggregate(
                        total_commission=Coalesce(Sum('amount'), 0))['total_commission']
                if commission_transaction.status == TRAN_APPROVED_TYPE:
                    tranDict['status'] = "Released"
                else:
                    tranDict['status'] = "Pending"
                if commission_transaction.arrive_time:
                    tranDict['release_time'] = str(utcToLocalDatetime(commission_transaction.arrive_time))
                else:
                    tranDict['release_time'] = ""

                tranDict['operator'] = ""

                commission_this_month_record.append(tranDict)
            return HttpResponse(json.dumps(commission_this_month_record), content_type='application/json')

        elif get_type == "getAffiliateApplicationDetail":
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
                'address': user_obj.get_user_address()
            }
            # user_detail['email_verified'] = user_obj.

            return HttpResponse(json.dumps(user_detail), content_type='application/json')

        else:
            context = super().get_context()
            context['time'] = timezone.now()
            title = "Affiliate overview"
            context["breadcrumbs"].append(
                {'url': '/affiliate_overview/', 'title': title})
            context["title"] = title

            # user-affiliate-group
            users = CustomUser.objects.all()
            # the filter for affiliate
            affiliates = CustomUser.objects.exclude(
                user_to_affiliate_time=None)

            downline_list = getDownline(users)

            # commission transaction
            commission_transaction = Transaction.objects.filter(
                transaction_type=TRANSACTION_COMMISSION)
            commission_transaction_last_month = commission_transaction.filter(
                Q(request_time__gte=last_month) & Q(request_time__lte=this_month))
            commission_transaction_last_month_before = commission_transaction.filter(
                Q(request_time__gte=before_last_month) & Q(request_time__lte=last_month))
            commission_transaction_month_before = Transaction.objects.filter(
                request_time__gte=before_last_month)

            transaction_this_month = Transaction.objects.filter(
                request_time__gte=last_month)

            # Overview

            # AFFILIATES COUNT
            context["affiliate"] = affiliates
            context["active_number"] = users.filter(
                affiliate_status='Active').count()
            context["deactivated_number"] = users.filter(
                affiliate_status='Deactivated').count()
            context["vip_number"] = users.filter(
                affiliate_status='VIP').count()
            context["negative_number"] = users.filter(
                affiliate_status='Negative').count()

            # FTD THIS MONTH
            context["ftd_this_month"] = affiliates.filter(
                ftd_time__gte=last_month).count()

            # ACTIVE THIS MONTH
            context["actives_this_month"] = bet_tran.filter(Q(request_time__gte=last_month) & Q(
                user_id__in=affiliates)).values_list('user_id').distinct().count()

            # GGR NEEDS BET TRANSACTION TABLE
            context["ggr_this_month"] = "/"

            # AFFILIATES ACQUIRED THIS MONTH
            context["affiliates_acquired_this_month"] = affiliates.filter(
                user_to_affiliate_time__gte=last_month).count()

            # Commission Table
            commission_transactions = commission_transaction.annotate(
                commission_release_month=TruncMonth('request_time')).values(
                'commission_release_month').annotate(total_commission=Sum('amount')).order_by(
                '-commission_release_month')

            commission = []
            for trans in commission_transactions:
                commission_dict = {}
                current_month = trans['commission_release_month']
                commission_dict['commission_release_month'] = current_month
                commission_dict['total_commission'] = trans['total_commission']
                affiliates_this_month = affiliates.filter(
                    user_to_affiliate_time__gte=current_month + relativedelta(months=1))
                commission_dict['affiliate_number'] = affiliates_this_month.count()
                downline_list_this_month = getDownline(affiliates_this_month)
                commission_dict['active_downline'] = bet_tran.filter(
                    user_id__in=affiliates).values_list('user_id').distinct().count()

                # commission status(tran_type=commission, user_id in affiliate, month=current month)
                commission_status = commission_transaction.filter(Q(request_time__gte=current_month) & Q(
                    request_time__lte=current_month + relativedelta(months=1)) & ~Q(status=TRAN_APPROVED_TYPE)).count()
                if commission_status == 0:
                    commission_dict['commission_status'] = "All released"
                else:
                    commission_dict['commission_status'] = str(
                        commission_status) + " Pending"
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

            # Affliates Table
            affiliates_table = []

            if affiliates.count() > 0:
                for affiliate in affiliates:
                    affiliates_dict = {}
                    affiliates_dict['id'] = affiliate.pk
                    affiliates_dict['manager'] = ""
                    if affiliate.managed_by:
                        affiliates_dict['manager'] = affiliate.managed_by.username
                    # downline list

                    downlines = getDownline(affiliate)
                    downlines_deposit = 0

                    for downline in downlines:
                        downlines_deposit += deposit_tran.filter(user_id=downline).aggregate(
                            total_deposit=Coalesce(Sum('amount'), 0))['total_deposit']
                    affiliates_dict['active_users'] = calculateActiveDownlineNumber(affiliate)
                    affiliates_dict['downlines_deposit'] = downlines_deposit
                    affiliates_dict['turnover'] = 0
                    affiliates_dict['downlines_ggr'] = 0
                    affiliates_dict['commission_last_month'] = commission_transaction_last_month_before.filter(
                        user_id=affiliate).aggregate(total_commission=Coalesce(Sum('amount'), 0))['total_commission']
                    affiliates_dict['commission_month_before'] = commission_transaction_month_before.filter(
                        user_id=affiliate).aggregate(total_commission=Coalesce(Sum('amount'), 0))['total_commission']
                    affiliates_dict['balance'] = affiliate.main_wallet + \
                                                 affiliate.other_game_wallet
                    affiliates_dict['status'] = affiliate.affiliate_status
                    affiliates_dict['level'] = affiliate.affiliate_level
                    affiliates_table.append(affiliates_dict)
            context["affiliates_table"] = affiliates_table

            # SYSTEM COMMISSION
            system_commission = SystemCommission.objects.all()
            # if there is no system commission, will set up a default one
            if len(system_commission) == 0:
                default_sc_level = SystemCommission(
                    commission_level=1,
                )
                default_sc_level.save()
            context["system_commission_type"] = system_commission.order_by('commission_level')

            return render(request, 'agent_list.html', context)

    def post(self, request):
        post_type = request.POST.get("type")

        if post_type == "releaseCommission":
            # transaction pk list need to be released
            commissionList = request.POST.getlist("list[]")
            if commissionList is not []:
                for trans_id in commissionList:
                    current_trans = Transaction.objects.get(pk=trans_id)
                    if current_trans is None:
                        logger.error(
                            "Cannot find Commission History " + trans_id)
                    else:
                        current_trans.status = TRAN_APPROVED_TYPE
                        current_trans.arrive_time = timezone.now()
                        current_trans.save()
            return HttpResponse(status=200)
        elif post_type == "affiliateApplication":
            result = request.POST.get("result")
            remark = request.POST.get("remark")
            userID = request.POST.get("user_id")

            admin_user = request.POST.get("admin_user")
            user = CustomUser.objects.get(pk=userID)

            admin_user = CustomUser.objects.get(username=admin_user)
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
                        logger.error("Error referrer's referral_path " + str(e))
                user.referral_path = referral_path
                user.save()
                affiliate_default_commission = Commission.objects.create(
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
            return HttpResponse(status=200)

        elif post_type == 'systemCommissionChange':
            level_details = request.POST.get('level_details')
            admin_user = request.POST.get('admin_user')
            comments = request.POST.get('comments')

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
                logger.info('Error get admin user object: ' + str(e))

            commission_list = []
            # update commission levels
            for i in level_details:
                if i['pk'] == '':
                    current_commission = SystemCommission.objects.create(
                        commission_percentage=i['rate'],
                        downline_commission_percentage=i['downline_rate'],
                        commission_level=i['level'],
                        active_downline_needed=i['active_downline'],
                        monthly_downline_ftd_needed=i['downline_ftd'],
                        ngr=i['downline_ngr'],
                    )
                    current_commission.save()
                    commission_list.append(current_commission.pk)
                    logger.info(str(admin_user) + " create new system commission level " + i['level'])
                else:
                    current_commission = SystemCommission.objects.filter(pk=i['pk'])
                    current_commission.update(
                        commission_percentage=i['rate'],
                        downline_commission_percentage=i['downline_rate'],
                        commission_level=i['level'],
                        active_downline_needed=i['active_downline'],
                        monthly_downline_ftd_needed=i['downline_ftd'],
                        ngr=i['downline_ngr'],
                    )
                    logger.info(str(admin_user) + "update commission level " + i['level'])
                    commission_list.append(i['pk'])

            deleted_commission_levels = SystemCommission.objects.exclude(pk__in=commission_list)
            deleted_list = deleted_commission_levels.values_list('commission_level', flat=True)
            if deleted_list.count() > 0:
                logger.info("Admin user " + admin_user + " delete commission level " + str(
                    deleted_list))
                deleted_commission_levels.delete()

        return HttpResponse(status=200)


class AgentDetailView(CommAdminView):

    def get(self, request, *args, **kwargs):
        get_type = request.GET.get("type")
        if get_type == 'search_affiliate_manager':
            text = request.GET['text']
            manager_id_list = CustomUser.objects.values('managed_by').distinct()
            manager_name_list = CustomUser.objects.filter(
                pk__in=manager_id_list).values('username')
            recontents = CustomUser.objects.filter(
                pk__in=manager_id_list).filter(username__startswith=text)
            rejson = []
            for recontent in recontents:
                rejson.append(recontent.username)
            return HttpResponse(json.dumps(rejson), content_type='application/json')

        else:
            context = super().get_context()
            affiliate = CustomUser.objects.get(pk=self.kwargs.get('pk'))
            title = "Affiliate " + affiliate.username

            downline = affiliate.referees.all()

            downline_deposit = deposit_tran.filter(user_id__in=downline).aggregate(
                total_deposit=Coalesce(Sum('amount'), 0))
            user_transaction = Transaction.objects.filter(user_id=affiliate)
            affiliate_commission_tran = user_transaction.filter(
                transaction_type=TRANSACTION_COMMISSION)

            context["title"] = title
            context["breadcrumbs"].append(
                {'url': '/cwyadmin/', 'title': title})
            context['time'] = timezone.now()
            # affiliate details
            context["affiliate"] = affiliate
            context["name"] = affiliate.username
            context["id"] = affiliate.id
            context["balance"] = affiliate.main_wallet
            context["affiliate_referee"] = downline
            context["affiliate_level"] = affiliate.affiliate_level
            context["affiliate_status"] = affiliate.affiliate_status
            context["transerfer_between_levels"] = affiliate.transerfer_between_levels

            # commission
            context["commission_this_month"] = affiliate_commission_tran.filter(request_time__gte=(
                today.replace(day=1))).aggregate(comm=Coalesce(Sum('amount'), 0))
            context["commission_last_month"] = affiliate_commission_tran.filter(
                Q(request_time__lte=(today.replace(day=1))) & Q(
                    request_time__gte=today.replace(day=1) + relativedelta(months=-1))).aggregate(
                comm=Coalesce(Sum('amount'), 0))
            context["commission_before_last"] = affiliate_commission_tran.filter(
                Q(request_time__lte=(today.replace(day=1) + relativedelta(months=-1))) & Q(
                    request_time__gte=today.replace(day=1) + relativedelta(months=-2))).aggregate(
                comm=Coalesce(Sum('amount'), 0))
            # downline status
            context["downline_number"] = getDownline(affiliate).count()
            context["active_users"] = calculateActiveDownlineNumber(affiliate)
            context["downline_deposit"] = downline_deposit
            try:
                context["promotion_link"] = ReferChannel.objects.get(
                    user_id=affiliate, refer_channel_name="default").pk
            except ObjectDoesNotExist:
                context["promotion_link"] = ""
            context["promotion_link_list"] = ReferChannel.objects.filter(
                user_id=affiliate)

            # related affiliates
            # get this affiliate's all ip addresses
            # filer other affiliate who have use these addresses before
            affiliate_ip_list = UserAction.objects.filter(
                user=affiliate.pk).values_list('ip_addr').distinct()
            related_affiliate_list = UserAction.objects.filter(
                ip_addr__in=affiliate_ip_list).values('user').exclude(user=affiliate.pk).distinct()

            related_affiliates_data = []
            for related_affiliate in related_affiliate_list:
                related_affiliates_info = {}
                related_affiliate = CustomUser.objects.get(pk=related_affiliate['user'])
                related_affiliates_info['member_id'] = related_affiliate.pk
                related_affiliates_info['balance'] = related_affiliate.main_wallet
                related_affiliates_data.append(related_affiliates_info)
            context["related_affiliates"] = related_affiliates_data

            # edit detail bottom
            try:
                context["commission_type"] = Commission.objects.filter(
                    user_id=affiliate).order_by('commission_level')
            except ObjectDoesNotExist:
                context["commission_type"] = ""

            manager = affiliate.managed_by
            if manager == None:
                context["manager"] = ""
            else:
                context["manager"] = manager

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
                downline_info['turnover'] = calculateTurnover(i, None, None)
                downline_info['balance'] = i.main_wallet
                downline_list_table.append(downline_info)
            context["downline_list"] = downline_list_table

            # CHANNEL REPORT TABLE
            channel_repost = []
            user_channel = ReferChannel.objects.filter(
                user_id=affiliate).values_list('pk').distinct()
            user_channel_list = ReferChannel.objects.filter(pk__in=user_channel)

            # Total commission
            context["total_commission"] = commission_tran.aggregate(
                total_commission=Coalesce(Sum('amount'), 0))['total_commission']

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
                affiliate.managed_by = manager
            except CustomUser.DoesNotExist:
                manager = affiliate.managed_by

            commission_list = []
            # update commission levels
            for i in level_details:
                if i['pk'] == '':
                    current_commission = Commission.objects.create(
                        user_id=affiliate,
                        commission_percentage=i['rate'],
                        downline_commission_percentage=i['downline_rate'],
                        commission_level=i['level'],
                        active_downline_needed=i['active_downline'],
                        monthly_downline_ftd_needed=i['downline_ftd']
                    )
                    current_commission.save()
                    commission_list.append(current_commission.pk)
                    logger.info("Create new commission level " +
                                i['level'] + " for affiliate " + affiliate.username)
                else:
                    current_commission = Commission.objects.filter(pk=i['pk'])
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
            deleted_commission_levels = Commission.objects.filter(user_id=affiliate).exclude(pk__in=commission_list)
            deleted_list = deleted_commission_levels.values_list('commission_level', flat=True)
            if deleted_list.count() > 0:
                logger.info("Admin user " + admin_user + " delete commission level " + str(
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
