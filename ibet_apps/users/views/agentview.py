from django.contrib.auth import get_user_model
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views import View
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import timedelta, localtime, now
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth, TruncYear, TruncDate, Coalesce
from django.contrib import messages
from django.shortcuts import render
from django.template.defaulttags import register
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.conf import settings
from dateutil.relativedelta import relativedelta
from django.shortcuts import render_to_response

from xadmin.views import CommAdminView
from utils.constants import *
from accounting.models import *
from users.models import CustomUser, UserAction, Commission, UserActivity, UserReferLink, ReferLink
from operation.models import Notification, NotificationToUsers


import logging
import simplejson as json
import datetime


logger = logging.getLogger('django')


class AgentView(CommAdminView):
    def get(self, request):
        get_type = request.GET.get("type")

        if get_type == "getCommissionHistory":
            date = request.GET.get("date")
            date = date+" "+MONTHLY_COMMISSION_SETTLE_DATE
            date = datetime.datetime.strptime(date, '%b %Y %d')
            tran_commission_this_month = Transaction.objects.filter(
                Q(transaction_type=TRANSACTION_COMMISSION) & Q(request_time__lte=date) & Q(request_time__gte=date-relativedelta(months=1)))
            # print(tran_commission_this_month)
            deposit_tran = Transaction.objects.filter(
                transaction_type=TRANSACTION_DEPOSIT)
            withdrawal_tran = Transaction.objects.filter(
                transaction_type=TRANSACTION_WITHDRAW)
            bonus_tran = Transaction.objects.filter(
                transaction_type=TRANSACTION_BONUS)
            commission_tran = Transaction.objects.filter(
                transaction_type=TRANSACTION_COMMISSION)
            response = {}
            commission_this_month_record = []

            for tran_commission in tran_commission_this_month:
                tranDict = {}
                user_id = tran_commission.user_id.pk
                tranDict['id'] = user_id
                tranDict['trans_pk'] = tran_commission.pk
                tranDict['active_players'] = calculateActiveUser(user_id)
                tranDict['downline_ftd'] = calculateFTD(
                    tran_commission.user_id.referees.all(), date-relativedelta(months=1), date)
                if tran_commission.user_id.commission_id in [None, '']:
                    tranDict['commission_rate'] = 0
                else:
                    tranDict['commission_rate'] = tran_commission.user_id.commission_id.commission_level

                tranDict['deposit'] = deposit_tran.filter(user_id=user_id).aggregate(
                    total_deposit=Coalesce(Sum('amount'), 0))['total_deposit']
                tranDict['withdrawal'] = withdrawal_tran.filter(user_id=user_id).aggregate(
                    total_withdrawal=Coalesce(Sum('amount'), 0))['total_withdrawal']
                tranDict['bonus'] = bonus_tran.filter(user_id=user_id).aggregate(
                    total_bonus=Coalesce(Sum('amount'), 0))['total_bonus']
                # query from bet history
                tranDict['winorloss'] = 0
                tranDict['commission'] = commission_tran.filter(Q(user_id=user_id) & Q(request_time__gte=date)).aggregate(
                    total_commission=Coalesce(Sum('amount'), 0))['total_commission']
                if tran_commission.status == TRAN_APPROVED_TYPE:
                    tranDict['status'] = "Released"
                else:
                    tranDict['status'] = "Pending"
                if tran_commission.arrive_time in [None, '']:
                    tranDict['release_time'] = ""
                else:
                    tranDict['release_time'] = str(tran_commission.arrive_time)
                tranDict['operator'] = ""

                commission_this_month_record.append(tranDict)
            return HttpResponse(json.dumps(commission_this_month_record), content_type='application/json')

        elif get_type == "getAffiliateApplicationDetail":
            user_id = request.GET.get("user_id")
            # print("review user " + user_id + " Affiliate Application")
            user_obj = CustomUser.objects.get(pk=user_id)
            user_detail = {}
            user_detail['id'] = user_id
            user_detail['username'] = user_obj.username
            user_detail['first_name'] = user_obj.first_name
            user_detail['last_name'] = user_obj.last_name
            user_detail['email'] = user_obj.email
            user_detail['phone'] = user_obj.phone
            user_detail['address'] = str(user_obj.street_address_1) + ', ' + str(user_obj.street_address_2) + ', ' + str(user_obj.city) + ', ' + str(user_obj.state) + ', ' + str(user_obj.zipcode) + ', ' + str(user_obj.country) 
            intro = user_obj.user_application_info
            if intro is None:
                user_detail["intro"] = ""
            else:
                user_detail["intro"] = intro            
            return HttpResponse(json.dumps(user_detail), content_type='application/json')

        else:
            context = super().get_context()
            context['time'] = timezone.now()
            title = "Affiliate overview"
            context["breadcrumbs"].append(
                {'url': '/affiliate_overview/', 'title': title})
            context["title"] = title

            # user-affiliate-group
            users = get_user_model().objects.all()
            affiliates = get_user_model().objects.exclude(user_to_affiliate_time=None)
            # print("affiliates" + str(affiliates))
            affiliate_has_referred = affiliates.filter(
                referred_by_id__isnull=False)

            # date
            today = localtime(now()).date()
            yesterday = today - timezone.timedelta(days=1)
            last_month = today.replace(day=1) + relativedelta(months=-1)
            before_last_month = today.replace(day=1) + relativedelta(months=-2)
            this_month = today.replace(day=1)

            downline_list = users.filter(referred_by_id__isnull=False)
            tran_for_active_user = Transaction.objects.filter(
                Q(transaction_type=TRANSACTION_DEPOSIT) & Q(transaction_type=TRANSACTION_WITHDRAW))

            # commission transaction
            tran_commission = Transaction.objects.filter(
                transaction_type=TRANSACTION_COMMISSION)
            tran_with_commission_this_month = tran_commission.filter(
                Q(request_time__gte=last_month) & Q(request_time__lte=this_month))
            tran_with_commission_this_month_before = tran_commission.filter(
                Q(request_time__gte=before_last_month) & Q(request_time__lte=last_month))
            tran_this_month = Transaction.objects.filter(
                request_time__gte=last_month)
            tran_with_commission_month_before = Transaction.objects.filter(
                request_time__gte=before_last_month)
            deposit_trans = Transaction.objects.filter(
                transaction_type=TRANSACTION_DEPOSIT)

            # Overview Part
            # affliate count
            context["affiliate"] = affiliates
            context["active_number"] = users.filter(
                affiliate_status='Active').count()
            context["deactivated_number"] = users.filter(
                affiliate_status='Deactivated').count()
            context["vip_number"] = users.filter(
                affiliate_status='VIP').count()
            context["negative_number"] = users.filter(
                affiliate_status='Negative').count()

            context["ftd_this_month"] = affiliates.filter(
                ftd_time__gte=last_month).count()
            context["actives_this_month"] = tran_for_active_user.filter(Q(request_time__gte=last_month) & Q(
                user_id__in=affiliates)).values_list('user_id').distinct().count()

            # company total win/loss
            # deposit - withdrawal - adjustment - commission (- bonus) ???
            tran_this_month_deposit_amount = tran_this_month.filter(transaction_type=TRANSACTION_DEPOSIT).aggregate(
                total_deposit=Coalesce(Sum('amount'), 0))['total_deposit']
            tran_this_month_withdrawal_amount = tran_this_month.filter(transaction_type=TRANSACTION_WITHDRAW).aggregate(
                total_withdrawal=Coalesce(Sum('amount'), 0))['total_withdrawal']
            tran_this_month_adjustment_amount = tran_this_month.filter(transaction_type=TRANSACTION_ADJUSTMENT).aggregate(
                total_adjustment=Coalesce(Sum('amount'), 0))['total_adjustment']
            tran_this_month_commission_amount = tran_this_month.filter(transaction_type=TRANSACTION_COMMISSION).aggregate(
                total_commission=Coalesce(Sum('amount'), 0))['total_commission']
            context["ggr_this_month"] = tran_this_month_deposit_amount - \
                (tran_this_month_withdrawal_amount +
                 tran_this_month_adjustment_amount + tran_this_month_commission_amount)

            context["affiliates_acquired_this_month"] = affiliates.filter(
                user_to_affiliate_time__gte=last_month).count()

            # context["new_ftd"] = affiliates.filter(ftd_time__range=[yesterday, today]).count()
            # context["most_new_player"] = affiliates_has_referred.values("referred_by_id").annotate(downline_number=Count("referred_by_id")).order_by("-referred_by_id")

            # active users
            # user who has transaction within this month ???

            # Affliates Table
            affiliates_table = []
            for affiliate in affiliates:
                affiliates_dict = {}
                affiliates_dict['id'] = affiliate.pk
                affiliates_dict['manager'] = ""
                if affiliate.managed_by is not None:
                    affiliates_dict['manager'] = affiliate.managed_by.username
                affiliate_active_users = 0
                # downline list
                downlines = affiliate.referees.all()
                downlines_deposit = 0
                for downline in downlines:
                    downlines_deposit += deposit_trans.filter(user_id=downline).aggregate(
                        total_deposit=Coalesce(Sum('amount'), 0))['total_deposit']
                    if tran_for_active_user.filter(user_id=downline).exists():
                        affiliate_active_users += 1
                affiliates_dict['active_users'] = affiliate_active_users
                affiliates_dict['downlines_deposit'] = downlines_deposit
                affiliates_dict['turnover'] = 0
                affiliates_dict['downlines_ggr'] = 0
                affiliates_dict['commission_last_month'] = tran_with_commission_this_month_before.filter(
                    user_id=affiliate).aggregate(total_commission=Coalesce(Sum('amount'), 0))['total_commission']
                affiliates_dict['commission_month_before'] = tran_with_commission_month_before.filter(
                    user_id=affiliate).aggregate(total_commission=Coalesce(Sum('amount'), 0))['total_commission']
                affiliates_dict['balance'] = affiliate.main_wallet + \
                    affiliate.other_game_wallet
                affiliates_dict['status'] = affiliate.affiliate_status
                affiliates_dict['level'] = affiliate.affiliate_level
                affiliates_table.append(affiliates_dict)
            context["affiliates_table"] = affiliates_table

            # Commission Table
            commision_transaction = tran_commission.annotate(commission_release_month=TruncMonth('request_time')).values(
                'commission_release_month').annotate(total_commission=Sum('amount')).order_by('-commission_release_month')

            commission = []

            for tran in commision_transaction:
                commission_dict = {}
                commission_dict['commission_release_month'] = tran['commission_release_month'] + \
                    relativedelta(months=1)
                commission_dict['total_commission'] = tran['total_commission']
                commission_dict['affiliate_number'] = affiliates.count()

                # affiliates.exclude(user_to_affiliate_time=None).filter(
                #     user_to_affiliate_time__lte=tran['commission_release_month']+relativedelta(months=1)).count()
                downline_user = CustomUser.objects.exclude(referred_by=None)
                commission_active_downline = Transaction.objects.filter(Q(request_time__gte=tran['commission_release_month']) & Q(user_id__in=downline_user) & Q(
                    request_time__lte=tran['commission_release_month']+relativedelta(months=1))).values('user_id').distinct()
                commission_dict['active_downline'] = commission_active_downline.count(
                )

                # commission status(tran_type=commission, user_id in affiliate, month=current month)
                commission_status = tran_this_month.filter(
                    Q(transaction_type=TRANSACTION_COMMISSION) & ~Q(status=TRAN_APPROVED_TYPE)).count()
                if commission_status == 0:
                    commission_dict['commission_status'] = "All released"
                else:
                    commission_dict['commission_status'] = str(
                        commission_status) + " Pending"
                commission.append(commission_dict)

            context["commision_transaction"] = commission

            # Premium Application Table
            # have not become agent, but alreay applied
            users_with_application_to_premium = users.filter(user_to_affiliate_time=None).exclude(
                user_application_time=None).order_by('-user_application_time')
            context["users_with_application_to_premium"] = users_with_application_to_premium
            return render(request, 'agent_list.html', context)

    def post(self, request):
        get_type = request.POST.get("type")

        if get_type == "releaseCommission":
            # transaction pk list need to be released
            commissionList = request.POST.getlist("list[]")
            # print(commissionList)
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
        elif get_type == "affiliateApplication":
            result = request.POST.get("result")
            remark = request.POST.get("remark")
            userID = request.POST.get("user_id")
            admin_user = request.POST.get("admin_user")
            user = CustomUser.objects.get(pk=userID)
            admin_user = CustomUser.objects.get(username=admin_user)
            # print(user)
            if result == "Yes":
                user.user_to_affiliate_time=timezone.now()
            else:
                user.user_application_time=None
            user.save()
            activity = UserActivity.objects.create(
                user = user,
                admin = admin_user,
                message = remark,
                activity_type = ACTIVITY_AFFILIATE_APPLICATION,
            )
            # print(activity)
            return HttpResponse(status=200)

class AgentDetailView(CommAdminView):

    def get(self, request, *args, **kwargs):
        context = super().get_context()
        # date
        today = localtime(now()).date()
        yesterday = today - timezone.timedelta(days=1)
        affiliate = CustomUser.objects.get(pk=self.kwargs.get('pk'))
    
        # print(affiliate)
        title = "Affiliate " + affiliate.username
        downline = affiliate.referees.all()
        # CustomUser.objects.all().filter(
        #     referred_by_id=affiliate.id).values_list('id')
        affiliates_list = CustomUser.objects.exclude(user_to_affiliate_time=None)
        active_downline = Transaction.objects.filter(Q(user_id__in=downline) & Q(
            request_time__gte=yesterday))
        downline_current_month_ftd_number = 0

        downline_deposit = Transaction.objects.filter(Q(user_id__in=downline) & Q(
            transaction_type=TRANSACTION_DEPOSIT)).aggregate(total_deposit=Coalesce(Sum('amount'), 0))
        user_transaction = Transaction.objects.filter(user_id=affiliate)
        commission_tran = user_transaction.filter(transaction_type=TRANSACTION_COMMISSION)
        current_affiliate_ip = UserAction.objects.filter(user=affiliate.pk).values('ip_addr')

        context["title"] = title
        context["breadcrumbs"].append({'url': '/cwyadmin/', 'title': title})
        context['time'] = timezone.now()
        # affiliate details
        context["affiliate"] = affiliate
        context["name"] = affiliate.username
        context["id"] = affiliate.id
        context["level"] = affiliate.affiliate_level
        context["status"] = affiliate.affiliate_status
        context["balance"] = affiliate.main_wallet
        # commission
        context["commission_this_month"] = commission_tran.filter(request_time__gte=(
            today.replace(day=1))).aggregate(comm=Coalesce(Sum('amount'), 0))
        context["commission_last_month"] = commission_tran.filter(Q(request_time__lte=(today.replace(day=1))) & Q(
            request_time__gte=today.replace(day=1)+relativedelta(months=-1))).aggregate(comm=Coalesce(Sum('amount'), 0))
        context["commission_before_last"] = commission_tran.filter(Q(request_time__lte=(today.replace(day=1)+relativedelta(months=-1))) & Q(
            request_time__gte=today.replace(day=1)+relativedelta(months=-2))).aggregate(comm=Coalesce(Sum('amount'), 0))
        # downline status
        context["downline_number"] = downline.aggregate(
            total_users=Count('id'))
        context["active_users"] = active_downline.values(
            'user_id').distinct().count()
        context["downline_deposit"] = downline_deposit
        context["promition_link"] = affiliate.referral_id

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
            related_affiliates_info['member_id'] = related_affiliate['user']
            related_affiliates_info['balance'] = related_affiliate.main_wallet
            related_affiliates_data.append(related_affiliates_info)
        context["related_affiliates"] = related_affiliates_data

        # print("related affiliates")
        
        context["affiliate_referee"] = affiliate.referees.all()
        # edit detail top
        context["affiliate_level"] = affiliate.affiliate_level
        # context["affiliate_status"] = affiliate.affiliate_status
        context["transerfer_between_levels"] = affiliate.transerfer_between_levels
        # edit detail bottom
        try:
            context["commission_type"] = Commission.objects.get(pk=affiliate.commission_id_id)
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
        # print(user_activities_list)


        # DOWNLINE LIST TABLE
        downline_list = []
        for i in affiliate.referees.all():
            downline_info = {}
            affiliate_tran = Transaction.objects.filter(user_id=i)
            # print(affiliate_tran)
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
                downline_info['ftd_time'] = i.ftd_time
            
            downline_info['channel'] = ""
            downline_info['deposit'] = affiliate_tran.filter(
                transaction_type=TRANSACTION_DEPOSIT).aggregate(sum_deposit=Coalesce(Sum('amount'), 0))
            downline_info['withdraw'] = affiliate_tran.filter(
                transaction_type=TRANSACTION_WITHDRAW).aggregate(sum_withdraw=Coalesce(Sum('amount'), 0))
            downline_info['bouns'] = affiliate_tran.filter(
                transaction_type=TRANSACTION_BONUS).aggregate(sum_bouns=Coalesce(Sum('amount'), 0))
            downline_info['adjustment'] = affiliate_tran.filter(
                transaction_type=TRANSACTION_ADJUSTMENT).aggregate(sum_adjustment=Coalesce(Sum('amount'), 0))
            downline_info['turnover'] = calculateTurnover(i)
            downline_info['balance'] = i.main_wallet
            downline_list.append(downline_info)
        context["downline_list"] = downline_list

        # CHANNEL REPORT TABLE
        channel_repost = []
        user_channel = UserReferLink.objects.filter(user=affiliate).values_list('link').distinct()
        user_channel_list = ReferLink.objects.filter(pk__in=user_channel)
        
        # Total commission
        total_commission = commission_tran.aggregate(total_commission=Coalesce(Sum('amount'), 0))['total_commission']
        # TRANSACTION GROUP BY MONTH
        # commission_monthly_record = user_transaction.annotate(y=TruncYear('arrive_time'),m=TruncMonth('arrive_time')).values('y')
        # for trans in commission_monthly_record:
        #     print(trans.request_time) 
        #     print(trans.amount) 
        #     print(trans.transaction_type) 

        
        # opeartion report
        # get current affiliate's transaction and sort by date


        # affiliate_tran_list = Transaction.objects.filter(user_id=affiliate.pk).annotate(
        #     operation_date=TruncDate('arrive_time')).order_by('-operation_date').values('operation_date').distinct()

        # opeartion_report = []
        # for tran in affiliate_tran_list:

        #     opeartion_info = {}
        #     cur_operation_data = Transaction.objects.filter(
        #         user_id=affiliate.pk).filter(arrive_time__lte=tran['operation_date'])
        #     opeartion_info['date'] = tran['operation_date']
        #     opeartion_info['cumulative_deposit'] = cur_operation_data.filter(
        #         transaction_type=0).aggregate(sum_deposit=Coalesce(Sum('amount'), 0))['sum_deposit']
        #     opeartion_info['cumulative_withdrawal'] = cur_operation_data.filter(
        #         transaction_type=1).aggregate(sum_withdrawal=Coalesce(Sum('amount'), 0))['sum_withdrawal']
        #     opeartion_info['system_bouns'] = cur_operation_data.filter(
        #         transaction_type=6).aggregate(sum_bouns=Coalesce(Sum('amount'), 0))['sum_bouns']
        #     # need calculate
        #     opeartion_info['downline_transfer'] = 0
        #     opeartion_info['turnover'] = 0
        #     opeartion_report.append(opeartion_info)
        # context["opeartion_report"] = opeartion_report
        # # get manager list and search for name
        # # global variable
        # manager_id_list = CustomUser.objects.values('managed_by').distinct()
        # manager_name_list = CustomUser.objects.filter(
        #     pk__in=manager_id_list).values('username')
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
            print(str(activity_type))
            if activity_type == 'All':
                activities = UserActivity.objects.filter(user=affiliate_id).order_by('-created_time')
            else:
                activities = UserActivity.objects.filter(Q(user=affiliate_id)&Q(activity_type=activity_type)).order_by('-created_time')
            print(activities)
            activities = serializers.serialize('json', activities)
            activities = json.loads(activities)
            response = []
            for act in activities:
                actDict = {}
                try:
                    time = datetime.datetime.strptime(act['fields']['created_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    time = datetime.datetime.strptime(act['fields']['created_time'], "%Y-%m-%dT%H:%M:%SZ")
                time = time.strftime("%B %d, %Y, %I:%M %p")
                actDict['time'] = time
                adminUser = CustomUser.objects.get(pk=act['fields']['admin'])
                actDict['adminUser'] = str(adminUser.username)
                actDict['message'] = act['fields']['message']
                response.append(actDict)
            print(str(response))

            return HttpResponse(json.dumps(response), content_type='application/json')
        
        elif post_type == 'update_message':
            message = request.POST.get('message')

            UserActivity.objects.create(
                user = CustomUser.objects.filter(pk=affiliate_id).first(),
                admin = CustomUser.objects.filter(username=admin_user).first(),
                message = message,
                activity_type = 3,
            )
            logger.info('Finished create activity to DB')
            return HttpResponse(status=200)

        elif post_type == 'make_adjustment':
            print(admin_user)
            print(affiliate_id)
            admin_user = CustomUser.objects.get(username=admin_user)
            affiliate_id = CustomUser.objects.get(pk=affiliate_id)
            remark = request.POST.get('remark')
            amount = request.POST.get('amount')
            send = request.POST.get('send')
            subject = request.POST.get('subject')
            text = request.POST.get('text')
            new_adjustment = Transaction.objects.create(
                user_id = affiliate_id,
                amount = amount,
                status = TRAN_SUCCESS_TYPE,
                transaction_type = TRANSACTION_ADJUSTMENT,
                remark = remark,
                release_by = admin_user,
            )
            new_adjustment.save()
            logger.info(admin_user.username + " creates a new adjustment for affiliate " + affiliate_id.username + " with the amount " + amount)
            if send == "true":
                # create a message
                new_notication = Notification.objects.create(
                    subject = subject,
                    content_text = text,
                    creator = admin_user,
                )
                new_notication.save()
                # send it to affilite
                new_log = NotificationToUsers.objects.create(
                    notification_id = new_notication.pk,
                    notifier_id = affiliate_id,
                )
                logger.info(admin_user.username + " send a message to affiliate " + affiliate_id.username + " with the subject " + subject)
            return HttpResponse(status=200)
        
        # elif post_type == 'send_message':
        #     admin_user = CustomUser.objects.get(username=admin_user)
        #     affiliate_id = CustomUser.objects.get(pk=affiliate_id)
        #     subject = request.POST.get('subject')
        #     text = request.POST.get('text')
        #     print(subject)
        #     print(text)
        #     return HttpResponse(status=200)






def fsearch(request):
    q = request.GET['q']
    manager_id_list = CustomUser.objects.values('managed_by').distinct()
    manager_name_list = CustomUser.objects.filter(
        pk__in=manager_id_list).values('username')
    recontents = CustomUser.objects.filter(
        pk__in=manager_id_list).filter(username__startswith=q)
    rejson = []
    for recontent in recontents:
        rejson.append(recontent.username)
    return HttpResponse(json.dumps(rejson), content_type='application/json')

def calculateActiveUser(affiliate_id):
    # check affiliate_id first
    downlines = CustomUser.objects.get(pk=affiliate_id).referees.all()
    affiliate_active_users = 0
    if downlines is None:
        return affiliate_active_users
    else:
        tran_for_active_user = Transaction.objects.filter(
            Q(transaction_type=TRANSACTION_DEPOSIT) & Q(transaction_type=TRANSACTION_WITHDRAW))
        for downline in downlines:
            if tran_for_active_user.filter(user_id=downline).exists():
                affiliate_active_users += 1
        return affiliate_active_users

def calculateFTD(user_group, start_date, end_date):
    # calculate this user_group's(downline list group or user group) within end_date ftd
    # user_group has to be objects group, end_date should be datetime format
    ftd = user_group.filter(Q(ftd_time__gte=start_date) & Q(ftd_time__lte=end_date)).count()
    return ftd

def calculateTurnover(user):
    return 0
# active_user_dict = {}
    # for user, affiliate in affiliates.values_list('id', 'referred_by'):
    #     if affiliate is None:
    #         continue
    #     elif (Transaction.objects.all().filter(Q(user_id=user) & Q(request_time__gte=last_month)).exists()):
    #         active_user_dict.update({affiliate: active_user_dict.get(affiliate, 0) + 1})
    # context["active_user_dict"] = active_user_dict

    # downline deposit
    # downline_deposit = {}
    # for user, affiliate, balance in affiliates.values_list('id', 'referred_by', 'main_wallet'):
    #     if affiliate is not None:
    #         downline_deposit.update(
    #             {affiliate: downline_deposit.get(affiliate, 0) + balance})
    # context["downline_deposit"] = downline_deposit

    # @register.filter(name='lookup')
    # def lookup(dict, index):
    #     if index in dict:
    #         return dict[index]
    #     return '0'

    # commission_last_month = {}
    # commission_month_before = {}
    # for affiliate_name, affiliate_id in affiliates.values_list('username', 'id'):
    #     try:
    #         cur = tran_with_commission_this_month.get(
    #             user_id_id=affiliate_id)
    #         commission_last_month.update({affiliate_name: cur.amount})
    #     except:
    #         commission_last_month.update({affiliate_name: '0'})

    # for affiliate_name, affiliate_id in affiliates.values_list('username', 'id'):
    #     try:
    #         last = tran_with_commission_this_month_before.get(
    #             user_id_id=affiliate_id)
    #         commission_month_before.update({affiliate_name: last.amount})
    #     except:
    #         commission_month_before.update({affiliate_name: '0'})

    # context["commission_last_month"] = commission_last_month
    # context["commission_month_before"] = commission_month_before

    # premium application
