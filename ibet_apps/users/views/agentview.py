from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as django_login, logout as django_logout
from django.contrib import messages
from django.contrib.auth import get_user_model

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy

from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.decorators.debug import sensitive_post_parameters
from django.views import generic
from django.views import View

from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import timedelta
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth, TruncDate, Coalesce
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from django.utils.crypto import get_random_string

from django_rest_passwordreset.signals import reset_password_token_created
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.views import get_password_reset_token_expiry_time

from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth, Coalesce
from django.template.defaulttags import register

from rest_auth.models import TokenModel
from rest_auth.app_settings import TokenSerializer, JWTSerializer, create_token

from allauth.account.utils import complete_signup
from allauth.account import app_settings as allauth_settings

from dateutil.relativedelta import relativedelta
from users.serializers import GameSerializer, CategorySerializer, UserDetailsSerializer, RegisterSerializer, LoginSerializer, CustomTokenSerializer, NoticeMessageSerializer, FacebookRegisterSerializer, FacebookLoginSerializer, BalanceSerializer
from users.serializers import LazyEncoder
from users.forms import RenewBookForm, CustomUserCreationForm
from users.models import Game, CustomUser, Category, Config, NoticeMessage, UserAction, UserActivity, Limitation
from games.models import Game as NewGame
from accounting.models import Transaction
from threading import Timer
from xadmin.views import CommAdminView
from users.views.helper import *

from operation.views import send_sms

import datetime
import logging
import os
import base64
import uuid
import csv
import random
import simplejson as json
import decimal
from utils.constants import *
import requests

import xmltodict

logger = logging.getLogger('django')

class AgentView(CommAdminView):
    def get(self, request):
        context = super().get_context()
        users = get_user_model().objects.all()
        agents = get_user_model().objects.exclude(agent_level='Normal')
        agents_has_referred = agents.filter(referred_by_id__isnull=False)
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        today = datetime.date.today()
        last_month = datetime.date.today().replace(day=1) + relativedelta(months=-1)
        before_last_month = datetime.date.today().replace(day=1) + relativedelta(months=-2)
        this_month = datetime.date.today().replace(day=1)

        # get transaction type 
        tran_type = Transaction._meta.get_field('transaction_type').choices
        commission_number = None
        for key, value in tran_type:
            if value is 'Commission':
                commission_number = key

        if commission_number is None:
            raise ValueError('No Commission Type Here!!!')      
        tran_commission = Transaction.objects.filter(transaction_type=commission_number)
        tran_with_commission_this_month = tran_commission.filter(Q(request_time__gte=last_month) & Q(request_time__lte=this_month))
        tran_with_commission_month_before = tran_commission.filter(Q(request_time__gte=before_last_month) & Q(request_time__lte=last_month))


        title = "Agent Overview"
        context["breadcrumbs"].append({'url': '/agent_overview/', 'title': title})
        context["title"] = title
        context["agents"] = agents
        context["premium_number"] = users.filter(agent_level='Premium').count()
        context["invalid_number"] = users.filter(agent_level='Invalid').count()
        context["normal_number"] = users.filter(agent_level='Normal').count()
        context["negative_number"] = users.filter(agent_level='Negative').count()
        context["new_ftd"] = agents.filter(ftd_time__range=[yesterday, today]).count()
        context["most_new_player"] = agents_has_referred.values("referred_by_id").annotate(downline_number=Count("referred_by_id")).order_by("-referred_by_id")


        # active user
        @register.filter(name='lookup')
        def lookup(dict, index):
            if index in dict:
                return dict[index]
            return '0'

        active_user_dict = {}
        for user, agent in agents.values_list('id', 'referred_by'):
            if agent is None:
                continue
            elif (Transaction.objects.all().filter(Q(user_id=user) & Q(request_time__gte=last_month)).exists()):
                active_user_dict.update({agent: active_user_dict.get(agent, 0) + 1})
        context["active_user_dict"] = active_user_dict

        # downline deposit
        downline_deposit = {}
        for user, agent, balance in agents.values_list('id', 'referred_by', 'main_wallet'):
            if agent is not None:
                downline_deposit.update({agent: downline_deposit.get(agent, 0) + balance})                
        context["downline_deposit"] = downline_deposit

        # commission system
        commision_transaction = tran_commission.annotate(month=TruncMonth('request_time')).values('month').annotate(total_commission=Sum('amount')).order_by('-month')
        
        commission = []

        for tran in commision_transaction:
            commission_dict = {}
            commission_dict['month'] = tran['month']
            commission_dict['total_commission'] = tran['total_commission']
            commission_dict['agent_number'] = agents.exclude(user_to_agent=None).filter(user_to_agent__lte=tran['month']+relativedelta(months=1)).count()
            # add a condition referred_by_id is none
            commission_dict['active_downline'] = Transaction.objects.filter(Q(request_time__gte=tran['month']) & Q(request_time__lte=tran['month']+relativedelta(months=1))).values('user_id').distinct().count()
            commission.append(commission_dict)
        
        context["commision_transaction"] = commission
        
        
        commission_last_month = {}
        commission_month_before = {}
        for agent_name,agent_id in agents.values_list('username','id'):
            try:
                cur = tran_with_commission_this_month.get(user_id_id=agent_id)
                commission_last_month.update({agent_name: cur.amount})
            except:
                commission_last_month.update({agent_name: '0'})
            

        for agent_name,agent_id in agents.values_list('username','id'):
            try:
                last = tran_with_commission_month_before.get(user_id_id=agent_id)
                commission_month_before.update({agent_name: last.amount})
            except:
                commission_month_before.update({agent_name: '0'})
        
        context["commission_last_month"] = commission_last_month
        context["commission_month_before"] = commission_month_before

        # premium application
        users_with_application_to_premium = users.exclude(user_application_time=None).order_by('-user_application_time')
        context["users_with_application_to_premium"] = users_with_application_to_premium

        return render(request, 'users/agent_list.html', context) 
    
    # post for new affiliate
    # def post(self, request, *args, **kwargs):
    #     username = generate_username()
    #     check_duplicate = CustomUser.objects.filter(username=username)
    #     while check_duplicate:
    #         username = generate_username
    #         check_duplicate = CustomUser.objects.filter(username=username)

    #     email = get_random_string(length=8)
    #     check_duplicate = CustomUser.objects.filter(email=email)
    #     while check_duplicate:
    #         email = get_random_string(length=8)
    #         check_duplicate = CustomUser.objects.filter(email=email)

    #     phone = ''.join([str(random.randint(0,10)) for i in range(10)])
    #     check_duplicate = CustomUser.objects.filter(phone=phone)
    #     while check_duplicate:
    #         phone = ''.join([str(random.randint(0,10)) for i in range(10)])
    #         check_duplicate = CustomUser.objects.filter(phone=phone)

    #     password = get_random_string(length=10)
    #     email = email + '@gmail.com'

    #     CustomUser.objects.create_user(username, email, phone, password)
    #     user = CustomUser.objects.filter(username=username)
    #     user.update(active=True, modified_time=timezone.now())

    #     context = super().get_context()
    #     agent_name = request.POST.get('username')
    #     args = {'agent_name':username, 'agent_password':password, 'user':user}
        
    #     return render(request,"users/agent_list.html",args)

class AgentDetailView(CommAdminView):
    def get(self, request, *args, **kwargs):
        context = super().get_context()
        return render(request,"users/agent_detail.html", context)
     
from xadmin.views import CommAdminView
from django.core import serializers
from django.http import HttpResponse
from django.db.models import Sum
from datetime import timedelta
from django.db.models import Q
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from django.conf import settings   
            

class ChangePassword(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            username = request.data['username']
            password = request.data['password']
            user = get_user_model().objects.get(username=username)
            user.set_password(password)
            user.save()
            return Response('Success')
        except:
            return Response('Failed')


class CheckUsernameExist(View):

    def get(self, request, *args, **kwargs):
        username = self.request.GET['username']
        user = get_user_model().objects.filter(username=username)
        if user:
            return HttpResponse(status=400)
        return HttpResponse(status=200)


class GenerateActivationCode(APIView):

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        user = get_user_model().objects.filter(username=username)
        random_num = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        user.update(activation_code=random_num)

        send_sms(str(random_num), user[0].pk)
    
        return Response(status=status.HTTP_200_OK)

class VerifyActivationCode(APIView):

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        code = request.data['code']
        user = get_user_model().objects.filter(username=username)
        if user[0].activation_code == code:
            user.update(active=True)
            user.update(activation_code='')
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserSearchAutocomplete(View):
    def get(self, request, *args, **kwargs):
        search = request.GET['search']
        # block = request.GET['block'] == 'true'

        logger.info('Search user, key: ' + search)
        # search_id = CustomUser.objects.filter(Q(pk__contains=search)&Q(block=block))
        # search_username = CustomUser.objects.filter(Q(username__contains=search)&Q(block=block))
        # search_email = CustomUser.objects.filter(Q(email__contains=search)&Q(block=block))
        # search_phone = CustomUser.objects.filter(Q(phone__contains=search)&Q(block=block))
        # search_first_name = CustomUser.objects.filter(Q(first_name__contains=search)&Q(block=block))
        # search_last_name = CustomUser.objects.filter(Q(last_name__contains=search)&Q(block=block))

        search_id = CustomUser.objects.filter(pk__contains=search)
        search_username = CustomUser.objects.filter(username__contains=search)
        search_email = CustomUser.objects.filter(email__contains=search)
        search_phone = CustomUser.objects.filter(phone__contains=search)
        search_first_name = CustomUser.objects.filter(first_name__contains=search)
        search_last_name = CustomUser.objects.filter(last_name__contains=search)

        search_id = serializers.serialize('json', search_id)
        search_username = serializers.serialize('json', search_username)
        search_email = serializers.serialize('json', search_email)
        search_phone = serializers.serialize('json', search_phone)
        search_first_name = serializers.serialize('json', search_first_name)
        search_last_name = serializers.serialize('json', search_last_name)

        search_id = json.loads(search_id)
        search_username = json.loads(search_username)
        search_email = json.loads(search_email)
        search_phone = json.loads(search_phone)
        search_first_name = json.loads(search_first_name)
        search_last_name = json.loads(search_last_name)
        response = {}

        id_data = []
        for user in search_id:
            userMap = {}
            userMap['id'] = user['pk']
            id_data.append(userMap)
        response['id'] = id_data

        username_data = []
        for user in search_username:
            userMap = {}
            userMap['id'] = user['pk']
            userMap['username'] = user['fields']['username']
            username_data.append(userMap)
        response['username'] = username_data

        email_data = []
        for user in search_email:
            userMap = {}
            userMap['id'] = user['pk']
            userMap['email'] = user['fields']['email']
            email_data.append(userMap)
        response['email'] = email_data

        phone_data = []
        for user in search_phone:
            userMap = {}
            userMap['id'] = user['pk']
            userMap['phone'] = user['fields']['phone']
            phone_data.append(userMap)
        response['phone'] = phone_data

        first_name_data = []
        for user in search_first_name:
            userMap = {}
            userMap['id'] = user['pk']
            userMap['firstName'] = user['fields']['first_name']
            first_name_data.append(userMap)
        response['firstName'] = first_name_data

        last_name_data = []
        for user in search_last_name:
            userMap = {}
            userMap['id'] = user['pk']
            userMap['lastName'] = user['fields']['last_name']
            last_name_data.append(userMap)
        response['lastName'] = last_name_data
        # print(str(response))
        logger.info('Search response: ' + json.dumps(response))
        return HttpResponse(json.dumps(response), content_type='application/json')


class ValidateAndResetPassowrd(APIView):

    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        
        current = request.data['current_password']
        new = request.data['new_password']
        user = self.request.user

        if not user.check_password(current):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new)
        user.save()
        return Response(status=status.HTTP_200_OK)


class CancelRegistration(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):

        username = request.data['username']
        user = CustomUser.objects.get(username=username)
        user.delete()
        return Response(status=status.HTTP_200_OK)

from users.views.helper import set_loss_limitation, set_deposit_limitation, set_temporary_timeout, set_permanent_timeout, get_old_limitations

class SetLimitation(View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        user_id = data['user_id']
        limit = data['limit']
        interval = data['interval']
        limit_type = data['type']
        
        # print(limit, interval, user_id, limit_type)
        user = CustomUser.objects.get(pk=user_id)

        oldLimitMap = get_old_limitations(user_id)
        # print(oldLimitMap)

        if limit_type == 'loss':
            otherLimits = oldLimitMap[LIMIT_TYPE_LOSS]
            set_loss_limitation(user_id, limit, interval, oldLimitMap, user)
        elif limit_type == 'deposit':
            set_deposit_limitation(user_id, limit, interval, oldLimitMap, user)

        return HttpResponse(('Successfully set the {} limitation'.format(limit_type)), status = 200)

class DeleteLimitation(View):

    def post(self, request, *args, **kwargs):
        
        data = json.loads(request.body)
        user_id = data['user_id']
        if checkUserBlock(user_id):
            blockMessage = _('Current user is blocked!')
            data = {
                "block": True,
                "blockMessage": blockMessage
            }
            return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json", status = 403)
        
        # limit = data['limit']
        interval = data['interval']
        limit_type = data['type']
        limit_id = data['id']
        
        if limit_type == 'deposit':
            limit_type = LIMIT_TYPE_DEPOSIT
        elif limit_type == 'loss':
            limit_type = LIMIT_TYPE_LOSS

        user = CustomUser.objects.get(pk=user_id)

        limit = Limitation.objects.get(user=user, limit_type=limit_type, interval=interval)
        time = timezone.now() + datetime.timedelta(days=1)
        limit.expiration_time = time
        limit.temporary_amount = limit.amount
        limit.amount = None
        limit.save()
        # return HttpResponse(('Successfully delete the {} limitation'.format(limit_type)), status = 200)
        message = 'Successfully delete the {} limitation and interval is {}'.format(limit_type, interval)
        current_tz = timezone.get_current_timezone()
        time = time.astimezone(current_tz)
        expiration_timeStr = str(time.astimezone(current_tz))

        
        response = {
            "expire_time": expiration_timeStr,
            "message": message
        }
        
        return JsonResponse(response, status = 200)


class CancelDeleteLimitation(View):

    def post(self, request, *args, **kwargs):
        
        data = json.loads(request.body)
        user_id = data['user_id']
        if checkUserBlock(user_id):
            blockMessage = _('Current user is blocked!')
            data = {
                "block": True,
                "blockMessage": blockMessage
            }
            return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json", status = 403)

        # limit = data['limit']
        interval = data['interval']
        limit_type = data['type']
        limit_id = data['id']

        if limit_type == 'deposit':
            limit_type = LIMIT_TYPE_DEPOSIT
        elif limit_type == 'loss':
            limit_type = LIMIT_TYPE_LOSS

        user = CustomUser.objects.get(pk=user_id)

        limit = Limitation.objects.get(user=user, limit_type=limit_type, interval=interval)
        limit.expiration_time = None
        limit.amount = limit.temporary_amount
        limit.temporary_amount = None
        limit.save()

        return HttpResponse(('Successfully cancel delete the {} limitation action'.format(limit_type)), status = 200)

class GetLimitation(View):

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('id')
        # limit_type = request.GET.get('type')
        # limit_type = limit_type.capitalize()
        # limitDict = dict(LIMIT_TYPE)
        # for key, value in limitDict.items():
        #     if value == limit_type:
        #         limit_type = key
        if checkUserBlock(user_id):
            blockMessage = _('Current user is blocked!')
            data = {
                "block": True,
                "blockMessage": blockMessage
            }
            return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json", status = 403)

        user = CustomUser.objects.get(pk=user_id)
        userJson = serializers.serialize('json', [user])
        userJson = json.loads(userJson)
        # print(userJson)

        # print(user)
        userLimitation = Limitation.objects.filter(user=user)

        intervalMap = {}
        for t in Limitation._meta.get_field('interval').choices:
            intervalMap[t[0]] = t[1]

        limitationDict = {
            'bet': [],
            'loss': [],
            'deposit': [],
            'withdraw': [],
            'tempBlock': {},
            'permBlock': {}
        }
        for limitation in userLimitation:
            temporary_amount = decimal.Decimal(0) if limitation.temporary_amount is None else  decimal.Decimal(limitation.temporary_amount)
            amount = None if limitation.amount is None else decimal.Decimal(limitation.amount)
            expiration_timeStr = ''
            expiration_time = ""
            if limitation.expiration_time:
                current_tz = timezone.get_current_timezone()
                expiration_time = limitation.expiration_time.astimezone(current_tz)
                expiration_timeStr = str(limitation.expiration_time.astimezone(current_tz))

            if not limitation.amount and not expiration_time:
                continue
            else:
                if expiration_time and expiration_time <= timezone.now():
                    continue
            
            if limitation.limit_type == LIMIT_TYPE_LOSS:
                lossMap = {
                    'amount': amount,
                    'intervalValue': limitation.interval,
                    'interval': intervalMap[limitation.interval],
                    'limitId': limitation.pk,
                    'temporary_amount': temporary_amount,
                    'expiration_time': expiration_timeStr
                }
                limitationDict['loss'].append(lossMap)
            elif limitation.limit_type == LIMIT_TYPE_DEPOSIT:
                
                depositMap = {
                    'amount': amount,
                    'intervalValue': limitation.interval,
                    'interval': intervalMap[limitation.interval],
                    'limitId': limitation.pk,
                    'temporary_amount': temporary_amount,
                    'expiration_time': expiration_timeStr
                }
                limitationDict['deposit'].append(depositMap)
    
        if user.temporary_block_interval:
            # print(user.temporary_block_timespan)
            # print(userJson[0]['fields']['temporary_block_timespan'])
            # timeList = userJson[0]['fields']['temporary_block_timespan'].split(' ')
            # time = timeList[0]
            # time = int(time)
            tempMap = {
                'temporary_block': user.temporary_block_interval
            }
            limitationDict['tempBlock'] = tempMap

        if user.permanent_block_interval:
            permanentMap = {
                'permanent_block': user.permanent_block_interval
            }
            limitationDict['permBlock'] = permanentMap
            # print(limitationDict)

        return HttpResponse(json.dumps(limitationDict, cls=DjangoJSONEncoder), content_type="application/json", status = 200)

class SetBlockTime(View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        lock_timespan = data['timespan']
        user_id = data['userId']

        if checkUserBlock(user_id):
            blockMessage = _('Current user is blocked!')
            data = {
                "block": True,
                "blockMessage": blockMessage
            }
            return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json", status = 403)

        # lock_type = data['type']
        tempIntervals = list(map(lambda x: x[0], TEMPORARY_INTERVAL))
        # print(user_id, lock_type, lock_timespan)
        if lock_timespan not in tempIntervals:
            set_permanent_timeout(user_id, lock_timespan)
            set_temporary_timeout(user_id, -1)
        else:
            set_temporary_timeout(user_id, lock_timespan)
            set_permanent_timeout(user_id, -1)
        
        return HttpResponse(('Successfully block the userId: {0} for lock timespan option {1}'.format(user_id, lock_timespan)), status = 200)
 
class MarketingSettings(View):

    def get(self, request, *args, **kwargs):
        user_id = request.GET['userId']

        if checkUserBlock(user_id):
            blockMessage = _('Current user is blocked!')
            data = {
                "block": True,
                "blockMessage": blockMessage
            }
            return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json", status = 403)

        user = CustomUser.objects.get(pk=user_id)
        contact_methods = user.contact_methods

        response = {
            "email": False,
            "phone": False,
            "sms": False,
            "postal": False
        }
           
        if contact_methods:
            contact_methods_list = contact_methods.split(',')
            for i in contact_methods_list:
                response[i] = True

        response.update(socialMedia=user.social_media)

        # print(response)
        logger.info("Sending marketing settings response: {}".format(json.dumps(response)))
        return HttpResponse(json.dumps(response), content_type='application/json', status=200)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        # print(data)
        email = data['email']
        phone = data['phone']
        sms = data['sms']
        postal_mail = data['postalMail']
        social_media = data['socialMedia']
        user_id = data['userId']

        if checkUserBlock(user_id):
            blockMessage = _('Current user is blocked!')
            data = {
                "block": True,
                "blockMessage": blockMessage
            }
            return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json", status = 403)

        contact_methods = []
        # print(email, phone, sms, postal_mail, social_media, user_id)
        if email is True:
            contact_methods.append("email")
        if phone is True:
            contact_methods.append("phone")
        if sms is True:
            contact_methods.append("sms")
        if postal_mail is True:
            contact_methods.append("postal")
        
        contact_methods_str = ''
        contact_methods_str = ','.join(str(i) for i in contact_methods)

        # print(contact_methods_str)
        # print(social_media)
        user = CustomUser.objects.get(pk=user_id)
        user.social_media = social_media
        user.contact_methods = contact_methods_str
        user.save()

        logger.info("Marketing settings for user: {}".format(str(user.username)))
        logger.info("Email: {}, Phone: {}, SMS: {}, Mail: {}, Social Media: {}".format(email, phone, sms, postal_mail, social_media))

        return HttpResponse(('Successfully set the marketing setting'), status = 200)



class PrivacySettings(View):

    def get(self, request, *args, **kwargs):
        user_id = request.GET['userId']

        if checkUserBlock(user_id):
            blockMessage = _('Current user is blocked!')
            data = {
                "block": True,
                "blockMessage": blockMessage
            }
            return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json", status = 403)
        
        user = CustomUser.objects.get(pk=user_id)
        response = {
            "bonus": user.bonusesProgram,
            "vip": user.vipProgram
        }

        logger.info("Sending privacy settings response: {}".format(json.dumps(response)))
        return HttpResponse(json.dumps(response), content_type='application/json', status=200)


    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        bonuses = data['bonuses']
        vip = data['vip']
        user_id = data['userId']
        if checkUserBlock(user_id):
            blockMessage = _('Current user is blocked!')
            data = {
                "block": True,
                "blockMessage": blockMessage
            }
            return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json", status = 403)

        user = CustomUser.objects.get(pk=user_id)
        user.bonusesProgram = bonuses
        user.vipProgram = vip
        user.save()

        logger.info("Privacy setting for user: {}".format(str(user.username)))
        logger.info("Bonuses: {}, VIP: {}".format(bonuses, vip))

        return HttpResponse(('Successfully set the privacy setting'), status = 200)

class ActivityCheckSetting(View):


    def get(self, request, *args, **kwargs):
        userId= request.GET['userId']
        user = CustomUser.objects.get(pk=userId)
        response = {
            "activityOpt": user.activity_check
        }

        return HttpResponse(json.dumps(response), content_type='application/json', status=200)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        userId = data['userId']
        activityOpt = data['activityOpt']

        user = CustomUser.objects.get(pk=userId)
        user.activity_check = activityOpt
        user.save()
        logger.info("Activity check setting for user: {}, and time option is: {}".format(str(user.username), activityOpt))
        return HttpResponse(('Successfully set the activity check setting'), status = 200)

class AgentView(CommAdminView):
    def get(self, request):
        context = super().get_context()
        users = get_user_model().objects.all()
        agents = get_user_model().objects.filter(agent_level='Affiliates')
        agents_has_referred = agents.filter(referred_by_id__isnull=False)
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        today = datetime.date.today()
        last_month = datetime.date.today().replace(day=1) + relativedelta(months=-1)
        before_last_month = datetime.date.today().replace(day=1) + relativedelta(months=-2)
        this_month = datetime.date.today().replace(day=1)
        downline_list = users.filter(referred_by_id__isnull=False)
        tran_for_active_user = Transaction.objects.filter(Q(transaction_type=0) & Q(transaction_type=2))

        # get transaction type 
        tran_type = Transaction._meta.get_field('transaction_type').choices
        commission_number = None
        for key, value in tran_type:
            if value is 'Commission':
                commission_number = key

        if commission_number is None:
            raise ValueError('No Commission Type Here!!!')      
        tran_commission = Transaction.objects.filter(transaction_type=commission_number)
        tran_with_commission_this_month = tran_commission.filter(Q(request_time__gte=last_month) & Q(request_time__lte=this_month))
        tran_with_commission_month_before = tran_commission.filter(Q(request_time__gte=before_last_month) & Q(request_time__lte=last_month))


        title = "Agent Overview"
        context["breadcrumbs"].append({'url': '/agent_overview/', 'title': title})
        context["title"] = title
        context["agents"] = agents
        context["affiliates_number"] = users.filter(agent_level='Affiliates').count()
        context["deactivated_number"] = users.filter(agent_level='Deactivated').count()
        context["refer_a_friend_number"] = users.filter(agent_level='Refer a friend').count()
        context["negative_number"] = users.filter(agent_level='Negative').count()
        context["internal_affiliates_number"] = users.filter(agent_level='Internal affiliates').count()
        context["new_ftd"] = agents.filter(ftd_time__range=[yesterday, today]).count()
        context["most_new_player"] = agents_has_referred.values("referred_by_id").annotate(downline_number=Count("referred_by_id")).order_by("-referred_by_id")

        # new data
        context["ftd_this_month"] = agents.filter(ftd_time__gte=last_month).count()
        # get the specific definition
        context["actives_this_month"] = tran_for_active_user.filter(Q(request_time__gte=last_month) & Q(user_id__in=agents)).values_list('user_id').distinct().count()
        context["affiliates_acquired_this_month"] = agents.filter(user_application_time__gte=last_month).count()


        # active user
        @register.filter(name='lookup')
        def lookup(dict, index):
            if index in dict:
                return dict[index]
            return '0'

        active_user_dict = {}
        for user, agent in agents.values_list('id', 'referred_by'):
            if agent is None:
                continue
            elif (Transaction.objects.all().filter(Q(user_id=user) & Q(request_time__gte=last_month)).exists()):
                active_user_dict.update({agent: active_user_dict.get(agent, 0) + 1})
        context["active_user_dict"] = active_user_dict

        # downline deposit
        downline_deposit = {}
        for user, agent, balance in agents.values_list('id', 'referred_by', 'main_wallet'):
            if agent is not None:
                downline_deposit.update({agent: downline_deposit.get(agent, 0) + balance})                
        context["downline_deposit"] = downline_deposit

        # commission system
        commision_transaction = tran_commission.annotate(month=TruncMonth('request_time')).values('month').annotate(total_commission=Sum('amount')).order_by('-month')
        
        commission = []

        for tran in commision_transaction:
            commission_dict = {}
            commission_dict['month'] = tran['month']
            commission_dict['total_commission'] = tran['total_commission']
            commission_dict['agent_number'] = agents.exclude(user_to_agent=None).filter(user_to_agent__lte=tran['month']+relativedelta(months=1)).count()
            # add a condition referred_by_id is none
            commission_dict['active_downline'] = Transaction.objects.filter(Q(request_time__gte=tran['month']) & Q(request_time__lte=tran['month']+relativedelta(months=1))).values('user_id').distinct().count()
            commission.append(commission_dict)
        
        context["commision_transaction"] = commission
        
        
        commission_last_month = {}
        commission_month_before = {}
        for agent_name,agent_id in agents.values_list('username','id'):
            try:
                cur = tran_with_commission_this_month.get(user_id_id=agent_id)
                commission_last_month.update({agent_name: cur.amount})
            except:
                commission_last_month.update({agent_name: '0'})
            

        for agent_name,agent_id in agents.values_list('username','id'):
            try:
                last = tran_with_commission_month_before.get(user_id_id=agent_id)
                commission_month_before.update({agent_name: last.amount})
            except:
                commission_month_before.update({agent_name: '0'})
        
        context["commission_last_month"] = commission_last_month
        context["commission_month_before"] = commission_month_before

        # premium application
        users_with_application_to_premium = users.exclude(user_application_time=None).order_by('-user_application_time')
        context["users_with_application_to_premium"] = users_with_application_to_premium

        return render(request, 'agents/agent_list.html', context) 
    

 

class AgentDetailView(CommAdminView):

    def get(self, request, *args, **kwargs):
        context = super().get_context()
        agent = CustomUser.objects.get(pk=self.kwargs.get('pk'))
        title = "Affiliate " + agent.username
        downline = CustomUser.objects.all().filter(referred_by_id=agent.id).values_list('id')
        affiliates_list = CustomUser.objects.all().filter(agent_level='Affiliates')
        active_downline = Transaction.objects.all().filter(Q(user_id__in=downline) & Q(request_time__gte=(datetime.date.today().replace(day=1))))
        downline_current_month_ftd_number = 0
        
        # get transaction type 
        tran_type = Transaction._meta.get_field('transaction_type').choices
        deposit_type_number = None
        withdraw_type_number = None
        bonus_type_number = None
        adjustment_type_number = None
        for key, value in tran_type:
            if value is 'Deposit':
                deposit_type_number = key
            elif value is 'Withdrawal':
                withdraw_type_number = key
            elif value is 'Bonus':
                bonus_type_number = key
            elif value is 'Adjustment':
                adjustment_type_number = key
            elif value is 'Commission':
                commission_type_number = key

        if deposit_type_number is None:
            raise ValueError('No Deposit Type Here!!!') 
        if withdraw_type_number is None:
            raise ValueError('No Withdraw Type Here!!!') 
        if bonus_type_number is None:
            raise ValueError('No Bouns Type Here!!!') 
        if adjustment_type_number is None:
            raise ValueError('No Adjustment Type Here!!!')
        if commission_type_number is None:
            raise ValueError('No Commission Type Here!!!')  
        downline_deposit = Transaction.objects.all().filter(Q(user_id__in=downline) & Q(transaction_type=deposit_type_number)).aggregate(total_deposit=Coalesce(Sum('amount'), 0))
        commission_tran = Transaction.objects.all().filter(Q(transaction_type=commission_type_number) & Q(user_id=agent.id))
        current_affiliate_ip = UserAction.objects.all().filter(user=agent.pk).values('ip_addr')
        
        
        context["title"] = title
        context["breadcrumbs"].append({'url': '/cwyadmin/', 'title': title})
        # affiliate details
        context["agent"] = agent
        context["name"] = agent.username
        context["id"] = agent.id
        context["level"] = agent.agent_level
        context["status"] = agent.agent_status
        context["balance"] = agent.main_wallet
        # commission
        context["commission_this_month"] = commission_tran.filter(request_time__gte=(datetime.date.today().replace(day=1))).aggregate(comm=Coalesce(Sum('amount'), 0))
        context["commission_last_month"] = commission_tran.filter(Q(request_time__lte=(datetime.date.today().replace(day=1))) & Q(request_time__gte=datetime.date.today().replace(day=1)+relativedelta(months=-1))).aggregate(comm=Coalesce(Sum('amount'), 0))
        context["commission_before_last"] = commission_tran.filter(Q(request_time__lte=(datetime.date.today().replace(day=1)+relativedelta(months=-1))) & Q(request_time__gte=datetime.date.today().replace(day=1)+relativedelta(months=-2))).aggregate(comm=Coalesce(Sum('amount'), 0))
        # downline status
        context["downline_number"] = downline.aggregate(total_users=Count('id'))
        context["active_users"] = active_downline.values('user_id').distinct().count()
        context["downline_deposit"] = downline_deposit
        context["promition_link"] = agent.referral_id
        
        # related affiliates
        #get this agent's all ip addresses
        #filer other agents who have use these addresses before
        agent_ip_list = UserAction.objects.filter(user=agent.pk).values_list('ip_addr').distinct()
        related_agents_list = UserAction.objects.filter(ip_addr__in=agent_ip_list).values('user').exclude(user=agent.pk).distinct()
        related_affiliates_data = []
        for related_affiliate in related_agents_list:
            related_affiliates_info = {}
            related_affiliates_info['member_id'] = related_affiliate['user']
            related_affiliates_info['balance'] = CustomUser.objects.all().get(pk=related_affiliate['user']).main_wallet
            related_affiliates_data.append(related_affiliates_info)
        context["related_affiliates"] = related_affiliates_data

        # downline list
        downline_list = []
        for i in agent.referees.all():
            downline_info = {}
            agent_tran = Transaction.objects.all().filter(user_id_id=i.pk)
            # print(agent_tran)
            downline_info['agent_id'] = i.pk
            downline_info['username'] = i.username
            downline_info['time_of_registration'] = i.time_of_registration
            downline_info['last_login_time'] = i.last_login_time
            downline_info['ftd_time'] = i.ftd_time
            downline_info['deposit'] = agent_tran.filter(transaction_type=0).aggregate(sum_deposit=Coalesce(Sum('amount'), 0))
            downline_info['withdraw'] = agent_tran.filter(transaction_type=1).aggregate(sum_withdraw=Coalesce(Sum('amount'), 0))
            downline_info['bouns'] = agent_tran.filter(transaction_type=6).aggregate(sum_bouns=Coalesce(Sum('amount'), 0))
            downline_info['adjustment'] = agent_tran.filter(transaction_type=7).aggregate(sum_adjustment=Coalesce(Sum('amount'), 0))
            downline_info['balance'] = i.main_wallet
            downline_list.append(downline_info)
        
        context["downline_list"] = downline_list
        context["agent_referee"] = agent.referees.all()

        # edit detail top
        context["agent_level"] = agent.affiliate_level
        context["agent_status"] = agent.agent_status
        context["transerfer_between_levels"] = agent.transerfer_between_levels

        #edit detail bottom
        context["commission_type"] = Commission.objects.all().get(pk=agent.commission_id_id)

        # opeartion report
        # get current agent's transaction and sort by date
        agent_tran_list = Transaction.objects.filter(user_id=agent.pk).annotate(operation_date=TruncDate('arrive_time')).order_by('-operation_date').values('operation_date').distinct()

        opeartion_report = []
        for tran in agent_tran_list:
            
            opeartion_info = {}
            cur_operation_data = Transaction.objects.filter(user_id=agent.pk).filter(arrive_time__lte=tran['operation_date'])
            opeartion_info['date'] = tran['operation_date']
            opeartion_info['cumulative_deposit'] = cur_operation_data.filter(transaction_type=0).aggregate(sum_deposit=Coalesce(Sum('amount'), 0))['sum_deposit']
            opeartion_info['cumulative_withdrawal'] = cur_operation_data.filter(transaction_type=1).aggregate(sum_withdrawal=Coalesce(Sum('amount'), 0))['sum_withdrawal']
            opeartion_info['system_bouns'] = cur_operation_data.filter(transaction_type=6).aggregate(sum_bouns=Coalesce(Sum('amount'), 0))['sum_bouns']
            # need calculate
            opeartion_info['downline_transfer'] = 0
            opeartion_info['turnover'] = 0
            opeartion_report.append(opeartion_info)
        context["opeartion_report"] = opeartion_report

        # get manager list and search for name
        # global variable
        manager_id_list = CustomUser.objects.values('managed_by').distinct()
        manager_name_list = CustomUser.objects.filter(pk__in=manager_id_list).values('username')

        return render(request,"agents/agent_detail.html", context)

def fsearch(request):
    q = request.GET['q']
    manager_id_list = CustomUser.objects.values('managed_by').distinct()
    manager_name_list = CustomUser.objects.filter(pk__in=manager_id_list).values('username')
    recontents = CustomUser.objects.filter(pk__in=manager_id_list).filter(username__startswith=q)
    rejson = []
    for recontent in recontents:
        rejson.append(recontent.username)
    return HttpResponse(json.dumps(rejson), content_type='application/json') 