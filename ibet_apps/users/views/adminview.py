from xadmin.views import CommAdminView
from django.core import serializers
from django.http import HttpResponse
from django.db.models import Sum
from datetime import timedelta
from django.db.models import Q
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
from games.models import GameBet, Category

import requests
import logging
import pytz


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
        context['userPhotoId'] = self.download_user_photo_id(customUser.username)
        context['userLoginActions'] = UserAction.objects.filter(user=customUser, event_type=0)[:20]
        transaction = Transaction.objects.filter(user_id=customUser)
        context['block'] = False
        temporaryBlockRes = {}
        permanentBlockRes = {}
        context['temperaryBlock'] = temporaryBlockRes
        context['permanentBlock'] = permanentBlockRes
        if customUser.block is True:
            blockLimitationDeatil = Limitation.objects.filter(user=customUser, limit_type=LIMIT_TYPE_BLOCK).order_by('-created_time').first()
            data = {
                'date': blockLimitationDeatil.created_time,
                'admin': blockLimitationDeatil.admin,
            }
            context['blockDetail'] = data
            context['block'] = True

        elif checkUserBlock(customUser):
            expired_time = ""
            blocked_time = ""
            temporaryStr = ""
            temporaryCode = ""
            permanentStr = ""
            permanentCode = ""
            blocked_time = customUser.temporary_block_time or customUser.permanent_block_time
            if customUser.temporary_block_time:
                expired_time = customUser.temporary_block_time
                if customUser.temporary_block_interval == INTERVAL_PER_DAY:
                    expired_time = expired_time + datetime.timedelta(days=1)
                    temporaryStr = "one day"
                    temporaryCode = customUser.temporary_block_interval
                elif customUser.temporary_block_interval == INTERVAL_PER_WEEK:
                    expired_time = expired_time + datetime.timedelta(days=7)
                    temporaryStr = "one week"
                    temporaryCode = INTERVAL_PER_WEEK
                elif customUser.temporary_block_interval == INTERVAL_PER_MONTH:
                    expired_time = expired_time + datetime.timedelta(days=30)
                    temporaryStr = "one month"
                    temporaryCode = INTERVAL_PER_MONTH
                
            elif customUser.permanent_block_time:
                expired_time = customUser.permanent_block_time
                if customUser.permanent_block_interval == INTERVAL_PER_SIX_MONTH:
                    expired_time = expired_time + datetime.timedelta(6*365/12)
                    permanentStr = "six months"
                    permanentCode = INTERVAL_PER_SIX_MONTH
                elif customUser.permanent_block_interval == INTERVAL_PER_ONE_YEAR:
                    expired_time = expired_time + datetime.timedelta(365)
                    permanentStr = "one year"
                    permanentCode = INTERVAL_PER_ONE_YEAR
                elif customUser.permanent_block_interval == INTERVAL_PER_THREE_YEAR:
                    expired_time = expired_time + datetime.timedelta(365*3)
                    permanentStr = "three years"
                    permanentCode = INTERVAL_PER_THREE_YEAR
                elif customUser.permanent_block_interval == INTERVAL_PER_FIVE_YEAR:
                    expired_time = expired_time + datetime.timedelta(365*5)
                    permanentStr = "five years"
                    permanentCode = INTERVAL_PER_FIVE_YEAR
                
            temporaryBlockRes = {
                'temporaryStr': temporaryStr,
                'temporaryCode': temporaryCode
            }

            permanentBlockRes = {
                'permanentStr': permanentStr,
                'permanentCode': permanentCode
            }

            data = {
                "expired_time": expired_time,
                "date": blocked_time,
                "admin": "User themselve"
            }
            context['blockDetail'] = data
            context['block'] = True
            context['temperaryBlock'] = temporaryBlockRes
            context['permanentBlock'] = permanentBlockRes

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
                    'balance': tran['fields']['amount'],
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
        context['userLastIpAddr'] = userLastLogin
        context['loginCount'] = UserAction.objects.filter(user=customUser, event_type=0).count()
        context['activeTime'] = GameBet.objects.filter(user=customUser, amount_wagered__gte=0).count()

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
                time = time.strftime("%B %d, %Y, %I:%M %p")
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
                    'channel': channelMap[deposit['fields']['channel']],
                    'method': deposit['fields']['method'],
                }
                lastDeposit.append(depositDict)
            context['lastDeposits'] = lastDeposit[:1]
        else:
            context['lastDeposits'] = {}

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
                    'channel': channelMap[withdraw['fields']['channel']],
                    'method': withdraw['fields']['method'],
                }
                lastWithdraw.append(withdrawDict)
            context['lastWithdraws'] = lastWithdraw[0]
        else:
            context['lastWithdraws'] = {}


        activity = UserActivity.objects.filter(user=customUser).order_by("-created_time")
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

        # userJson = serializers.serialize('json', [customUser])
        # userJson = json.loads(userJson)
        
        return render(request, 'user_detail.html', context)


    def post(self, request):
        post_type = request.POST.get('type')
        user_id = request.POST.get('user_id')

        if post_type == 'edit_user_detail':
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            birthday = request.POST.get('birthday')
            address = request.POST.get('address')
            city = request.POST.get('city')
            zipcode = request.POST.get('zipcode')
            country = request.POST.get('country')
            user_id_img = request.POST.get('user_id_img')
            # upload image to S3
            self.upload_user_photo_id(username, user_id_img)

            CustomUser.objects.filter(pk=user_id).update(
                username=username, first_name=first_name, 
                last_name=last_name, email=email, 
                phone=phone, date_of_birth=birthday, 
                street_address_1=address, city=city,
                zipcode=zipcode, country=country)
            
            logger.info('Finished update user: ' + str(username) + 'info to DB')
            # print(CustomUser.objects.get(pk=user_id).id_image)

            return HttpResponseRedirect(reverse('xadmin:user_detail', args=[user_id]))
        
        elif post_type == 'update_message':
            admin_user = request.POST.get('admin_user')
            message = request.POST.get('message')

            UserActivity.objects.create(
                user = CustomUser.objects.filter(pk=user_id).first(),
                admin = CustomUser.objects.filter(username=admin_user).first(),
                message = message,
                activity_type = 3,
            )

            logger.info('Finished create activity to DB')
            return HttpResponseRedirect(reverse('xadmin:user_detail', args=[user_id]))

        elif post_type == 'activity_filter':
            activity_type = request.POST.get('activity_type')

            user = CustomUser.objects.get(pk=user_id)
            # print(str(activity_type))
            
            if activity_type == 'all':
                activitys = UserActivity.objects.filter(user=user).order_by('-created_time')
            else:
                activitys = UserActivity.objects.filter(user=user, activity_type=activity_type).order_by('-created_time')
            
            activitys = serializers.serialize('json', activitys)
            activitys = json.loads(activitys)
            response = []
            for act in activitys:
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
            # print(str(response))

            return HttpResponse(json.dumps(response), content_type='application/json')

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
            if temporary_time:
                set_temporary_timeout(user_id, temporary_time)
            if permanent_time:
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
            adminUsername = request.POST.get('admin_user')
            admin = CustomUser.objects.get(username=adminUsername)
            adminId = admin.pk
            user = CustomUser.objects.get(pk=user_id)
                
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

                user.block = True
                user.temporary_block_time = datetime.datetime.now()
                # user = CustomUser.objects.filter(pk=user_id).update(block=True, temporary_block_time=datetime.datetime.now())
                user.save()
                limitation = Limitation.objects.create(user=user, limit_type=LIMIT_TYPE_BLOCK, admin=admin)
                logger.info("Block user: " + str(user.username) + " by admin user: " + str(adminUsername))
            else:
                # user = CustomUser.objects.filter(pk=user_id).update(block=False, temporary_block_time=None)
                user.block = False
                user.temporary_block_time = None
                user.save()
                limitation = Limitation.objects.create(user=user, limit_type=LIMIT_TYPE_UNBLOCK, admin=admin)
                logger.info("Unblock user: " + str(user.username) + " by admin user: " + str(adminUsername))

            return HttpResponseRedirect(reverse('xadmin:user_detail', args=[user_id]))
    
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
            userDict['risk_level'] = ''
            userDict['balance'] = user.main_wallet + user.other_game_wallet
            userDict['product_attribute'] = ''
            userDict['time_of_registration'] = user.time_of_registration
            userDict['ftd_time'] = user.ftd_time
            userDict['verfication_time'] = user.verfication_time
            userDict['id_location'] = user.id_location
            userDict['phone'] = user.phone
            userDict['address'] = user.get_user_address()
            # userDict['address'] = str(user.street_address_1) + ', ' + str(user.street_address_2) + ', ' + str(user.city) + ', ' + str(user.state) + ', ' + str(user.country) 
            userDict['deposit_turnover'] = ''
            userDict['bonus_turnover'] = ''
            userDict['contribution'] = 0
            # depositTimes = Transaction.objects.filter(user_id=user, transaction_type=0).count()
            # withdrawTimes = Transaction.objects.filter(user_id=user, transaction_type=1).count()
            betTims = GameBet.objects.filter(user=user, amount_wagered__gte=0).count()
            activeDays = int(betTims)
            userDict['active_days'] = activeDays
            userDict['member_status'] = user.get_member_status_display() if user.get_member_status_display() else ""
            userDict['status_changed'] = ''
            userDict['changed_by'] = ''
            userDict['closure_reason'] = ''


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
                userDict['verfication_time'] = str(user.verfication_time)
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
                'status': user.member_status if user.member_status else '',
                'playerSegment': user.vip_level.level if user.vip_level else '',
                'riskLevel': user.risk_level,
                'manager': user.vip_managed_by.username if user.vip_managed_by else '',
                'email': user.email,
                'phone': user.phone,
                'address': user.street_address_1 + ( " " + user.street_address_2 if user.street_address_2 else ""),
                'city': user.city,
                'zipcode': user.zipcode,
                'country': user.country,
                'idApplicationTime': user.verfication_time if user.verfication_time else "",
                'idReviewTime': user.verfication_time if  user.verfication_time else "",
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
                        'balance': tran['fields']['amount'],
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
            bet_time = bet_obj.bet_time.strftime("%B %d, %Y, %I:%M %p")

            # try:
            #     resolved_time = datetime.datetime.strptime(bet_obj.resolved_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            # except:
            #     resolved_time = datetime.datetime.strptime(bet_obj.resolved_time, "%Y-%m-%dT%H:%M:%SZ")
            resolved_time = bet_obj.resolved_time.strftime("%B %d, %Y, %I:%M %p")

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
