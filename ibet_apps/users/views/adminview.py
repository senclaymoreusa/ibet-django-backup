from xadmin.views import CommAdminView
from django.core import serializers
from django.http import HttpResponse
from django.db.models import Sum, Q, F
from datetime import timedelta
from django.db import transaction
import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError
from django.conf import settings
from django.utils import timezone
from users.models import *
from accounting.models import Transaction
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
import simplejson as json
import datetime
from django.http import HttpResponseRedirect, HttpResponse
from users.views.helper import set_loss_limitation, set_deposit_limitation, set_temporary_timeout, set_permanent_timeout, get_old_limitations
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from system.models import UserToUserGroup
from django.views import View
from django.contrib.auth import update_session_auth_hash
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.urls import reverse
from django.utils import translation
from users.views.helper import *
from games.models import GameBet, Category, GameProvider
from utils.admin_helper import *
from operation.views import send_email
from games.helper import transferRequest
from utils.redisClient import RedisClient
from utils.redisHelper import RedisHelper
from operation.views import send_sms


import requests
import logging
import pytz
import random


logger = logging.getLogger('django')


class UserDetailView(CommAdminView):
    def get(self, request, *args, **kwargs):
        context = super().get_context()
        title = 'Member ' + self.kwargs.get('pk')
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context["title"] = title
        context['time'] = timezone.now()
        customUser = CustomUser.objects.get(pk=self.kwargs.get('pk'))
        context['customuser'] = customUser
        context['bonus_amount'] = getUserBonus(customUser) if getUserBonus(customUser) else 0
        context['can_withdraw_balance'] = customUser.main_wallet - customUser.bonus_wallet if  customUser.main_wallet - customUser.bonus_wallet > 0 else 0
        context['userPhotoId'] = self.download_user_photo_id(customUser.username)
        context['userLoginActions'] = UserAction.objects.filter(user=customUser, event_type=0).order_by('-created_time')[:20]
        context['trans_wallet'] = GameProvider.objects.filter(is_transfer_wallet=True)
        context['total_ngr'] = calculateNGR(customUser, None, None, None)
        context['total_ggr'] = calculateGGR(customUser, None, None, None)
        context['segment'] = customUser.vip_level.level if  customUser.vip_level else None
        context['member_status'] = customUser.get_member_status_display()
        transaction = Transaction.objects.filter(user_id=customUser)
        context['block'] = False
        temporaryBlockRes = {}
        permanentBlockRes = {}
        context['temperaryBlock'] = temporaryBlockRes
        context['permanentBlock'] = permanentBlockRes
        if checkUserBlock(customUser):
            act_obj = UserActivity.objects.filter(user=customUser, activity_type=ACTIVITY_CLOSE_ACCOUNT).order_by('-created_time').first()
            # blockLimitationDeatil = Limitation.objects.filter(user=customUser, limit_type=LIMIT_TYPE_BLOCK).order_by('-created_time').first()
            data = {
                'date': act_obj.created_time,
                'admin': act_obj.admin,
                'reason_options': act_obj.system_message,
                'reason': act_obj.message,
            }
            context['blockDetail'] = data
            context['block'] = True

        # elif checkUserBlock(customUser):
        #     expired_time = ""
        #     blocked_time = ""
        #     temporaryStr = ""
        #     temporaryCode = ""
        #     permanentStr = ""
        #     permanentCode = ""
        #     blocked_time = customUser.temporary_block_time or customUser.permanent_block_time
        #     if customUser.temporary_block_time:
        #         expired_time = customUser.temporary_block_time
        #         if customUser.temporary_block_interval == INTERVAL_PER_DAY:
        #             expired_time = expired_time + datetime.timedelta(days=1)
        #             temporaryStr = "one day"
        #             temporaryCode = customUser.temporary_block_interval
        #         elif customUser.temporary_block_interval == INTERVAL_PER_WEEK:
        #             expired_time = expired_time + datetime.timedelta(days=7)
        #             temporaryStr = "one week"
        #             temporaryCode = INTERVAL_PER_WEEK
        #         elif customUser.temporary_block_interval == INTERVAL_PER_MONTH:
        #             expired_time = expired_time + datetime.timedelta(days=30)
        #             temporaryStr = "one month"
        #             temporaryCode = INTERVAL_PER_MONTH
                
        #     elif customUser.permanent_block_time:
        #         expired_time = customUser.permanent_block_time
        #         if customUser.permanent_block_interval == INTERVAL_PER_SIX_MONTH:
        #             expired_time = expired_time + datetime.timedelta(6*365/12)
        #             permanentStr = "six months"
        #             permanentCode = INTERVAL_PER_SIX_MONTH
        #         elif customUser.permanent_block_interval == INTERVAL_PER_ONE_YEAR:
        #             expired_time = expired_time + datetime.timedelta(365)
        #             permanentStr = "one year"
        #             permanentCode = INTERVAL_PER_ONE_YEAR
        #         elif customUser.permanent_block_interval == INTERVAL_PER_THREE_YEAR:
        #             expired_time = expired_time + datetime.timedelta(365*3)
        #             permanentStr = "three years"
        #             permanentCode = INTERVAL_PER_THREE_YEAR
        #         elif customUser.permanent_block_interval == INTERVAL_PER_FIVE_YEAR:
        #             expired_time = expired_time + datetime.timedelta(365*5)
        #             permanentStr = "five years"
        #             permanentCode = INTERVAL_PER_FIVE_YEAR
                
        #     temporaryBlockRes = {
        #         'temporaryStr': temporaryStr,
        #         'temporaryCode': temporaryCode
        #     }

        #     permanentBlockRes = {
        #         'permanentStr': permanentStr,
        #         'permanentCode': permanentCode
        #     }

        #     data = {
        #         "expired_time": expired_time,
        #         "date": blocked_time,
        #         "admin": "User themselve"
        #     }
        #     context['blockDetail'] = data
        #     context['block'] = True
        #     context['temperaryBlock'] = temporaryBlockRes
        #     context['permanentBlock'] = permanentBlockRes

        #     temporaryBlockRes = {}
        # if customUser.temporary_block_interval is not None:
        #     temporaryBlock = customUser.temporary_block_interval
        #     # timeList = userJson[0]['fields']['temporary_block_timespan'].split(' ')
        #     # time = timeList[0]
        #     # temporaryBlock = int(time)
        #     if temporaryBlock == INTERVAL_PER_DAY:
        #         temporaryStr = "one day"
        #         temporaryCode = customUser.temporary_block_interval
        #     elif temporaryBlock == INTERVAL_PER_WEEK:
        #         temporaryStr = "one week"
        #         temporaryCode = INTERVAL_PER_WEEK
        #     elif temporaryBlock == INTERVAL_PER_MONTH:
        #         temporaryStr = "one month"
        #         temporaryCode = INTERVAL_PER_MONTH
        #     else:
        #         temporaryCode = ""
        #         temporaryStr = ""
            
        #     temporaryBlockRes = {
        #         'temporaryStr': temporaryStr,
        #         'temporaryCode': temporaryCode
        #     }
            
        
        #     permanentBlockRes = {}
        #     if customUser.permanent_block_interval is not None:
        #         permanentBlock = customUser.permanent_block_interval
        #         # timeList = userJson[0]['fields']['permanent_block_timespan'].split(' ')
        #         # time = timeList[0]
        #         # permanentBlock = int(time)
        #         if permanentBlock == INTERVAL_PER_SIX_MONTH:
        #             permanentStr = "six months"
        #             permanentCode = INTERVAL_PER_SIX_MONTH
        #         elif permanentBlock == INTERVAL_PER_ONE_YEAR:
        #             permanentStr = "one year"
        #             permanentCode = INTERVAL_PER_ONE_YEAR
        #         elif permanentBlock == INTERVAL_PER_THREE_YEAR:
        #             permanentStr = "three years"
        #             permanentCode = INTERVAL_PER_THREE_YEAR
        #         elif permanentBlock == INTERVAL_PER_FIVE_YEAR:
        #             permanentStr = "five years"
        #             permanentCode = INTERVAL_PER_FIVE_YEAR
        #         else:
        #             permanentStr = ""
        #             permanentCode = ""
                
                
            

        #     context['temperaryBlock'] = temporaryBlockRes
        #     # print("!!!! temperaryBlock: " + str(temporaryBlockRes))
        #     context['permanentBlock'] = permanentBlockRes
        #     # print(temporaryBlock, permanentBlock)


        total_balance = customUser.main_wallet
        each_wallet = UserWallet.objects.filter(user=customUser)
        for wallet in each_wallet:
            total_balance += wallet.wallet_amount
        context['totalBalance'] = total_balance


        riskLevelMap = {}
        for t in CustomUser._meta.get_field('risk_level').choices:
            riskLevelMap[t[0]] = t[1]

        context['riskLevel'] = riskLevelMap[int(customUser.risk_level)]

        statusMap = {}
        for t in Transaction._meta.get_field('status').choices:
            statusMap[t[0]] = t[1]

        transTypeMap = {}
        for t in Transaction._meta.get_field('transaction_type').choices:
            transTypeMap[t[0]] = t[1]
        
        productMap = {}
        for t in Transaction._meta.get_field('product').choices:
            productMap[t[0]] = t[1]

        currencyMap = {}
        for t in Transaction._meta.get_field('currency').choices:
            currencyMap[t[0]] = t[1]
        
        channelMap = {}
        for t in Transaction._meta.get_field('channel').choices:
            channelMap[t[0]] = t[1]

        # transaction
        transactions_list = Transaction.objects.filter(user_id=customUser)
        if transactions_list.count() == 0:
            context['userTransactions'] = ''
        else:
            transactions = transactions_list.order_by("-request_time")[:20]
            transactions = serializers.serialize('json', transactions)
            transactions = json.loads(transactions)
            trans = []
            for tran in transactions:
                try:
                    time = datetime.datetime.strptime(tran['fields']['request_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    time = datetime.datetime.strptime(tran['fields']['request_time'], "%Y-%m-%dT%H:%M:%SZ")
                time = time.strftime("%B %d, %Y, %I:%M %p")
                transDict = {
                    'transactionId': str(tran['fields']['transaction_id']),
                    'category': str(transTypeMap[tran['fields']['transaction_type']]),
                    'transType': transTypeMap[tran['fields']['transaction_type']],
                    'transTypeCode': tran['fields']['transaction_type'],
                    'product': productMap[tran['fields']['product']],
                    'fromWallet': str(tran['fields']['transfer_from']) if tran['fields']['transfer_from'] else "",
                    'toWallet': str(tran['fields']['transfer_to']) if tran['fields']['transfer_to'] else "",
                    'currency': currencyMap[tran['fields']['currency']],
                    'time': time,
                    'amount': tran['fields']['amount'],
                    'balance': tran['fields']['current_balance'],
                    'status': statusMap[tran['fields']['status']],
                    # 'bank': str(tran['fields']['bank']),
                    'bank': "",
                    'channel': channelMap[tran['fields']['channel']] if tran['fields']['channel'] else "",
                    'method': tran['fields']['method'] if tran['fields']['method'] else "",
                }
                # transDict = serializers.serialize('json')
                trans.append(transDict)
            context['userTransactions'] = trans
            
        # bet hisotry
        bet_history_list = GameBet.objects.filter(user=customUser)

        if bet_history_list.count() <= 20:
            context['betIsLastPage'] = True
        else:
            context['betIsLastPage'] = False

        if bet_history_list.count() == 0:
            context['userBetHistory'] = ''
        else:
            bet_history = bet_history_list.order_by("-bet_time")[:20]
            bet_history = serializers.serialize('json', bet_history)
            bet_history = json.loads(bet_history)

            bet_list = []

            for i in bet_history:
                try:
                    time = datetime.datetime.strptime(i['fields']['bet_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    time = datetime.datetime.strptime(i['fields']['bet_time'], "%Y-%m-%dT%H:%M:%SZ")
                time = time.strftime("%B %d, %Y, %I:%M %p")
                betDict = {
                    'pk': i['pk'],
                    'transactionId': str(i['fields']['transaction_id']),
                    'category': 'Bet',
                    # 'transType': transTypeMap[tran['fields']['transaction_type']],
                    # 'transTypeCode': tran['fields']['transaction_type'],
                    'product': str(Category.objects.get(pk=i['fields']['category']).name),
                    # 'fromWallet': str(tran['fields']['transfer_from']) if tran['fields']['transfer_from'] else "",
                    # 'toWallet': str(tran['fields']['transfer_to']) if tran['fields']['transfer_to'] else "",
                    'currency': currencyMap[i['fields']['currency']],
                    'time': time,
                    'amount_won': i['fields']['amount_won'] if i['fields']['amount_won'] else "",
                    'amount_wagered': i['fields']['amount_wagered'] ,
                    'status': 'Open' if not i['fields']['resolved_time'] else 'Close',
                    # 'bank': str(tran['fields']['bank']),
                    'bank': "",
                    # 'channel': channelMap[tran['fields']['channel']],
                    # 'method': tran['fields']['method'],
                }
                bet_list.append(betDict)
            context['userBetHistory'] = bet_list


        userLastLogin = UserAction.objects.filter(user=customUser, event_type=0).order_by('-created_time').first()
        login_json_obj = userLastLogin.ip_location if userLastLogin else ""
        # print(login_json_obj)
        context['userLoginObj'] = {
            'time': userLastLogin.created_time if userLastLogin else "None",
            'location': login_json_obj['region'] + ", " + login_json_obj['country'] if login_json_obj else "None",
            'ip_address': userLastLogin.ip_addr if userLastLogin else "None"
        }
        context['userLastIpAddr'] = userLastLogin
        context['loginCount'] = UserAction.objects.filter(user=customUser, event_type=0).count()
        context['activeTime'] = GameBet.objects.filter(user=customUser, amount_wagered__gte=0).count()
        create_account_ip =  UserAction.objects.filter(user=customUser, event_type=EVENT_CHOICES_REGISTER)
        # print(create_account_ip)
        context['create_account_ip'] = create_account_ip.order_by('-created_time').first().ip_addr if len(create_account_ip) > 0 else ""

        transaction = Transaction.objects.filter(user_id=customUser)
        if transaction.count() <= 20:
            context['isLastPage'] = True
        else:
            context['isLastPage'] = False

        deposit_trans = transactions_list.filter(transaction_type=0)
        withdraw_trans = transactions_list.filter(transaction_type=1)
        depositAmount = deposit_trans.aggregate(Sum('amount'))
        withdrawAmount = withdraw_trans.aggregate(Sum('amount'))
        depositCount = deposit_trans.count()
        withdrawCount = withdraw_trans.count()
        bonusAmount = transactions_list.filter(transaction_type=6).aggregate(Sum('amount'))

        if bonusAmount['amount__sum'] is None:
            bonusAmount['amount__sum'] = 0
        if withdrawAmount['amount__sum'] is None:
            withdrawAmount['amount__sum'] = 0
        if depositAmount['amount__sum'] is None:
            depositAmount['amount__sum'] = 0

        if depositAmount['amount__sum'] == 0:
            withdrawRate = 0
            bonusRate = 0
        else:
            withdrawRate = withdrawAmount['amount__sum']/depositAmount['amount__sum']
            bonusRate = bonusAmount['amount__sum']/depositAmount['amount__sum']
        
        context['withdrawDepositRate'] = "%.2f" % withdrawRate
        context['bonusDepositRate'] = "%.2f" % bonusRate
        context['depositCount'] = depositCount
        context['withdrawCount'] = withdrawCount
        context['depositAmount'] = depositAmount['amount__sum']
        context['withdrawAmount'] = withdrawAmount['amount__sum']
        
        if userLastLogin is None:
            context['relativeAccount'] = ''
        else:
            context['relativeAccount'] = self.account_by_ip(userLastLogin.ip_addr, userLastLogin.user)
        # print(str(context['relativeAccount']))

        deposits = deposit_trans.order_by('-request_time').first()
        if deposits:
            deposits = serializers.serialize('json', [deposits])
            deposits = json.loads(deposits)
            lastDeposit = []
            for deposit in deposits:
                try:
                    time = datetime.datetime.strptime(deposit['fields']['request_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    time = datetime.datetime.strptime(deposit['fields']['request_time'], "%Y-%m-%dT%H:%M:%SZ")
                time = time.strftime("%B %d, %Y, %H:%M")
                depositDict = {
                    'transactionId': str(deposit['pk']),
                    'category': str(transTypeMap[deposit['fields']['transaction_type']]),
                    'transType': transTypeMap[deposit['fields']['transaction_type']],
                    'transTypeCode': deposit['fields']['transaction_type'],
                    'product': productMap[deposit['fields']['product']],
                    'toWhichWallet': str(deposit['fields']['transfer_to']),
                    'currency': currencyMap[deposit['fields']['currency']],
                    'time': time,
                    'amount': deposit['fields']['amount'],
                    'status': statusMap[deposit['fields']['status']],
                    # 'bank': str(deposit['fields']['bank']),
                    'bank': "",
                    'channel': channelMap[deposit['fields']['channel']] if deposit['fields']['channel'] else "",
                    'method': deposit['fields']['method'],
                }
                lastDeposit.append(depositDict)
            context['lastDeposits'] = lastDeposit[:1][0]
        else:
            context['lastDeposits'] = {
                'time': "",
                'amount': "",
                'status': "",
            }

        withdraws = withdraw_trans.order_by('-request_time').first() 
        if withdraws:
            withdraws = serializers.serialize('json', [withdraws])
            withdraws = json.loads(withdraws)
            lastWithdraw = []
            for withdraw in withdraws:
                try:
                    time = datetime.datetime.strptime(withdraw['fields']['request_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    time = datetime.datetime.strptime(withdraw['fields']['request_time'], "%Y-%m-%dT%H:%M:%SZ")
                time = time.strftime("%B %d, %Y, %I:%M %p")
                withdrawDict = {
                    'transactionId': str(withdraw['pk']),
                    'category': withdraw['fields']['transaction_type'],
                    'transType': transTypeMap[withdraw['fields']['transaction_type']],
                    'transTypeCode': withdraw['fields']['transaction_type'],
                    'product': productMap[withdraw['fields']['product']],
                    'toWhichWallet': str(withdraw['fields']['transfer_to']),
                    'currency': currencyMap[withdraw['fields']['currency']],
                    'time': time,
                    'amount': withdraw['fields']['amount'],
                    'status': statusMap[withdraw['fields']['status']],
                    # 'bank': str(withdraw['fields']['bank']),
                    'bank': "",
                    'channel': channelMap[withdraw['fields']['channel']] if withdraw['fields']['channel'] else "",
                    'method': withdraw['fields']['method'],
                }
                lastWithdraw.append(withdrawDict)
            context['lastWithdraws'] = lastWithdraw[0]
        else:
            context['lastWithdraws'] = {
                'time': "",
                'amount': "",
                'status': "",
            }


        activity = UserActivity.objects.filter(user=customUser, activity_type__in=[0,1,2,3]).order_by("-created_time")
        if activity:
            context['activity'] = activity
        else:
            context['activity'] = ''

        limitations = Limitation.objects.filter(user=customUser)

        productMap = {}
        for t in Limitation._meta.get_field('product').choices:
            productMap[t[0]] = t[1]

        intervalMap = {}
        for t in Limitation._meta.get_field('interval').choices:
            intervalMap[t[0]] = t[1]

        limitationDict = {
            'bet': [],
            'loss': [],
            'deposit': [],
            'withdraw': [],
        }
        productAccessArr = []
        for limitation in limitations:
            if limitation.limit_type == LIMIT_TYPE_BET:
                betLimit = {
                    'amount': limitation.amount,
                    'productValue': limitation.product,
                    'product':  productMap[limitation.product]
                }
                limitationDict['bet'].append(betLimit)
            elif limitation.limit_type == LIMIT_TYPE_LOSS:
                lossMap = {
                    'amount': limitation.amount,
                    'intervalValue': limitation.interval,
                    'interval': intervalMap[limitation.interval]
                }
                limitationDict['loss'].append(lossMap)
                # limitationDict['loss'] = lossMap
            elif limitation.limit_type == LIMIT_TYPE_DEPOSIT:
                depositMap = {
                    'amount': limitation.amount,
                    'intervalValue': limitation.interval,
                    'interval': intervalMap[limitation.interval]
                }
                limitationDict['deposit'].append(depositMap)
                # limitationDict['deposit'] = depositMap
            elif limitation.limit_type == LIMIT_TYPE_WITHDRAW:
                withdrawMap = {
                    'amount': limitation.amount,
                    'intervalValue': limitation.interval,
                    'interval': intervalMap[limitation.interval]
                }
                limitationDict['withdraw'].append(withdrawMap)
                # limitationDict['withdraw'] = withdrawMap
            elif limitation.limit_type == LIMIT_TYPE_ACCESS_DENY:
                value = limitation.product
                productAccessMap = {
                    'productValue': value,
                    'product':  productMap[value]
                }
                productAccessArr.append(productAccessMap)


        # print(limitationDict)
        context['limitation'] = limitationDict
        context['productAccess'] = json.dumps(productAccessArr)
        context['accessDenyObj'] = productAccessArr
        context['segment_level'] = Segmentation.objects.all()
        context['related_user_data'] = getRelatedDevice(customUser.username)

        log_obj = UserActivity.objects.filter(user=customUser, activity_type=ACTIVITY_UPLOAD_IMAGE).order_by('-created_time')
        if len(log_obj) > 0:
            log_obj = log_obj[0]
            context['user_image_log_obj'] = log_obj


        # userJson = serializers.serialize('json', [customUser])
        # userJson = json.loads(userJson)
        
        return render(request, 'user_detail.html', context)


    def post(self, request):
        post_type = request.POST.get('type')
        user_id = request.POST.get('user_id')

        try:
            if post_type == 'edit_user_detail':
                username = request.POST.get('username')
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                email = request.POST.get('email')
                phone = request.POST.get('phone')
                date_of_birth = request.POST.get('date_of_birth')
                address = request.POST.get('street_address_1')
                city = request.POST.get('city')
                zipcode = request.POST.get('zipcode')
                country = request.POST.get('country')
                user_id_img = request.POST.get('user_id_img')
                reason_text = request.POST.get('reason_text')
                update_fields = request.POST.get('update_fields')
                update_fields = json.loads(update_fields)

                user = CustomUser.objects.get(pk=user_id)
                before_status = user.member_status
                after_status = ""

                if len(update_fields) <= 0:
                    response = {
                        "status": True,
                        "message": 'Nothing change for user: ' + str(username) + 'info'
                    }
                    return HttpResponse(json.dumps(response), content_type='application/json')

                query = {}
                system_message = ""
                first_image_upload = False
                status_change = False
                for i in update_fields:
                    if i['name'] == 'reason_text':
                        continue
                    elif i['name'] == 'user_id_img':
                        continue
                    elif i['name'] == 'user_id_img_first' and i['value'] == "true":
                        first_image_upload = True
                        # print(first_image_upload)
                        continue
                    if i['name'] == 'member_status':
                        status_change = True
                        after_status = int(i['value'])
                        query[i['name']] = i['value']
                        system_message += i['name'] + " change to " + str(dict(MEMBER_STATUS).get(after_status))
                    else:
                        query[i['name']] = i['value']
                        system_message += i['name'] + " change to " + i['value']

                    
                with transaction.atomic():
                # # upload image to S3
                    if user_id_img and first_image_upload:
                        self.upload_user_photo_id(username, user_id_img)
                        UserActivity.objects.create(
                            user = user,
                            admin = request.user,
                            system_message = "Upload user ID image",
                            message = reason_text,
                            activity_type = ACTIVITY_UPLOAD_IMAGE,
                        )
                    elif not user_id_img and not first_image_upload:
                        UserActivity.objects.create(
                            user = user,
                            admin = request.user,
                            system_message = "Delete user ID image",
                            message = reason_text,
                            activity_type = ACTIVITY_REMOVE_IMAGE,
                        )
                        self.remove_user_photo_id(username)

                    if status_change:
                        UserActivity.objects.create(
                            user = user,
                            admin = request.user,
                            system_message = "Status change from " + str(dict(MEMBER_STATUS).get(before_status)) + " to " + str(dict(MEMBER_STATUS).get(after_status)),
                            message = reason_text,
                            activity_type = ACTIVITY_STATUS_CHANGED,
                        )

                    UserActivity.objects.create(
                        user = user,
                        admin = request.user,
                        system_message = system_message.replace("_", " ") if system_message else None,
                        message = reason_text,
                        activity_type = ACTIVITY_SYSTEM,
                    )
                    CustomUser.objects.filter(pk=user_id).update(**query)
                logger.info('Finished update user: ' + str(username) + 'info to DB')
                # print(CustomUser.objects.get(pk=user_id).id_image)
                response = {
                    "status": True,
                    "message": 'Finished update user: ' + str(username) + 'info to DB'
                }
                return HttpResponse(json.dumps(response), content_type='application/json')
        
            elif post_type == 'update_message':
                admin_user = request.POST.get('admin_user')
                message = request.POST.get('message')

                UserActivity.objects.create(
                    user = CustomUser.objects.get(pk=user_id),
                    admin = request.user,
                    message = message,
                    activity_type = 3,
                )

                logger.info('Finished create activity to DB')
                return HttpResponseRedirect(reverse('xadmin:user_detail', args=[user_id]))

            elif post_type == 'activity_filter':
                activity_type = request.POST.get('activity_type')

                user = CustomUser.objects.get(pk=user_id)
                # print(str(activity_type))
                
                if activity_type == '-1':
                    activities = UserActivity.objects.filter(user=user, activity_type_in=[0,1,2,3]).order_by('-created_time')
                else:
                    activities = UserActivity.objects.filter(user=user, activity_type=activity_type).order_by('-created_time')

                response = []
                for act in activities:
                    data = {
                        'created_time': act.created_time.strftime("%B %d, %Y, %I:%M %p"),
                        'adminUser': act.admin.username,
                        'activity_type': act.activity_type,
                        'message': act.message if act.message else "",
                        'system_message': act.system_message if act.system_message else "",
                    }
                    response.append(data)

                return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json')

            elif post_type == 'limitation_setting':
                
                loss_limitation = request.POST.getlist('loss_limit')
                loss_limitation = [item for item in loss_limitation if len(item) > 0]
                # print("loss_limitation type: " + str(type(loss_limitation)))
                # print("origin loss_limitation: " + str(loss_limitation))
                loss_interval = request.POST.getlist('loss_limit_interval')
                # print("origin loss_interval: " + str(loss_interval))
                # loss_interval = list(map(lambda x : int(x) if x >= 0, loss_interval))
                loss_interval = [item for item in loss_interval if int(item) >= 0]
                deposit_limitation = request.POST.getlist('deposit_limit')
                # deposit_limitation = [float(item) for item in deposit_limitation if float(item) >= 0]
                deposit_interval = request.POST.getlist('deposit_limit_interval')
                # deposit_interval = list(map(lambda x : int(x), deposit_interval))
                deposit_interval = [int(item) for item in deposit_interval if int(item) >= 0]
                withdraw_limitation = request.POST.getlist('withdraw_limit')
                # print("withdraw_limitation type: " + str(withdraw_limitation))
                # deposit_limitation = [float(item) for item in withdraw_limitation if float(item) >= 0]
                withdraw_interval = request.POST.getlist('withdraw_limit_interval')
                withdraw_interval = [int(item) for item in withdraw_interval if int(item) >= 0]

                reason = request.POST.get('reasonTextarea')

                temporary_time = request.POST.get('temporary_time')
                permanent_time = request.POST.get('permanent_time')
                # print(temporary_time, permanent_time)
                # print("reason type: " + str(reason))
                # print(str(reason))

                access_deny_tags = request.POST.get('access_deny_tags')
                if access_deny_tags:
                    access_deny_tags = json.loads(access_deny_tags)
                # print(str(access_deny_tags))
                user = CustomUser.objects.get(pk=user_id)
                oldLimitMap = get_old_limitations(user_id)

                # oldLimitMap = {
                #     LIMIT_TYPE_BET: {},
                #     LIMIT_TYPE_LOSS: {},
                #     LIMIT_TYPE_DEPOSIT: {},
                #     LIMIT_TYPE_WITHDRAW: {},
                #     LIMIT_TYPE_ACCESS_DENY: {}
                # }

                # limitations = Limitation.objects.filter(user=user)
                # for limit in limitations:
                #     limitType = limit.limit_type
                #     if limitType == LIMIT_TYPE_ACCESS_DENY:
                #         oldLimitMap[limitType][limit.product] = limit.amount
                #     else:
                #         # oldLimitMap[limitType]['amount'] = limit.amount
                #         oldLimitMap[limitType][limit.interval] = limit.amount
                if int(temporary_time) >= 0:
                    set_temporary_timeout(user_id, temporary_time)
                if int(permanent_time) >= 0:
                    set_permanent_timeout(user_id, permanent_time)
                # print("oldLimitMap: " + str(oldLimitMap))
                # if bet_limitation:

                #     # delete
                #     for productType in oldLimitMap[LIMIT_TYPE_BET]:
                #         if productType not in bet_product:
                #             logger.info('Deleting bet limit for product type' + str(productType))
                #             Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_BET, product=productType).delete()

                #     # insert or update
                #     for i in range(len(bet_limitation)):
                #         if Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_BET, product=bet_product[i]).exists():
                #             logger.info('Update bet limit for product type for' + str(user))
                #             Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_BET, product=bet_product[i]).update(amount=bet_limitation[i])
                #         else:
                #             logger.info('Create new bet limit for product type for' + str(user))
                #             limitation = Limitation(
                #                 user= user,
                #                 limit_type=0,
                #                 amount=bet_limitation[i],
                #                 product=bet_product[i],
                #             )
                #             limitation.save()

                if access_deny_tags:
                    for productType in oldLimitMap[LIMIT_TYPE_ACCESS_DENY]:
                        if productType not in access_deny_tags:
                            logger.info('Deleting access deny limit for product type ' + str(productType))
                            Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_ACCESS_DENY, product=productType).delete()

                    for i in range(len(access_deny_tags)):
                        if Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_ACCESS_DENY, product=access_deny_tags[i]).exists():
                            pass
                        else:
                            logger.info('Create new access deny for product type for' + str(user))
                            limitation = Limitation(
                                user= user,
                                limit_type=LIMIT_TYPE_ACCESS_DENY,
                                amount=0,
                                product=access_deny_tags[i],
                            )
                            limitation.save()
                else:
                    Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_ACCESS_DENY).delete()
                    
                
                # set_loss_deposit_limitation(user_id, loss_limitation, loss_interval, deposit_limitation, deposit_interval, oldLimitMap)
                if loss_limitation:
                    set_loss_limitation(user_id, loss_limitation, loss_interval, oldLimitMap, user)
                else:
                    Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_LOSS).update(amount=None)

                if deposit_limitation:
                    set_deposit_limitation(user_id, deposit_limitation, deposit_interval, oldLimitMap, user)
                else:
                    Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_DEPOSIT).update(amount=None)

                if withdraw_interval:
                    # delete
                    for intervalType in oldLimitMap[LIMIT_TYPE_WITHDRAW]:
                        if intervalType not in withdraw_interval:
                            logger.info('Deleting loss limit for interval type: ' + str(intervalType))
                            Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_WITHDRAW, interval=intervalType).delete()

                    # insert or update
                    for i in range(len(withdraw_limitation)):
                        if Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_WITHDRAW, interval=withdraw_interval[i]).exists():
                            logger.info('Update loss limit for interval type: ' + str(user))
                            Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_WITHDRAW, interval=withdraw_interval[i]).update(amount=withdraw_limitation[i])
                        else:
                            logger.info('Create new bet limit for product type for' + str(user))
                            limitation = Limitation(
                                user= user,
                                limit_type=LIMIT_TYPE_WITHDRAW,
                                amount=withdraw_limitation[i],
                                interval=withdraw_interval[i],
                            )
                            limitation.save()
                else:
                    Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_WITHDRAW).delete()

                return HttpResponseRedirect(reverse('xadmin:user_detail', args=[user_id]))

            elif post_type == 'block_user':
                action = request.POST.get('action')
                admin_user = request.user
                user_id = request.POST.get('user_id')
                block_time = request.POST.get('block_time')
                reason_option = request.POST.get('reason_option')
                reason = request.POST.get('reason')

                # print(action, admin_user, user_id, block_time, reason_option, reason)
                # block vicky 30 None None 0
                # set_temporary_timeout(user, lock_timespan)
                user = CustomUser.objects.get(pk=user_id)
                sys_message = dict(CLOSE_REASON).get(int(reason_option)) if reason_option else ""
                # print(sys_message)
                if action == 'block':

                    if user.is_admin == True:
                        message = _("Cannot block the admin user")
                        logger.info("Cannot block the admin user")
                        error = {
                            'errorCode': '1001',
                            'message': str(message)
                        }
                        # print(json.dumps(error))
                        return HttpResponse(json.dumps(error), content_type="application/json")
                    
                    if block_time != '-1':
                        with transaction.atomic():
                            if int(block_time) >= 0 and int(block_time) <= 2:
                                set_temporary_timeout(user, block_time)
                            else:
                                set_permanent_timeout(user, block_time)
                            user.member_status = MEMBER_STATUS_CLOSED
                            UserActivity.objects.create(
                                user = user,
                                admin = request.user,
                                system_message = sys_message,
                                message = reason,
                                activity_type = ACTIVITY_CLOSE_ACCOUNT,
                            )
                            # user.temporary_block_time = datetime.datetime.now()
                            user.save()
                            # limitation = Limitation.objects.create(user=user, limit_type=LIMIT_TYPE_BLOCK, admin=admin_user)
                            logger.info("Block user: " + str(user.username) + " by admin user: " + str(admin_user))
                    else:
                        with transaction.atomic():
                            user.block = True
                            user.member_status = MEMBER_STATUS_CLOSED
                            UserActivity.objects.create(
                                user = user,
                                admin = request.user,
                                system_message = sys_message,
                                message = reason,
                                activity_type = ACTIVITY_CLOSE_ACCOUNT,
                            )

                            UserActivity.objects.create(
                                user = user,
                                admin = request.user,
                                system_message = sys_message,
                                message = reason,
                                activity_type = ACTIVITY_STATUS_CHANGED,
                            )

                            UserActivity.objects.create(
                                user = user,
                                admin = request.user,
                                system_message = sys_message,
                                message = reason,
                                activity_type = ACTIVITY_SYSTEM,
                            )
                            # user.temporary_block_time = datetime.datetime.now()
                            user.save()
                            # limitation = Limitation.objects.create(user=user, limit_type=LIMIT_TYPE_BLOCK, admin=admin_user)
                            logger.info("Block user: " + str(user.username) + " by admin user: " + str(admin_user))
                    return HttpResponse(json.dumps({"message": "finished block"}), content_type="application/json")
                else:
                    with transaction.atomic():
                        # user = CustomUser.objects.filter(pk=user_id).update(block=False, temporary_block_time=None)
                        user.temporary_block_time = None
                        user.block = False
                        user.member_status = MEMBER_STATUS_NORMAL
                        user.save()

                        UserActivity.objects.create(
                            user = user,
                            admin = request.user,
                            system_message = "Open account",
                            message = reason,
                            activity_type = ACTIVITY_OPEN_ACCOUNT,
                        )

                        UserActivity.objects.create(
                            user = user,
                            admin = request.user,
                            system_message = sys_message,
                            message = reason,
                            activity_type = ACTIVITY_STATUS_CHANGED,
                        )

                        UserActivity.objects.create(
                            user = user,
                            admin = request.user,
                            system_message = "Open account",
                            message = reason,
                            activity_type = ACTIVITY_SYSTEM,
                        )

                        # limitation = Limitation.objects.create(user=user, limit_type=LIMIT_TYPE_UNBLOCK, admin=admin_user)
                        logger.info("Unblock user: " + str(user.username) + " by admin user: " + str(admin_user))
                    return HttpResponse(json.dumps({"message": "finished open"}), content_type="application/json")
                # return HttpResponseRedirect(reverse('xadmin:user_detail', args=[user.pk]))
        except Exception as e:
            logger.error("User Detail View Error -- {}".format(repr(e)))
            return HttpResponseRedirect(reverse('xadmin:user_detail', args=[user.pk]))
    
    def account_by_ip(self, userIp, username):
        relative_account = UserAction.objects.filter(ip_addr=userIp, event_type=0).exclude(user=username).values('user_id').distinct()
        # print(relative_account)

        accounts = []
        for item in relative_account:
            userDict = {}
            # user = CustomUser.objects.get(username=i.user)
            user = CustomUser.objects.get(pk=item['user_id'])
            userDict['id'] = user.pk
            userDict['username'] = user.username
            userDict['source'] = user.get_user_attribute_display
            userDict['channel'] = user.get_user_attribute_display
            depositSucc = Transaction.objects.filter(user_id=user, transaction_type=0, status=3).count()
            depositCount = Transaction.objects.filter(user_id=user, transaction_type=0).count()
            userDict['deposit'] = str(depositSucc) + '/' + str(depositCount)
            userDict['turnover'] = ''
            withdrawAmount = Transaction.objects.filter(user_id=user, transaction_type=1).aggregate(Sum('amount'))
            if withdrawAmount['amount__sum'] is None:
                withdrawAmount['amount__sum'] = 0
            userDict['withdrawal'] = withdrawAmount['amount__sum']
            userDict['contribution'] = ''
            userDict['riskLevel'] = 'A'
            accounts.append(userDict)
        return accounts

    
    def remove_user_photo_id(self, username):
        # print(username)
        aws_session = boto3.Session()
        s3_client = aws_session.client('s3')
        file_name = self.get_user_photo_file_name(username)
        s3_client.delete_object(Bucket=settings.AWS_S3_ADMIN_BUCKET, Key=file_name)

        logger.info('Finished remove username: ' + username + ' and file: ' + file_name + ' from S3!!!')


    def download_user_photo_id(self, username):
        aws_session = boto3.Session()
        s3_client = aws_session.client('s3')
        file_name = self.get_user_photo_file_name(username)

        success = False
        try:
            s3_response_object = s3_client.get_object(Bucket=settings.AWS_S3_ADMIN_BUCKET, Key=file_name)
            success = True
        except ClientError as e:
            # AllAccessDisabled error == bucket or object not found
            logger.error(e)
        except NoCredentialsError as e:
            logger.error(e)
        if not success:
            logger.info('Cannout find any image from this user: ' + username)
            return None

        object_content = s3_response_object['Body'].read()
        object_content = object_content.decode('utf-8')

        logger.info('Finished download username: ' + username + ' and file: ' + file_name + ' to S3!!!')
        return object_content


    def upload_user_photo_id(self, username, content):
        aws_session = boto3.Session()
        s3 = aws_session.resource('s3')
        file_name = self.get_user_photo_file_name(username)

        success = False
        try:
            obj = s3.Object(settings.AWS_S3_ADMIN_BUCKET, file_name)
            obj.put(Body=content)
            success = True
            logger.info('Finished upload username: ' + username + 'and file: ' + file_name + ' to S3!!!')
        except NoCredentialsError as e:
            logger.error(e)
        if not success:
            logger.info('Cannout upload image: ' + username)
            return None


    def get_user_photo_file_name(self, username):
        return username + '_photo_id'       


class UserListView(CommAdminView): 
    def get(self, request):

        # print(request.GET)
        search = request.GET.get('search')
        pageSize = request.GET.get('pageSize')
        offset = request.GET.get('offset')
        status = request.GET.get('status')

        # print("search: " + str(search))

        if pageSize is None:
            pageSize = 20
        else: 
            pageSize = int(pageSize)

        if offset is None:
            offset = 0
        else:
            offset = int(offset)
    
        context = super().get_context()
        title = 'Member List'
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context['title'] = title
        context['time'] = timezone.now()
        context['status'] = dict(MEMBER_STATUS)

        user_filter = Q()

        if status and status != '-1':
            user_filter &= Q(member_status=status)
        
        if search:
            user_filter &= (Q(pk__contains=search)|Q(username__icontains=search)|Q(email__icontains=search)|Q(phone__contains=search)|Q(first_name__icontains=search)|Q(last_name__icontains=search))

        customUser = CustomUser.objects.filter(user_filter).order_by('username')
        count = customUser.count()

        customUser = customUser[offset:offset+pageSize]

        if offset == 0:
            context['isFirstPage'] = True
        else:
            context['isFirstPage'] = False
        
        if count <= offset+pageSize:
            context['isLastPage'] = True
        else:
            context['isLastPage'] = False

        user_data = []
        for user in customUser:
            userDict = {}
            userDict['id'] = user.pk
            userDict['username'] = user.username
            userDict['source'] = str(user.get_user_attribute_display())
            userDict['manager'] = str(user.vip_managed_by.username) if user.vip_managed_by else ""
            userDict['risk_level'] = user.get_risk_level_display()
            userDict['balance'] = user.main_wallet + user.other_game_wallet
            userDict['product_attribute'] = ''
            userDict['time_of_registration'] = user.time_of_registration
            userDict['ftd_time'] = user.ftd_time
            userDict['ftd_time_amount'] = user.ftd_time_amount if user.ftd_time_amount != 0 else ""
            userDict['verification_time'] = user.verification_time
            userDict['id_location'] = user.id_location
            userDict['phone'] = user.phone
            userDict['address'] = user.get_user_address()
            deposit_sum = 0
            turnover_sum = 0
            bonus_sum = 0
            userDict['deposit_turnover'] = ''
            userDict['bonus_turnover'] = ''
            userDict['contribution'] = '{:.2f}'.format(calculateContribution(user))
            # depositTimes = Transaction.objects.filter(user_id=user, transaction_type=0).count()
            # withdrawTimes = Transaction.objects.filter(user_id=user, transaction_type=1).count()
            betTims = GameBet.objects.filter(user=user, amount_wagered__gte=0).count()
            activeDays = int(betTims)
            userDict['active_days'] = activeDays
            userDict['member_status'] = user.get_member_status_display() if user.get_member_status_display() else ""
            status_change_obj = UserActivity.objects.filter(user=user, activity_type=ACTIVITY_STATUS_CHANGED).order_by('created_time').first()
            close_obj = UserActivity.objects.filter(user=user, activity_type=ACTIVITY_CLOSE_ACCOUNT).order_by('created_time').first()
            userDict['status_changed'] = status_change_obj.created_time if status_change_obj else ""
            # userDict['status_changed'] = user.member_changed_time if user.member_changed_time else ""
            userDict['changed_by'] = status_change_obj.admin if status_change_obj else ""
            userDict['closure_reason'] = close_obj.system_message if close_obj and user.member_status == MEMBER_STATUS_CLOSED else ""


            userDict['last_login_time'] = user.last_login_time
            userDict['last_betting_time'] = user.last_betting_time
            userDict['login'] = UserAction.objects.filter(user=user, event_type=0).count()
            userDict['betting'] = Transaction.objects.filter(user_id=user, transaction_type=2).count()
            userDict['turnover'] = ''
            userDict['deposit'] = Transaction.objects.filter(user_id=user, transaction_type=0).count()
            userDict['deposit_amount'] = Transaction.objects.filter(user_id=user, transaction_type=0).aggregate(Sum('amount'))
            userDict['withdrawal'] = Transaction.objects.filter(user_id=user, transaction_type=1).count()
            userDict['withdrawal_amount'] = Transaction.objects.filter(user_id=user, transaction_type=1).aggregate(Sum('amount'))
            userDict['last_login_ip'] = UserAction.objects.filter(user=user, event_type=0).order_by('-created_time').first()

            if user.is_admin:
                userDict['is_admin'] = 'Yes'
            else:
                userDict['is_admin'] = 'No'
            # print("object: " + str(userDict))
            user_data.append(userDict)
        
        context['user_data'] = user_data

        return render(request, 'user_list.html', context)

    
    def post(self, request):
        post_type = request.POST.get('type')
        # user_id = request.POST.get('user_id')

        if post_type == 'user_list_time_range_filter':
            time_from = request.POST.get('from')
            time_to = request.POST.get('to')
            # print("from: " + str(time_from) + 'to: ' + str(time_to))
            Customuser = CustomUser.objects.all()
            # context['customuser'] = Customuser
            
            updated_data = []
            for user in Customuser:
                userDict = {}
                userDict['login_times'] = UserAction.objects.filter(user=user, event_type=0, created_time__range=[time_from, time_to]).count()
                userDict['betting_times'] = Transaction.objects.filter(user_id=user, transaction_type=2, request_time__range=[time_from, time_to]).count()
                userDict['deposit_times'] = Transaction.objects.filter(user_id=user, transaction_type=0, request_time__range=[time_from, time_to]).count()
                userDict['deposit_amount'] = Transaction.objects.filter(user_id=user, transaction_type=0, request_time__range=[time_from, time_to]).aggregate(Sum('amount'))
                userDict['withdrawal_times'] = Transaction.objects.filter(user_id=user, transaction_type=1, request_time__range=[time_from, time_to]).count()
                userDict['withdrawal_amount'] = Transaction.objects.filter(user_id=user, transaction_type=1, request_time__range=[time_from, time_to]).aggregate(Sum('amount'))
                # add GGR amount, turnover amount, contribution
                updated_data.append(userDict)
                # print(userDict)
            
            # print("sending data")
            return HttpResponse(json.dumps(updated_data), content_type="application/json")

        elif post_type == 'user_list_filter':
            time_from = request.POST.get('from')
            time_to = request.POST.get('to')
            pageSize = int(request.POST.get('pageSize'))
            fromItem = int(request.POST.get('fromItem'))
            endItem = fromItem + pageSize

            if time_from == 'Invalid date':
                time_from = datetime.datetime(2000, 1, 1)
            if time_to == 'Invalid date':
                time_to = datetime.datetime(2400, 1, 1)

            # print('fromItem: ' + str(fromItem))
            # print('endItem: ' + str(endItem))
            users = CustomUser.objects.all()[fromItem:endItem]
            count = CustomUser.objects.all().count()
            # print(str(count))
            # usersJson = serializers.serialize('json', users)

            # usersList = json.loads(usersJson)            
            response = {}
            if endItem >= count:
                response['isLastPage'] = True
            else:
                response['isLastPage'] = False

            if fromItem == 0:
                response['isFirstPage'] = True
            else:
                response['isFirstPage'] = False
            
            sourceMap = {}
            for t in CustomUser._meta.get_field('user_attribute').choices:
                sourceMap[t[0]] = t[1]

            usersList = []
            for user in users:
                userDict = {}
                userDict['id'] = user.pk
                userDict['username'] = user.username
                userDict['source'] = str(sourceMap[user.user_attribute])
                userDict['balance'] = user.main_wallet + user.other_game_wallet
                userDict['product_attribute'] = ''
                userDict['time_of_registration'] = str(user.time_of_registration)
                userDict['ftd_time'] = str(user.ftd_time)
                userDict['verification_time'] = str(user.verification_time)
                userDict['id_location'] = user.id_location
                userDict['phone'] = user.phone
                userDict['address'] = str(user.street_address_1) + ', ' + str(user.street_address_2) + ', ' + str(user.city) + ', ' + str(user.state) + ', ' + str(user.country) 
                userDict['deposit_turnover'] = ''
                userDict['bonus_turnover'] = ''
                userDict['contribution'] = 0
                depositTimes = Transaction.objects.filter(user_id=user, transaction_type=0).count()
                # print(type(depositTimes))
                withdrawTimes = Transaction.objects.filter(user_id=user, transaction_type=1).count()
                betTimes = Transaction.objects.filter(user_id=user, transaction_type=2).count()
                activeDays = int(depositTimes) + int(withdrawTimes) + int(betTimes)
                userDict['active_days'] = ''
                userDict['bet_platform'] = user.product_attribute

                # print("object: " + str(userDict))
                usersList.append(userDict)
            response['usersList'] = usersList
            # response = json.loads(response)
            return HttpResponse(json.dumps(response), content_type="application/json")   


class UserProfileView(CommAdminView):

    def get(self, request, *args, **kwargs):
        context = super().get_context()
        title = 'User Profile'
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context['title'] = title
        context['time'] = timezone.now()

        user = request.user
        user = CustomUser.objects.get(username=user)

        languageCode = 'en'
        if LANGUAGE_SESSION_KEY in request.session:
            # print(request.session[LANGUAGE_SESSION_KEY])
            languageCode = request.session[LANGUAGE_SESSION_KEY]
        
        logger.info("System language is : {}".format(languageCode))

        response = {
            'userId': user.pk,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'title': user.title,
            'location': user.country,
            'birthday': '',
            'email': user.email,
            'phone': user.phone,
            'language': languageCode,
            'username': user.username,
            'department': '',
            'role': '',
            'ibetMarkets': '',
            'letouMarkets': ''
        }

        imagePath = PUBLIC_S3_BUCKET + 'admin_images/'

        ibetMarketList = []
        if user.ibetMarkets:
            countryCodes = user.ibetMarkets.split(',')
            for countryCode in countryCodes:
                ibetMarketList.append({
                    'code': countryCode,
                    'name': COUNTRY_CODE_TO_IMG_PREFIX[countryCode],
                    'url': imagePath + COUNTRY_CODE_TO_IMG_PREFIX[countryCode] + '.png'
                })

        letouMarketList = []
        if user.letouMarkets:
            countryCodes = user.letouMarkets.split(',')
            for countryCode in countryCodes:
                letouMarketList.append({
                    'code': countryCode,
                    'name': COUNTRY_CODE_TO_IMG_PREFIX[countryCode],
                    'url': imagePath + COUNTRY_CODE_TO_IMG_PREFIX[countryCode] + '.png'
                })

        if user.department:
            role = UserToUserGroup.objects.get(user=user)
            response.update(role=role.group.name)
            department = ''
            for i in DEPARTMENT_LIST:
                if int(i['code']) == int(user.department):
                    department = i['name']

            response.update(department=department)

        if user.date_of_birth:
            dobList = user.date_of_birth.split('/')
            month = dobList[0]
            day = dobList[1]
            year = dobList[2]
            birthday = year + '-' + month + '-' + day
            response.update(ibetMarkets=ibetMarketList, letouMarkets=letouMarketList, birthday=birthday)

        context['userProfile'] = response

        return render(request, 'user_profile.html', context)
    

    def post(self, request):
        post_type = request.POST.get('type')
        userId = request.POST.get('userId')

        if post_type == 'changePassword':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            repeat_new_password = request.POST.get('repeat_new_password')

            logger.info("Change password request by: {}".format(userId))

            if new_password != repeat_new_password:
                logger.error("The passwords do not match")
                return JsonResponse({ "code": 1, "message": "The passwords do not match"})

            user = CustomUser.objects.get(pk=userId)
            
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                logger.info("Your password has been successfully changed.")
                return JsonResponse({ "code": 0, "message": "Your password has been successfully changed."}, status=200)
            else:
                logger.error("Old password is incorrect")
                return JsonResponse({ "code": 1, "message": "Old password is incorrect"})
        
        elif post_type == 'changeProfile':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            title = request.POST.get('title')
            location = request.POST.get('location')
            birthday = request.POST.get('birthday')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            language = request.POST.get('system_language')
            # print(first_name, last_name, title, location, birthday, email, phone, language)

            user = CustomUser.objects.get(pk=userId)
            user.first_name = first_name
            user.last_name = last_name
            user.title = title
            user.country = location
            user.email = email
            user.phone = phone

            if birthday:
                birthdayList = birthday.split('-')
                year = birthdayList[0]
                month = birthdayList[1]
                day = birthdayList[2]
                if len(year) > 4 :
                    logger.error("User profile birthday info is not correct")
                    return JsonResponse({ "code": 1, "message": "Birthday info is not correct"})
            
                date_of_birth = month + '/' + day + '/' + year
                user.date_of_birth = date_of_birth
                logger.info("Updating user date_of_birth field: {}".format(date_of_birth))
            
            logger.info("Updating user info: {0}, {1}, {2}, {3}, {4}, {5}".format(first_name, last_name, title, location, email, phone))
            user.save()
            
            response = JsonResponse({ "code": 0, "message": "User information has been successfully updated."}, status=200)
            
            if language:
                request.session[LANGUAGE_SESSION_KEY] = language
                request.session.modified = True
                translation.activate(language)

                session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
                if session_key is None:
                    request.session.create()
                    response.set_cookie(key=settings.SESSION_COOKIE_NAME, value=request.session._session_key)
                
                logger.info("Setting system language : {}".format(language))

            logger.info("Finished update admin user profile")
            return response



class GetUserInfo(View):

    def get(self, request, *args, **kwargs):

        try:
            user_id = request.GET.get('user_id', '')
            user = CustomUser.objects.get(pk=user_id)
            name =  user.first_name + " " + user.last_name if user.first_name else user.last_name
            response = {
                'userId': user.pk,
                'username': user.username,
                'name': name,
                'idNumber': '',
                'birthday': user.date_of_birth,
                'status': user.member_status,
                'playerSegment': user.vip_level.level if user.vip_level else '',
                'riskLevel': user.risk_level,
                'manager': user.vip_managed_by.username if user.vip_managed_by else '',
                'email': user.email,
                'phone': user.phone,
                'address': user.street_address_1 + ( " " + user.street_address_2 if user.street_address_2 else ""),
                'city': user.city,
                'zipcode': user.zipcode,
                'country': user.country,
                'idApplicationTime': user.verification_time if user.verification_time else "",
                'idReviewTime': user.verification_time if  user.verification_time else "",
                'idReviewer': '',
            }
            return HttpResponse(json.dumps(response), content_type="application/json")
        except Exception as e:
            response = {}
            return HttpResponse(response, content_type="application/json", status=404)



class GetUserTransaction(View):

    def get(self, request, *args, **kwargs):
        try:
            trans_type = request.GET.get('type')
            user_id = request.GET.get('user_id')
            time_from = request.GET.get('from')
            time_to = request.GET.get('to')
            pageSize = int(request.GET.get('pageSize'))
            fromItem = int(request.GET.get('fromItem'))
            endItem = fromItem + pageSize
            category = request.GET.get('category')
            product = request.GET.get('product')
            

            if trans_type == "transaction":
                # print(user_id, time_from, time_to, pageSize, fromItem, endItem, category, product)

                transaction_filter = Q(user_id__pk=user_id)

                current_tz = timezone.get_current_timezone()
                tz = pytz.timezone(str(current_tz))

                if time_from:
                    time_from = datetime.datetime.strptime(time_from, '%m/%d/%Y')
                    aware = time_from.replace(tzinfo=tz)
                    time_from = aware.astimezone(pytz.UTC)
                    min_time_from = tz.localize(datetime.datetime.combine(time_from, datetime.time.min))
                    transaction_filter &= Q(request_time__gte=min_time_from)

                if time_to:
                    time_to= datetime.datetime.strptime(time_to, '%m/%d/%Y')
                    # max_time_to = tz.localize(datetime.datetime.combine(time_to, datetime.time.max))  
                    aware = time_to.replace(tzinfo=tz)
                    time_to = aware.astimezone(pytz.UTC)
                    max_time_to = tz.localize(datetime.datetime.combine(time_to, datetime.time.max))
                    transaction_filter &= Q(request_time__lte=max_time_to)

                # logger.info('Transactions filter: username "' + str(user.username) + '" send transactions filter request which time form: ' + str(time_from) + ',to: ' + str(time_to) + ',category: ' + str(category))
                # logger.info('Pagination: Maximum size of the page is ' + str(pageSize) + 'and from item #' + str(fromItem) + ' to item # ' + str(endItem))
                
                if category and category != 'all':
                    transaction_filter &= Q(transaction_type=category)

                if product and product != 'all':
                    transaction_filter &= Q(product=product)
                

                all_transactions = Transaction.objects.filter(transaction_filter).order_by('-request_time')
                response = {}
                if endItem >= all_transactions.count():
                    response['isLastPage'] = True
                else:
                    response['isLastPage'] = False

                if fromItem == 0:
                    response['isFirstPage'] = True
                else:
                    response['isFirstPage'] = False


                all_transactions = all_transactions[fromItem: endItem]
                transactions_json = serializers.serialize('json', all_transactions)
                transactions_list = json.loads(transactions_json)

                # for tran in transactions_list:
                #     tran['fields']['status'] = statusMap[tran['fields']['status']]
                #     tran['fields']['currency'] = currencyMap[tran['fields']['currency']]
                #     try:
                #         time = datetime.datetime.strptime(tran['fields']['request_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                #     except:
                #         time = datetime.datetime.strptime(tran['fields']['request_time'], "%Y-%m-%dT%H:%M:%SZ")
                #     time = time.strftime("%B %d, %Y, %I:%M %p")
                #     tran['fields']['time'] = time
                

                trans = []
                for tran in transactions_list:
                    try:
                        time = datetime.datetime.strptime(tran['fields']['request_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    except:
                        time = datetime.datetime.strptime(tran['fields']['request_time'], "%Y-%m-%dT%H:%M:%SZ")
                    time = time.strftime("%B %d, %Y, %I:%M %p")
                    transDict = {
                        'transactionId': str(tran['fields']['transaction_id']),
                        'category': str(dict(TRANSACTION_TYPE_CHOICES).get(tran['fields']['transaction_type'])),
                        'transTypeCode': tran['fields']['transaction_type'],
                        'product': str(dict(GAME_TYPE_CHOICES).get(tran['fields']['product'])),
                        'fromWallet': str(tran['fields']['transfer_from']) if tran['fields']['transfer_from'] else "",
                        'toWallet': str(tran['fields']['transfer_to']) if tran['fields']['transfer_to'] else "",
                        'currency': str(dict(CURRENCY_CHOICES).get(tran['fields']['currency'])),
                        'time': time,
                        'amount': tran['fields']['amount'],
                        'balance': tran['fields']['current_balance'],
                        'status': str(dict(STATE_CHOICES).get(tran['fields']['status'])),
                        
                        # 'bank': str(tran['fields']['bank']),
                        'bank': "",
                        'channel':  str(dict(CHANNEL_CHOICES).get(tran['fields']['channel'])),
                        'method': tran['fields']['method'],
                    }
                    # transDict = serializers.serialize('json')
                    trans.append(transDict)

                    
                response['transactions'] = trans
                # transactionsJson = json.dumps(transactionsList)
                
                return HttpResponse(json.dumps(response), content_type='application/json')
            else:
                response = {}

                bet_filter = Q(user__pk=user_id)

                current_tz = timezone.get_current_timezone()
                tz = pytz.timezone(str(current_tz))

                if time_from:
                    time_from = datetime.datetime.strptime(time_from, '%m/%d/%Y')
                    aware = time_from.replace(tzinfo=tz)
                    time_from = aware.astimezone(pytz.UTC)
                    min_time_from = tz.localize(datetime.datetime.combine(time_from, datetime.time.min))
                    bet_filter &= Q(bet_time__gte=min_time_from)

                if time_to:
                    time_to= datetime.datetime.strptime(time_to, '%m/%d/%Y')
                    # max_time_to = tz.localize(datetime.datetime.combine(time_to, datetime.time.max))  
                    aware = time_to.replace(tzinfo=tz)
                    time_to = aware.astimezone(pytz.UTC)
                    max_time_to = tz.localize(datetime.datetime.combine(time_to, datetime.time.max))
                    bet_filter &= Q(bet_time__lte=max_time_to)

                # logger.info('Transactions filter: username "' + str(user.username) + '" send transactions filter request which time form: ' + str(time_from) + ',to: ' + str(time_to) + ',category: ' + str(category))
                # logger.info('Pagination: Maximum size of the page is ' + str(pageSize) + 'and from item #' + str(fromItem) + ' to item # ' + str(endItem))

                if product and product != 'all':
                    bet_filter &= Q(category__name=product)

                all_bet_objs = GameBet.objects.filter(bet_filter).order_by('-bet_time')
                response = {}
                if endItem >= all_bet_objs.count():
                    response['isLastPage'] = True
                else:
                    response['isLastPage'] = False

                if fromItem == 0:
                    response['isFirstPage'] = True
                else:
                    response['isFirstPage'] = False


                all_bet_objs = all_bet_objs[fromItem: endItem]
                # transactions_json = serializers.serialize('json', all_transactions)
                # transactions_list = json.loads(transactions_json)

                bet_list = []
                for bet in all_bet_objs:
                    betDict = {
                        'pk': bet.pk,
                        'transactionId': bet.transaction_id,
                        'category': 'Bet',
                        'product': str(bet.category),
                        'currency': bet.get_currency_display(),
                        'bet_time':  bet.bet_time.strftime("%B %d, %Y, %I:%M %p") if bet.bet_time else "",
                        'resolved_time': bet.resolved_time.strftime("%B %d, %Y, %I:%M %p") if bet.resolved_time else "",
                        'amount_won': bet.amount_won if bet.amount_won else "0.0000",
                        'amount_wagered': bet.amount_wagered if bet.amount_wagered else "0.0000",
                        'status': 'Open' if not bet.resolved_time else 'Close',
                    }
                    # transDict = serializers.serialize('json')
                    bet_list.append(betDict)

                response['transactions'] = bet_list

                return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json')


        except Exception as e:
            logger.error("Admin getting user transaction error: ", e)
            return HttpResponse(status=404)



class GetBetHistoryDetail(View):

    def get(self, request, *args, **kwargs):
        try:
            bet_id = request.GET.get('bet_id')

            bet_obj = GameBet.objects.get(pk=bet_id)

            # try:
            #     bet_time = datetime.datetime.strptime(bet_obj.bet_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            # except:
            #     bet_time = datetime.datetime.strptime(bet_obj.bet_time, "%Y-%m-%dT%H:%M:%SZ")
            if bet_obj.bet_time:
                bet_time = bet_obj.bet_time.strftime("%B %d, %Y, %I:%M %p")
            else:
                bet_time = ''

            # try:
            #     resolved_time = datetime.datetime.strptime(bet_obj.resolved_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            # except:
            #     resolved_time = datetime.datetime.strptime(bet_obj.resolved_time, "%Y-%m-%dT%H:%M:%SZ")
            if bet_obj.resolved_time:
                resolved_time = bet_obj.resolved_time.strftime("%B %d, %Y, %I:%M %p")
            else:
                resolved_time = ''

            response = {
                'bet_id': bet_obj.transaction_id,
                'amount_won': bet_obj.amount_won,
                'amount_wagered': bet_obj.amount_wagered,
                'bet_time': bet_time,
                'resolved_time': resolved_time,
                'outcome': bet_obj.get_outcome_display() if bet_obj.get_outcome_display() else "None",
                'user': bet_obj.user.username,
                'status': "Close" if bet_obj.resolved_time else "Open"
            }

            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json')

        except Exception as e:
            logger.error("Admin getting user bet deatil: ", e)
            return HttpResponse(status=404)



class UserAdjustment(View):

    def post(self, request, *args, **kwargs): 

        data = json.loads(request.body)

        
        user_id = data['user_id']
        user = CustomUser.objects.get(pk=user_id)
        try:
            reason = data['adjustment_reason'] if 'adjustment_reason' in data else ""
            amount = data['amount'] if 'amount' in data else 0
            wagering_amount = data['wagering_amount'] if 'wagering_amount' in data else 0
            debit_or_credit = data['debit_or_credit'] if 'debit_or_credit' in data else ""
            notify_player = data['notify_player'] if 'notify_player' in data else False
            affiliate = data['affiliate'] if 'affiliate' in data else False
            message_subject = data['message_subject'] if 'message_subject' in data else ""
            message_to_player = data['message_to_player'] if 'message_to_player' in data else ""
            message_note = data['message_note'] if 'message_note' in data else ""


            # print(reason, amount, debit_or_credit, notify_player, affiliate, message_subject, message_to_player, message_note)
            
            admin_user = self.request.user
            if debit_or_credit == 'credit':
                balance = user.main_wallet + decimal.Decimal(amount)
                with transaction.atomic():
                    ref_no = user.username+"-"+timezone.datetime.today().isoformat()+"-"+str(random.randint(0, 10000000))
                    obj, created = Transaction.objects.get_or_create(
                                user_id=user,
                                transaction_id=ref_no,
                                amount=decimal.Decimal(amount),
                                method="Admin adjustment (credit)",
                                currency=user.currency,
                                transaction_type=TRANSACTION_ADJUSTMENT,
                                current_balance = balance,
                                status=TRAN_SUCCESS_TYPE,
                                remark=message_note,
                                other_data={
                                    "wagering_amount": str(decimal.Decimal(wagering_amount) * decimal.Decimal(amount))
                                }
                            )
                    user.bonus_wallet += decimal.Decimal(amount)
                    user.main_wallet += decimal.Decimal(amount)
                    user.save()

                    UserActivity.objects.create(
                        user=user,
                        admin=admin_user,
                        message=message_note,
                        activity_type=ACTIVITY_REMARK,
                    )
            elif debit_or_credit == 'debit':
                balance = user.main_wallet - decimal.Decimal(amount)
                with transaction.atomic():
                    ref_no = user.username+"-"+timezone.datetime.today().isoformat()+"-"+str(random.randint(0, 10000000))
                    obj, created = Transaction.objects.get_or_create(
                                user_id=user,
                                transaction_id=ref_no,
                                amount=decimal.Decimal(amount),
                                method="Admin adjustment (debit)",
                                currency=user.currency,
                                transaction_type=TRANSACTION_ADJUSTMENT,
                                current_balance = balance,
                                status=TRAN_SUCCESS_TYPE,
                                remark=message_note,
                            )
                    user.main_wallet -= decimal.Decimal(amount)
                    user.save()

                    UserActivity.objects.create(
                        user=user,
                        admin=admin_user,
                        message=message_note,
                        activity_type=ACTIVITY_REMARK,
                    )


            if notify_player:
                send_email(message_subject, message_to_player, user.username)
            

            response = {}
            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json')
        except Exception as e:
            logger.error("Make adjustment error for user {}: {}".format(user.username, str(e)))
            return HttpResponse(status=400)


class UserTransfer(View):

    def post(self, request, *args, **kwargs): 

        data = json.loads(request.body)
        user_id = data['user_id']
        customUser = CustomUser.objects.get(pk=user_id)
        # print(data)
        try:
            
            admin_user = self.request.user
            transfer_to = data['transfer_to'] if 'transfer_to' in data else ""
            transfer_from = data['transfer_from'] if 'transfer_from' in data else ""
            transfer_amount = data['transfer_amount'] if 'transfer_amount' in data else 0
            notify_player = data['notify_player'] if 'notify_player' in data else False
            message_subject = data['message_subject'] if 'message_subject' in data else ""
            message_to_player = data['message_to_player'] if 'message_to_player' in data else ""
            message_note = data['message_note'] if 'message_note' in data else ""
            
            with transaction.atomic():
                transferRequest(customUser, transfer_amount, transfer_from, transfer_to)

                UserActivity.objects.create(
                    user=customUser,
                    admin=admin_user,
                    message=message_note,
                    activity_type=ACTIVITY_REMARK,
                )

            if notify_player:
                send_email(message_subject, message_to_player, customUser.username)
            
            response = {}
            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json')
        except Exception as e:
            logger.error("Make transfer error for user {}: {}".format(customUser.username, str(e)))
            return HttpResponse(status=400)



class ProductContribution(View):

    def get(self, request, *args, **kwargs):

        user_id = request.GET.get('user_id')
        customUser = CustomUser.objects.get(pk=user_id)
        # print(user_id, customUser)
        
        try:
            sport_query = Q(user_name=customUser.username) & (Q(category__name="Sports") | Q(category__parent_id__name="Sports"))
            sport_contribution = GameBet.objects.filter(sport_query).aggregate(total=Sum(F('amount_wagered')-F('amount_won')))['total']
            # print(sport_contribution)

            game_query = Q(user_name=customUser.username) & (Q(category__name="Games") | Q(category__parent_id__name="Games"))
            games_contribution = GameBet.objects.filter(game_query).aggregate(total=Sum(F('amount_wagered')-F('amount_won')))['total']
            # print(games_contribution)

            live_casino_query = Q(user_name=customUser.username) & (Q(category__name="Live Casino") | Q(category__parent_id__name="Live Casino"))
            live_casino_contribution = GameBet.objects.filter(live_casino_query).aggregate(total=Sum(F('amount_wagered')-F('amount_won')))['total']
            # print(live_casino_contribution)

            lottery_query = Q(user_name=customUser.username) & (Q(category__name="Lotteries") | Q(category__parent_id__name="Lotteries"))
            lottery_contribution = GameBet.objects.filter(lottery_query).aggregate(total=Sum(F('amount_wagered')-F('amount_won')))['total']
            # print(lottery_contribution)
            
            
            totalAmount = 0
            if sport_contribution is not None:
                totalAmount += sport_contribution
            if games_contribution is not None:
                totalAmount += games_contribution
            if live_casino_contribution is not None:
                totalAmount += live_casino_contribution
            if lottery_contribution is not None:
                totalAmount += lottery_contribution

            response = {
                'sport_value': "%.2f" % sport_contribution if sport_contribution else 0,
                'sport_percent': (round(100 * (sport_contribution / totalAmount))) if sport_contribution and sport_contribution > 0 else 0,
                'games': "%.2f" % games_contribution if games_contribution else 0,
                'games_percent': (round(100 * (games_contribution / totalAmount))) if games_contribution and games_contribution > 0 else 0,
                'live_casino': "%.2f" % live_casino_contribution if live_casino_contribution else 0,
                'live_casino_percent': (round(100 * (live_casino_contribution / totalAmount))) if live_casino_contribution and live_casino_contribution > 0 else 0,
                'lottery': "%.2f" % lottery_contribution if lottery_contribution else 0,
                'lottery_percent': (round(100 * (lottery_contribution / totalAmount))) if lottery_contribution and lottery_contribution > 0 else 0,
            }
            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json')
        except Exception as e:
            logger.error("Make transfer error for user {}: {}".format(customUser.username, str(e)))
            return HttpResponse(status=400)






def getRelatedDevice(user):
    r = RedisClient().connect()
    redis = RedisHelper()
    device = redis.get_devices_by_user(user)
    related_user_use_same_device = []
    related_user_data = []
    if device:
        related_user_use_same_device += redis.get_users_by_device(device.pop().decode('utf-8'))
    while related_user_use_same_device:
        username = related_user_use_same_device.pop().decode('utf-8')
        if username == user:
            continue
        related_user = CustomUser.objects.get(username=username)

        if related_user.is_admin:
            continue
        
        related_user_info = {
            'user_id': related_user.pk,
            'username': related_user.username,
            'member_status': related_user.get_member_status_display(),
            'risk_level': related_user.get_risk_level_display(),
            'balance': related_user.main_wallet
        }
        related_user_data.append(related_user_info)

    return related_user_data




class BlackListUser(View):

    def post(self, request, *args, **kwargs):

        data = json.loads(request.body)
        try:
            user_list = data['user_list']
            reason = data['reason']
            admin = request.user

            with transaction.atomic():
                for user in user_list:
                    blacklist_user = CustomUser.objects.get(pk=user)
                    blacklist_user.block = True
                    blacklist_user.member_status = MEMBER_STATUS_BLACKLISTED
                    blacklist_user.save()
                    UserActivity.objects.create(
                        user = blacklist_user,
                        admin = admin,
                        system_message = "blacklist user",
                        message = reason,
                        activity_type = ACTIVITY_CLOSE_ACCOUNT,
                    )

                    UserActivity.objects.create(
                        user = blacklist_user,
                        admin = admin,
                        system_message = "blacklist user",
                        message = reason,
                        activity_type = ACTIVITY_STATUS_CHANGED,
                    )

                    UserActivity.objects.create(
                        user = blacklist_user,
                        admin = admin,
                        system_message = "blacklist user",
                        message = reason,
                        activity_type = ACTIVITY_SYSTEM,
                    )

            response = {
                "message": "finished blacklist user"
            }
            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json')
        except Exception as e:
            logger.error("Blacklist user error: {}".format(str(e)))
            return HttpResponse(status=400)





class SendSMS(View):


    def post(self, request, *args, **kwargs):

        data = json.loads(request.body)
        try:
            message = data['message']
            user_id = data['user_id']

            customUser = CustomUser.objects.get(pk=user_id)

            send_sms(message, customUser, customUser.phone)

            UserActivity.objects.create(
                user = CustomUser.objects.get(pk=user_id),
                admin = request.user,
                system_message = "Send SMS message to " + customUser.username,
                activity_type = ACTIVITY_MESSAGE,
            )

            response = {
                "message": "finished send sms to user"
            }
            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json')
        except Exception as e:
            logger.error("Blacklist send sms to user: {}".format(str(e)))
            return HttpResponse(status=400)



class ExportUserList(View):

    def post(self, request, *args, **kwargs):

        data = json.loads(request.body)
        head = data['head']
        search = data['search']
        status = data['status']
        try:
            user_filter = Q()
            if status and status != '-1':
                user_filter &= Q(member_status=status)
        
            if search:
                user_filter &= (Q(pk__contains=search)|Q(username__icontains=search)|Q(email__icontains=search)|Q(phone__contains=search)|Q(first_name__icontains=search)|Q(last_name__icontains=search))

            customUser = CustomUser.objects.filter(user_filter).order_by('username')

            user_list_data = [head]
            for user in customUser:
                ip_address_obj = UserAction.objects.filter(user=user, event_type=0).order_by('-created_time').first()
                deposit_amount = Transaction.objects.filter(user_id=user, transaction_type=0).aggregate(Sum('amount'))
                withdrawal_amount = Transaction.objects.filter(user_id=user, transaction_type=1).aggregate(Sum('amount'))
                ip_address = ip_address_obj.ip_addr if ip_address_obj else ""
                vip_manager = str(user.vip_managed_by.username) if user.vip_managed_by else ""
                balance = user.main_wallet + user.other_game_wallet
                ftd_time = user.ftd_time if user.ftd_time else ""
                ftd_time_amount = user.ftd_time_amount if user.ftd_time_amount != 0 else ""
                user_address = user.get_user_address()
                id_number = user.id_number if user.id_number else ""
                contribution = '{:.2f}'.format(calculateContribution(user))
                betTimes = GameBet.objects.filter(user=user, amount_wagered__gte=0).count()
                activeDays = int(betTimes)
                status_change_obj = UserActivity.objects.filter(user=user, activity_type=ACTIVITY_STATUS_CHANGED).order_by('created_time').first()
                close_obj = UserActivity.objects.filter(user=user, activity_type=ACTIVITY_CLOSE_ACCOUNT).order_by('created_time').first()
                status_changed = status_change_obj.created_time if status_change_obj else ""
                changed_by = status_change_obj.admin if status_change_obj else ""
                closure_reason = close_obj.system_message if close_obj and user.member_status == MEMBER_STATUS_CLOSED else ""
                user_list_data.append([user.pk,
                                      user.username,
                                      user.get_user_attribute_display(),
                                      vip_manager,
                                      user.time_of_registration,
                                      ftd_time,
                                      ftd_time_amount,
                                      balance,
                                      user.phone,
                                      user_address,
                                      id_number,
                                      ip_address,
                                      "",
                                      "",
                                      contribution,
                                      activeDays,
                                      user.get_member_status_display(),
                                      status_changed,
                                      changed_by,
                                      closure_reason]
                                    )

            return streamingExport(user_list_data, 'User List')

            # response = {}
            # return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json')
        except Exception as e:
            logger.error("Export user list error: {}".format(str(e)))
            return HttpResponse(status=400)

