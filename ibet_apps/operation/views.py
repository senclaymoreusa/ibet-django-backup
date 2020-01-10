from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.views import View
from django.core import serializers
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import status
from rest_framework.test import APIRequestFactory

import datetime
from datetime import timedelta, time
import boto3
import json
import logging
import pytz

from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from operation.serializers import AWSTopicSerializer, NotificationSerializer, NotificationLogSerializer, NotificationToUsersSerializer, UserToAWSTopicSerializer, MessageUserGroupSerializer, CampaignSerializer
from operation.models import *
from users.models import CustomUser
from system.models import UserGroup, UserToUserGroup
from xadmin.views import CommAdminView
from utils.constants import *
from utils.aws_helper import getThirdPartyKeys, getAWSClient
from users.views.helper import *
from django.utils.translation import ugettext_lazy as _
from users.serializers import LazyEncoder


logger = logging.getLogger('django')


def send_message(notification_id):
    notification = Notification.objects.get(pk=notification_id)
    # All messages
    queryset = NotificationToUsers.objects.filter(notification_id=notification)
    # connect AWS S3
    third_party_keys = getThirdPartyKeys("ibet-admin-dev", "config/sns.json")

    # AWS SNS Client
    sns = boto3.resource('sns', region_name=AWS_SMS_REGION)
    client = getAWSClient('sns', third_party_keys, AWS_SMS_REGION)

    # Push Notification
    if notification.is_push_message:
        try:
            platform_endpoint = sns.PlatformEndpoint(third_party_keys["SNS_PLATFORM_ENDPOINT_ARN"])
            
            platform_endpoint.publish(
                Message=notification.content_text,
            )
            logger.info("Enabled Push Notification")
        except Exception as e:
            logger.error("Sending push notification error!:", e)
        
    # SMS Notification
    if notification.is_sms_message:
        try:
            for message in queryset:
                notifier = CustomUser.objects.get(username=message.notifier_id)
                phone = str(notifier.phone)
                client.publish(PhoneNumber=phone, Message=notification.content_text)

            logger.info("Enabled SMS Notification")
        except Exception as e:
            logger.error("Unexpected error: %s" % e)
            return Response("INVAILD SNS CLIENT", status=status.HTTP_401_UNAUTHORIZED)

    # Email Notification
    if notification.is_email_message:
        # AWS SNS Topic
        topic = sns.Topic(third_party_keys["SNS_TOPIC_ARN"])
        topic.publish(
            Message=notification.content_text,
            Subject='iBet Notification',
        )
        logger.info("Enabled Email Notification")

        Notification.objects.filter(pk=notification_id).update(status=MESSAGE_APPROVED)
        logger.info('create notification message')
        # return HttpResponseRedirect(reverse('xadmin:notification'))
    else:
        logger.error("Sending Email Notification error!")
        return HttpResponse("Can not send Email!")


class NotifierTagsInput(View):
    def get(self, request, *args, **kwargs):
    
        search_member = CustomUser.objects.all()
        search_group = UserGroup.objects.filter(groupType=MESSAGE_GROUP)

        search_member = serializers.serialize('json', search_member)
        search_group = serializers.serialize('json', search_group)

        search_member = json.loads(search_member)
        search_group = json.loads(search_group)
    
        response = {}
    
        member_data = []
        for member in search_member:
            memberMap = {}
            memberMap["type"] = "member"
            # memberMap["pk"] = member["fields"]["pk"]
            memberMap["name"] = member["fields"]["username"]
            member_data.append(memberMap)
        response["member"] = member_data
    
        group_data = []
        for group in search_group:
            groupMap = {}
            groupMap["type"] = "group"
            # groupMap["pk"] = group["fields"]["pk"]
            groupMap["name"] = group["fields"]["name"]
            group_data.append(groupMap)

        response["group"] = group_data
    
        logger.info('Search response: ' + json.dumps(response))
        try:
            return HttpResponse(json.dumps(response), content_type='application/json')
        except Exception as e:
            logger.error(e)

class NotifierSearchAutocomplete(View):
    def get(self, request, *args, **kwargs):
        search = request.GET.get('search')
    
        logger.info('Search notification, key: ' + search)
    
        search_member = CustomUser.objects.filter(Q(username__icontains=search))
        # search_body = Notification.objects.filter(content_text__contains=search)

        search_member = serializers.serialize('json', search_member)
        # search_body = serializers.serialize('json', search_body)

        search_member = json.loads(search_member)
        # search_body = json.loads(search_body)
    
        response = {}
    
        member_data = []
        for member in search_member:
            memberMap = {}
            memberMap["member"] = member["fields"]["username"]
            member_data.append(memberMap)
        response["member_data"] = member_data
    
        # body_data = []
        # for notification in search_body:
        #     notificationMap = {}
        #     notificationMap['body'] = notification['body']
        #     body_data.append(notificationMap)
        # response['body'] = body_data
    
        logger.info('Search response: ' + json.dumps(response))
        try:
            return HttpResponse(json.dumps(response), content_type='application/json')
        except Exception as e:
            logger.error(e)


class NotificationSearchAutocomplete(View):
    def get(self, request, *args, **kwargs):
        try:
            search = request.GET.get('search')
            tab = request.GET.get('tab')

            logger.info('Search notification, key: ' + search)

            search_subject = Notification.objects.filter(Q(subject__contains=search)&Q(status=tab))
            search_content = Notification.objects.filter(Q(content_text__contains=search)&Q(status=tab))

            # search_campaign = Notification.objects.filter(Q(campaign__name__icontains=search))

            search_subject = serializers.serialize('json', search_subject)
            search_content = serializers.serialize('json', search_content)
            # search_body = serializers.serialize('json', search_body)

            search_subject = json.loads(search_subject)
            search_content = json.loads(search_content)

            response = {}

            subject_data = []
            for notification in search_subject:
                notificationMap = {}
                notificationMap["subject"] = notification["fields"]["subject"]
                notificationMap["id"] = notification["pk"]
                subject_data.append(notificationMap)
            response["subject"] = subject_data

            content_data = []
            for content in search_content:
                contentMap = {}
                contentMap["content"] = content["fields"]["content_text"]
                contentMap["id"] = content['pk']
                content_data.append(contentMap)
            response["content"] = content_data

            # campaign_data = []
            # for campaign in search_campaign:
            #     campaignMap = {}
            #     campaignMap["campaign"] = campaign.name
            #     campaignMap["id"] = campaign.pk
            #     campaign_data.append(campaignMap)
            # response["campaign"] = campaign_data

            # body_data = []
            # for notification in search_body:
            #     notificationMap = {}
            #     notificationMap['body'] = notification['body']
            #     body_data.append(notificationMap)
            # response['body'] = body_data

            logger.info('Search response: ' + json.dumps(response))
            return HttpResponse(json.dumps(response), content_type='application/json')
        except Exception as e:
            logger.error("Autocomplete Search Error: {}".format(repr(e)))
            return HttpResponse(repr(e), status=400)


def isTimeFormat(time_str):
    if time_str is None:
        return False
    try:
        datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False


def isDateFormat(date_str):
    if date_str is None:
        return False
    try:
        datetime.datetime.strptime(date_str, "%m/%d/%Y")
        return True
    except ValueError:
        return False


class NotificationView(CommAdminView):
    def get(self, request, *arg, **kwargs):
        search = request.GET.get('search')
        # time_range = request.GET.get('time_range')
        start_time = request.GET.get('from')
        end_time = request.GET.get('to')
        pageSize = request.GET.get('pageSize')
        offset = request.GET.get('offset')
        tab = request.GET.get('tab')

        if pageSize is None:
            pageSize = 20
        else: 
            pageSize = int(pageSize)

        if offset is None or int(offset) < 1:
            offset = 1
        else:
            offset = int(offset)

        if tab is None:
            tab = MESSAGE_APPROVED
        else:
            tab = int(tab)

        # set context
        context = super().get_context()
        title = 'message'
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context["title"] = title
        context['time'] = timezone.now()

        context['all_user'] = CustomUser.objects.all()
        context['waiting_list'] = Notification.objects.filter(auditor=self.user.pk).count()
        context['imagePath'] = PUBLIC_S3_BUCKET + 'admin_images/'

        # set filter
        msg_filter = Q(status=tab)

        if search:
            logger.info('Search notification, key: ' + search)
            msg_filter = msg_filter & (Q(subject__icontains=search)|Q(campaign__name__icontains=search))
            # queryset = Notification.objects.filter(Q(subject__contains=search)&Q(status=tab))
            # queryset = Notification.objects.filter(status=tab)

        current_tz = timezone.get_current_timezone()
        tz = pytz.timezone(str(current_tz))
        if start_time:
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d")
            start_time = tz.localize(datetime.datetime.combine(start_time, time())) 
            msg_filter = msg_filter & Q(publish_on__gt=start_time)

        if end_time:
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d")
            end_time = tz.localize(datetime.datetime.combine(end_time, time())) 
            msg_filter = msg_filter & Q(publish_on__lt=end_time)

        # if start_time:
        #     try:
        #         current_tz = timezone.get_current_timezone()
        #         start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M").astimezone(current_tz)
        #         end_time =  datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M").astimezone(current_tz)

        #         msg_filter = msg_filter & Q(publish_on__range=(start_time, end_time))
        #         # queryset = Notification.objects.filter(publish_on__range=(start_time, end_time))
        #     except Exception as e:
        #         logger.error(e)

        queryset = Notification.objects.filter(msg_filter).order_by('-publish_on')

        notification_list = []

        for msg in queryset:
            notification_item = {}
            notification_item['pk'] = msg.pk
            notification_item['subject'] = msg.subject
            notification_item['campaign'] = msg.campaign
            notification_item["creator"] = msg.creator
            notification_item["publish_on"] = msg.publish_on
            notification_item["status"] = msg.status
            notifiers = NotificationToUsers.objects.filter(notification_id=msg)
            if len(notifiers) > 1:
                notification_item["notifiers"] = str(len(notifiers)) + " users"
            elif len(notifiers) == 0:
                notification_item["notifiers"] = "None"
            else:
                notification_item["notifiers"] = notifiers[0].notifier_id

            notification_item["sent_count"] = NotificationToUsers.objects.filter(notification_id=msg).count()
            notification_item["open"] = NotificationToUsers.objects.filter(Q(notification_id=msg)&Q(is_read=True)).count()
            if(notification_item["sent_count"] == 0):
                notification_item["rate"] = ""
            else:
                notification_item["rate"] = str(round((notification_item["open"] / notification_item["sent_count"]) * 100, 2)) + '%'

            notification_list.append(notification_item)

        paginator = Paginator(notification_list, pageSize)
        context["notifications"] = paginator.get_page(offset)

        campArr = []
        appCamp = Campaign.objects.all().distinct('name')
        for i in appCamp:
            campArr.append({"id" :i.pk, "name": i.name})
        context['campaignOpt'] = campArr

        logger.info("GET NotificationView")
        return render(request, 'notification/index.html', context)

    def post(self, request, *arg, **kwargs):
        data = {
            "campaign": request.POST.get('campaign'),
            "subject": request.POST.get('subject'),
            "content_text": request.POST.get('content_text'),
            "creator": self.user.id,
        }
        
        direct_check = request.POST.get('direct_check')
        email_check = request.POST.get('email_check')
        SMS_check = request.POST.get('SMS_check')
        push_check = request.POST.get('push_check')


        if direct_check == "true":
            data["is_direct_message"] = True

        if email_check == "true":
            data["is_email_message"] = True

        if SMS_check == "true":
            data["is_sms_message"] = True

        # if push_check == "true":
        #     data["is_push_message"] = True
        

        notifiers = request.POST.get("member_list")
        groups = request.POST.get("group_list")
        notifiers = json.loads(notifiers)
        groups = json.loads(groups)

        total_num = len(notifiers)

        for group in groups:
            group = UserGroup.objects.get(name=group, groupType=MESSAGE_GROUP)
            total_num = total_num + UserToUserGroup.objects.filter(group=group).count()

        logger.info("message send to %s members", total_num)

        if total_num < NOTIFICATION_CONSTRAINTS_QUANTITY:
            data["status"] = MESSAGE_APPROVED

        serializer = NotificationSerializer(data=data)

        try:
            if serializer.is_valid():
                with transaction.atomic():
                    notification = serializer.save()
                    logger.info("Save notification message")
                    # # store notification data in NotificationLog
                    for group in groups:
                        group = UserGroup.objects.get(name=group, groupType=MESSAGE_GROUP)
                        group.time_used = group.time_used + 1
                        group.save()
                        NotificationToGroup.objects.create(notification=notification, group=group)
                        group_users = UserToUserGroup.objects.filter(group=group)
                        for group_user in group_users:
                            NotificationToUsers.objects.get_or_create(notification_id=notification, notifier_id=group_user.user)

                    
                    for notifier in notifiers:
                        NotificationToUsers.objects.get_or_create(notification_id=notification, notifier_id=CustomUser.objects.get(username=notifier))

                    logger.info("Save notification log")

                    if(notification.status == MESSAGE_APPROVED):
                        send_message(notification.pk)

                    return HttpResponseRedirect(reverse('xadmin:notification'))
                else:
                    logger.error(serializer.errors)
                    return HttpResponse(serializer.errors)
        except Exception as e:
            logger.error("Admin Notification View Error -- {}".format(repr(e)))
            return HttpResponse(repr(e))


class NotificationDetailView(CommAdminView):
    def get(self, request, *args, **kwargs):
        try:
            notification_id = request.GET.get('msgId')
            
            notification = Notification.objects.get(pk=notification_id)

            response = {}
            response["subject"] = notification.subject
            response["content_text"] = notification.content_text

            return HttpResponse(json.dumps(response), content_type='application/json', status=200)
        except Exception as e:
            logger.error(repr(e))
            return HttpResponse(status=400)


class AuditNotificationView(CommAdminView):
    def get(self, request, *arg, **kwargs):
        context = super().get_context()
        title = 'message'
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context["title"] = title
        context['time'] = timezone.now()
        context['current_user'] = self.user
        queryset = Notification.objects.filter(status=MESSAGE_PENDING).order_by('-publish_on')
        serializer = NotificationSerializer(queryset, many=True)
        context["queryset"] = queryset
        return render(request, 'notification/audit.html', context)

    def post(self, request, *arg, **kwargs):
        notification_id = request.POST.get('notification_id')
        notification = Notification.objects.get(pk=notification_id)
        # All messages
        queryset = NotificationToUsers.objects.filter(notification_id=notification_id)
        # notification_methods = message.notification_method

        # connect AWS S3
        third_party_keys = getThirdPartyKeys("ibet-admin-dev", "config/sns.json")

        # AWS SNS Client
        sns = boto3.resource('sns', region_name=AWS_SMS_REGION)
        client = getAWSClient('sns', third_party_keys, AWS_SMS_REGION)

        # Push Notification
        if notification.is_push_message:
            platform_endpoint = sns.PlatformEndpoint(third_party_keys["SNS_PLATFORM_ENDPOINT_ARN"])
            
            platform_endpoint.publish(
                Message=notification.content_text,
            )
            logger.info("Enabled Push Notification")
            
        # SMS Notification
        if notification.is_sms_message:
            try:
                for message in queryset:
                    notifier = CustomUser.objects.get(pk=message.notifier_id)
                    phone = notifier.phone
                    client.publish(PhoneNumber=phone, Message=notification.content_text)

                logger.info("Enabled SMS Notification")
            except Exception as e:
                logger.error("Unexpected error: %s" % e)
                return Response("INVAILD SNS CLIENT", status=status.HTTP_401_UNAUTHORIZED)

        # Email Notification
        if notification.is_email_message:
            # AWS SNS Topic
            topic = sns.Topic(third_party_keys["SNS_TOPIC_ARN"])
            topic.publish(
                Message=message.content_text,
                Subject='iBet Notification',
            )
            logger.info("Enabled Email Notification")

        try:
            Notification.objects.filter(pk=notification_id).update(status=MESSAGE_APPROVED)
            logger.info('create notification message')
            return HttpResponseRedirect(reverse('xadmin:notification'))
        except Exception as e:
            logger.error("Audit message error")
            return HttpResponse(e)


# User Group related views
class MessageUserGroupView(CommAdminView):
    def get(self, request, *arg, **kwargs):
        getType = request.GET.get('type')
        if getType == "get_member_info":
            groupName = request.GET.get('group_name')

            group = UserGroup.objects.get(name=groupName, groupType=MESSAGE_GROUP)
            allUsers = UserToUserGroup.objects.filter(group=group)

            users = []
            for i in allUsers:
                data = {
                    "id": i.user.pk,
                    "username": i.user.username
                }
                users.append(data)

            return HttpResponse(json.dumps(users), content_type='application/json')

        else:
            pageSize = request.GET.get('pageSize')
            offset = request.GET.get('offset')

            if pageSize is None:
                pageSize = 20
            else: 
                pageSize = int(pageSize)

            if offset is None or int(offset) < 1:
                offset = 1
            else:
                offset = int(offset)

            context = super().get_context()
            title = 'message'
            context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
            context["title"] = title
            context['time'] = timezone.now()
            context['imagePath'] = PUBLIC_S3_BUCKET + 'admin_images/'
            
            context['users_count'] = CustomUser.objects.all().count()
            # queryset = CustomUser.objects.all()
            # user_list = []
            # for user in user_list:
            #     item = {}
            #     item["pk"] = user.pk
            #     item["username"] = user.username
            #     user_list.push(item)

            # context['user_list'] = user_list
            groups = UserGroup.objects.filter(groupType=MESSAGE_GROUP).order_by('-created_time')
            message_groups = []
            for group in groups:
                group_item = {}
                group_item['pk'] = group.pk
                group_item['name'] = group.name
                group_item['is_static'] = group.is_static
                group_item['is_player'] = group.is_player
                group_item['members'] = UserToUserGroup.objects.filter(group=group).count()
                group_item['time_used'] = group.time_used
                group_item['creator'] = group.creator
                group_item['created_time'] = group.created_time
                total_messages = 0
                read_messages = 0
                users = UserToUserGroup.objects.filter(group=group)
                # notifications = NotificationToGroup.objects.filter(group=group)
                # for notification in notifications:
                #     for user in users:
                #         total_messages += NotificationToUsers.objects.filter(Q(notification_id=notification)&Q(notifier_id=user)).count()
                #         read_messages += NotificationToUsers.objects.filter(Q(notification_id=notification)&Q(notifier_id=user)&Q(is_read=True)).count()

                # print(total_messages)
                # print(read_messages)

                message_groups.append(group_item)

            paginator = Paginator(message_groups, pageSize)
            context['message_groups'] = paginator.get_page(offset)

            logger.info("GET MessageUserGroupView")

            return render(request, 'notification/group.html', context)

    def post(self, request, *arg, **kwargs):
        try:
            postType = request.POST.get('type')

            if postType == "create_new_usergroup":
                group_name = request.POST.get('group_name')
                pk_list = request.POST.getlist('pk[]')
                product = request.POST.get("product")
                is_range = request.POST.get("is_range")
                active_from = request.POST.get("active_from")
                active_to = request.POST.get('active_to')
                register_from = request.POST.get('register_from')
                register_to = request.POST.get('register_to')
                is_deposit = request.POST.get('is_deposit')

                if is_range == "true":
                    is_range = True
                else:
                    is_range = False

                if isDateFormat(active_from):
                    active_from = datetime.datetime.strptime(active_from, "%m/%d/%Y").date()
                else:
                    active_from = None

                if isDateFormat(active_to):
                    active_to = datetime.datetime.strptime(active_to, "%m/%d/%Y").date()
                else:
                    active_to = None

                if isDateFormat(register_from):
                    register_from = datetime.datetime.strptime(register_from, "%m/%d/%Y").date()
                else:
                    register_from = None

                if isDateFormat(register_to):
                    register_to = datetime.datetime.strptime(register_to, "%m/%d/%Y").date()
                else:
                    register_to = None

                if is_deposit == "true":
                    is_deposit = True
                else:
                    is_deposit = False

                data = {
                    "name": group_name,
                    "groupType": MESSAGE_GROUP,
                    "creator": self.user.pk,
                    "is_range": is_range,
                    "product": product,
                    "active_from": active_from,
                    "active_to": active_to,
                    "register_from": register_from,
                    "register_to": register_to,
                    "is_deposit": is_deposit
                }

                serializer = MessageUserGroupSerializer(data=data)
                if serializer.is_valid():
                    with transaction.atomic():
                        group = serializer.save()
                        logger.info("saved message user group")
                        for pk in pk_list:
                            user = CustomUser.objects.get(pk=int(pk))
                            log = UserToUserGroup.objects.create(group=group, user=user)
                            
                        logger.info("saved message user group log")
                        return HttpResponseRedirect(reverse('xadmin:messagegroups'))
                else:
                    logger.error(serializer.errors['name'][0])
                    return HttpResponse(json.dumps({ "error": serializer.errors['name'][0], "errorCode": 1}), content_type='application/json')
            
            elif postType == "player":
                group_name = request.POST.get('group_name')
                user_list = request.POST.get('user_list')
                user_list = json.loads(user_list)

                data = {
                    "name": group_name,
                    "groupType": MESSAGE_GROUP,
                    "creator": self.user.pk,
                    "is_static": True,
                    "is_player": True,
                }

                serializer = MessageUserGroupSerializer(data=data)

                if serializer.is_valid():
                    with transaction.atomic():
                        group = serializer.save()
                        logger.info("saved message user group")
                        for user in user_list:
                            user = CustomUser.objects.get(pk=int(user['id']))
                            UserToUserGroup.objects.create(group=group, user=user)
                        
                        logger.info("saved message user group log")
                        return HttpResponseRedirect(reverse('xadmin:messagegroups'))
                else:
                    return HttpResponse(status=400)

            elif postType == "affiliate":
                group_name = request.POST.get('group_name')
                user_list = request.POST.get('user_list')
                user_list = json.loads(user_list)

                data = {
                    "name": group_name,
                    "groupType": MESSAGE_GROUP,
                    "creator": self.user.pk,
                    "is_static": True,
                    "is_player": False
                }

                serializer = MessageUserGroupSerializer(data=data)

                if serializer.is_valid():
                    with transaction.atomic():
                        group = serializer.save()
                        logger.info("saved message user group")
                        for user in user_list:
                            user = CustomUser.objects.get(pk=int(user['id']))
                            UserToUserGroup.objects.create(group=group, user=user)
                        
                        logger.info("saved message user group log")
                        return HttpResponseRedirect(reverse('xadmin:messagegroups'))
                else:
                    return HttpResponse(status=400)

            elif postType == "delete_group":
                group_name = request.POST.get('group_name')
                UserGroup.objects.filter(Q(name=group_name)&Q(groupType=MESSAGE_GROUP)).delete()
                logger.info("Deleted group: '{0}'".format(group_name))
                return HttpResponse("success delete", status=200)

        except Exception as e:
            logger.error("Group Error: '{0}'".format(repr(e)))
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


class StaticGroupValidationAPI(View):
    def get(self, request, *args, **kwargs):
        try:
            group_type = request.GET.get("type")
            valid_players = []
            players = request.GET.get("players")
            players = json.loads(players)
            if group_type == "player":
                for player in players:
                    if player[0].isnumeric():
                        player = CustomUser.objects.filter(Q(pk=player[0])&Q(username=player[1]))
                        if len(player) > 0:
                            valid_player = {}
                            valid_player["id"] = player[0].pk
                            valid_player["username"] = player[0].username
                            valid_players.append(valid_player)
                    else:
                        return HttpResponse("invalid")
            else:
                for player in players:
                    if player[0].isnumeric():
                        affiliate = CustomUser.objects.filter(Q(pk=player[0])&Q(username=player[1])&Q(user_to_affiliate_time__isnull=False))
                        if len(affiliate) > 0:
                            valid_player = {}
                            valid_player["id"] = affiliate[0].pk
                            valid_player["username"] = affiliate[0].username
                            valid_players.append(valid_player)
                    else:
                        return HttpResponse("invalid")

            return HttpResponse(json.dumps(valid_players), content_type='application/json')
        except Exception as e:
            logger.error("CSV Format Invalid Error:", repr(e))
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


class MessageGroupDetailAPI(View):
    def get(self, request, *arg, **kwargs):
        group_id = request.GET.get('groupId')
        group = UserGroup.objects.get(pk=group_id)

        group_users = UserToUserGroup.objects.filter(group=group)

        response = {}
        
        response["group"] = serializers.serialize('json', [group,])

        user_list = []
        for utog in group_users:
            item = {}
            item["pk"] = utog.user.pk
            item["username"] = utog.user.username
            user_list.append(item)

        response["user_list"] = user_list

        return HttpResponse(json.dumps(response), content_type='application/json', status=200)


class UserIsValidAPI(View):
    def get(self, request, *args, **kwargs):
        username = request.GET.get("username")
        user = get_object_or_404(CustomUser, username=username)
        return HttpResponse(status=200)


# Campaign 
class CampaignView(CommAdminView):
    def get(self, request, *arg, **kwargs):
        getType = request.GET.get('type')
        if getType == 'view_campaign':
            campaignName = request.GET.get('campaignName')
            campaigns = Campaign.objects.get(name=campaignName)
            campaignToGroup = CampaignToGroup.objects.filter(campaign=campaigns)
            groups = []
            for group in campaignToGroup:
                groupData = {
                    "group": group.group.name,
                    "id": group.group.pk
                }
                groups.append(groupData)

            
            # ids = []
            # for i in campaigns:
            #     groups.append(i.group.name)
            #     ids.append(i.pk)
            
            data = {
                "name": campaignName,
                "group": groups,
                "campaignId": campaigns.pk
            }

            return HttpResponse(json.dumps(data), content_type='application/json')

        elif getType == 'get_all_group':
            data = []
            groups = UserGroup.objects.filter(groupType=MESSAGE_GROUP)
            for i in groups:
                groupData = {
                    'id': i.pk,
                    'name': i.name
                }
                data.append(groupData)
            return HttpResponse(json.dumps(data), content_type='application/json')
        
        elif getType == 'view_campaign_info':
            campaignId = request.GET.get('campaignId')
            camp = Campaign.objects.get(pk=campaignId)
            res = {
                "campaignName": camp.name,
                "campaignCreator": camp.creator.username,
                "campaignCreatedTime": camp.create_on,
            }
            groups = []
            campGroups = CampaignToGroup.objects.filter(campaign=camp)
            for i in campGroups:
                groups.append(i.group.name)
            res["groups"] = groups

            notificationArr = Notification.objects.filter(campaign=camp)
            sentUser = 0
            openMsg = 0
            for i in notificationArr:
                query = NotificationToUsers.objects.filter(notification_id=i)
                sentUser += query.count()
                openMsg += query.filter(is_read=True).count()

            res["sent_count"] = sentUser
            res["message_open"] = openMsg

            if sentUser == 0:
                res["open_rate"] = "0 %"
            else:
                res["open_rate"] = str((openMsg / sentUser) * 100) + '%'

            # print(res)
            return JsonResponse(res)


        else:
            pageSize = request.GET.get('pageSize')
            offset = request.GET.get('offset')

            if pageSize is None:
                pageSize = 20
            else: 
                pageSize = int(pageSize)

            if offset is None or int(offset) < 1:
                offset = 1
            else:
                offset = int(offset)

            context = super().get_context()
            title = 'message'
            context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
            context["title"] = title
            context['time'] = timezone.now()
            context['imagePath'] = PUBLIC_S3_BUCKET + 'admin_images/'
            campaigns = []
            campaigns = Campaign.objects.all()
            # print(campaigns)
            campaign_data = []
            for campaign in campaigns:
                campaign_item = {}
                campaign_item['pk'] = campaign.pk
                campaign_item['name'] = campaign.name
                campaign_item['creator'] = campaign.creator
                campaign_item['created_time'] = campaign.create_on
                groupPerCamp = CampaignToGroup.objects.filter(campaign=campaign)
                # print(groupPerCamp)
                campaign_item['groups'] = []
                for i in groupPerCamp:
                    campaign_item['groups'].append(i.group.name)
                # allCampaign = Campaign.objects.filter(name=campaign.name)
                # for i in allCampaign:
                #     campaign_item['groups'].append(i.group.name)
                campaign_data.append(campaign_item)
                messages = Notification.objects.filter(campaign=campaign)
                campaign_item['messages'] =  messages.count()
                sentUser = 0
                for i in messages:
                    sentUser += NotificationToUsers.objects.filter(notification_id=i).count()
                campaign_item['sent_count']= sentUser
                
            paginator = Paginator(campaign_data, pageSize)
            context['campaigns'] = paginator.get_page(offset)

            logger.info("GET CampaignView")

            return render(request, 'notification/campaign.html', context)


    def post(self, request, *arg, **kwargs):
        postType = request.POST.get('type')

        try:
            if postType == "create_new_campaign":
                campaignName = request.POST.get('campaign_name')
                groups = request.POST.get('tags')
                groups = json.loads(groups)
                creator = CustomUser.objects.get(username=self.user.username)
                objs = []

                with transaction.atomic():
                    campaign = Campaign.objects.create(name=campaignName, creator=creator)
                    # print(groups)
                    for groupName in groups:
                        group = UserGroup.objects.get(name=groupName, groupType=MESSAGE_GROUP)
                        CampaignToGroup.objects.create(campaign=campaign, group=group)

                    return HttpResponse("success")
            
            elif postType == "delete_campaign":
                campaignName = request.POST.get('campaignName')
                Campaign.objects.filter(name=campaignName).delete()
                return HttpResponse("success delete")

            elif postType == "update_campaign":
                campaignName = request.POST.get('campaign_name')
                groups = request.POST.get('tags')
                campaignId = request.POST.get('id')
                groups = json.loads(groups)

                with transaction.atomic():
                    camp = Campaign.objects.get(pk=campaignId)
                    camp.name = campaignName
                    camp.save()

                    CampaignToGroup.objects.filter(campaign=camp).delete()

                    for groupName in groups:
                        group = UserGroup.objects.get(name=groupName, groupType=MESSAGE_GROUP)
                        # print(group)
                        CampaignToGroup.objects.create(campaign=camp, group=group)
                
                    # oldIds = []
                    # oldCampaignName = Campaign.objects.get(pk=ids[0])
                    # oldIds.append(Campaign.objects.filter(name=oldCampaignName).pk)
                    # CampaignToGroup.objects.filter()
                    # for i in ids:
                    #     campaign = Campaign.objects.get(pk=i)
                    #     if campaign.group.name in groups:
                    #         campaign.name = campaignName
                    #         campaign.save()
                    #     else:
                    #         campaign.delete()

                    return HttpResponse("success update")
        except Exception as e:
            logger.error("Admin Campaign View Error -- {}".format(repr(e))))
            return HttpResponse(status=400)


class AWSTopicView(CommAdminView):
    def get(self, request, *arg, **kwargs):
        context = super().get_context()
        title = 'message'
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context["title"] = title
        context['time'] = timezone.now()
        context['current_user'] = self.user
        context['users'] = CustomUser.objects.all()
        queryset = AWSTopic.objects.all()
        context['queryset'] = queryset
        logger.info("GET AWSTopicView")
        return render(request, 'notification/group.html', context)

    def post(self, request, *arg, **kwargs):
        topic_name = request.POST.get('topic_name')
        # valid_until = request.POST.get('valid_until')
        group_usrs = request.POST.getlist('usrs')
        
        # create AWS Topic
        third_party_keys = getThirdPartyKeys("ibet-admin-dev", "config/sns.json")
        client = getAWSClient("sns", third_party_keys, AWS_SMS_REGION)
        topicArn = client.create_topic(Name=topic_name)
        topic_arn = topicArn["TopicArn"]

        for usrs in group_usrs:
            subscriber = CustomUser.objects.get(pk=usrs)
            client.subscribe(
                TopicArn=topic_arn,
                Protocol="Email",
                Endpoint=subscriber.email
            )

        data = {
            "topic_name": topic_name,
            "topic_arn": topic_arn,
            "valid_until": request.POST.get('valid'),
            "creator": self.user.pk
        }

        serializer = AWSTopicSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return HttpResponseRedirect(reverse('xadmin:awstopic'))
        else:
            logger.error(serializer.errors)
            return HttpResponse(serializer.errors)


# Operation Apps API Views
class NotificationAPIView(GenericAPIView):
    lookup_field = 'pk'
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        return Notification.objects.all()
    
    def get(self, request, *arg, **kwargs):
        queryset = self.get_queryset()
        serializer = NotificationSerializer(queryset, many=True)
   
        return Response(serializer.data)

    def post(self, request, *arg, **kwargs):
        data = {
            "subject": request.POST.get('subject'),
            "content_text": request.POST.get('content_text'),
            "creator": self.user.id,
            "auditor": request.POST.get('auditor'),
            "notification_method": request.POST.get('noteification_method'),
            "notifiers": request.POST.get("notifiers"),
            "topic": request.POST.get("topic")
        }

        serializer = NotificationSerializer(data=data)

        try:
            if serializer.is_valid():
                with transaction.atomic():
                    notification = serializer.save()
                    logger.info("Save notification message")
                    # store notification data in NotificationLog
                    log = NotificationLog(notification_id=notification, actor_id=notification.notifiers, group_id = notification.topic)

                    log.save()
                    logger.info("Save notification log")
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.error("can not create notification message: ", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Notification Api Error -- {}".format(repr(e)))
            return Response(repr(e), status=status.HTTP_400_BAD_REQUEST)


class CreateNotificationAPIView(CreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *arg, **kwargs):
        data = {
            "campaign": request.POST.get('campaign'),
            "subject": request.POST.get('subject'),
            "content_text": request.POST.get('content_text'),
            "creator": request.POST.get('creator'),
            "is_direct_message": request.POST.get('is_direct_message'),
            "is_email_message": request.POST.get('is_email_message'),
            "is_sms_message":request.POST.get('is_sms_message'),
            "is_push_message": request.POST.get('is_push_message')
        }

        serializer = NotificationSerializer(data=data)

        if serializer.is_valid():
            notification = serializer.save()
            logger.info("Save notification message")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error("can not create notification message! ", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationDateFilterAPI(View):
    def get(self, request, *arg, **kwargs):
        start_date = request.GET.get('date')
        end_date = request.GET.get('date')

        queryset = Notification.objects.filter(date__range=[start_date, end_date])
        return HttpResponse(status=200)


class MessageGroupUserAPI(View):
    def get(self, request, *arg, **kwargs):
        product = request.GET.get('product')
        active = request.GET.get('active')
        active_from = request.GET.get('active_from')
        active_to = request.GET.get('active_to')
        register_from = request.GET.get('register_from')
        register_to = request.GET.get('register_to')
        vip = request.GET.getlist('vip[]')
        risk = request.GET.getlist('risk[]')

        # pageSize = request.GET.get('pageSize')
        # offset = request.GET.get('offset')

        # if pageSize is None:
        #     pageSize = 20
        # else: 
        #     pageSize = int(pageSize)

        # if offset is None or int(offset) < 1:
        #     offset = 1
        # else:
        #     offset = int(offset)

        group_filter = Q()
        if product != None:
            group_filter = group_filter & Q(product_attribute=product)

        if active.isdigit():
            end_date = timezone.now()
            start_date = end_date - timedelta(hours=24 * int(active))
            group_filter = group_filter & Q(last_betting_time__range=(start_date, end_date))

        if isDateFormat(active_from):
            current_tz = timezone.get_current_timezone()
            active_from = datetime.datetime.strptime(active_from, "%m/%d/%Y").astimezone(current_tz)
            group_filter = group_filter & Q(last_betting_time__gt=active_from)

        if isDateFormat(active_to):
            current_tz = timezone.get_current_timezone()
            active_to = datetime.datetime.strptime(active_to, "%m/%d/%Y").astimezone(current_tz)
            group_filter = group_filter & Q(last_betting_time__lt=active_to)

        if isDateFormat(register_from):
            current_tz = timezone.get_current_timezone()
            register_from = datetime.datetime.strptime(register_from, "%m/%d/%Y").astimezone(current_tz)
            group_filter = group_filter & Q(time_of_registration__gt=register_from)

        if isDateFormat(register_to):
            current_tz = timezone.get_current_timezone()
            register_to = datetime.datetime.strptime(register_to, "%m/%d/%Y").astimezone(current_tz)
            group_filter = group_filter & Q(time_of_registration__lt=register_to)

        if len(vip) > 0:
            if 'NORMAL' in vip:
                group_filter = group_filter & Q(last_betting_time__range=(start_date, end_date))

        if len(risk) > 0:
            if 'E1' in risk:
                group_filter = group_filter & Q(risk_level=RISK_LEVEL_E1)
            if 'E2' in risk:
                group_filter = group_filter & Q(risk_level=RISK_LEVEL_E2)
            if 'F' in risk:
                group_filter = group_filter & Q(risk_level=RISK_LEVEL_F)
        
        queryset = CustomUser.objects.filter(group_filter)

        response = {}
        user_count = CustomUser.objects.filter(group_filter).count()
        user_list = []
        pk_list = []

        for user in queryset:
            item = {}
            item["pk"] = user.pk
            pk_list.append(user.pk)
            item["username"] = user.username
            user_list.append(item)

        # paginator = Paginator(user_list, pageSize)
        # context["notifications"] = paginator.get_page(offset)

        response["user_count"] = user_count
        response["user"] = user_list
        response["pk_list"] = pk_list
        # return HttpResponse(response)
        return HttpResponse(json.dumps(response), content_type='application/json', status=200)


class MessageGroupUpdateAPI(View):
    def post(self, request, *arg, **kwargs):
        # group_id = self.kwargs.get('pk')
        group_id = request.POST.get('groupId')
        group = UserGroup.objects.get(pk=int(group_id))

        if group is None:
            logger.error("Can not find group with id:" + group_id)
            return HttpResponse(status=404)

        group_name = request.POST.get('group_name')

        if group_name != group.name:
            # exsit = get_object_or_404(UserGroup, name=group_name)
            # exsit = UserGroup.objects.get(name=group_name)
            if UserGroup.objects.filter(name=group_name, groupType=MESSAGE_GROUP):
                logger.error("group name already exists")
                return HttpResponse(json.dumps({ "error": "group name already exists", "errorCode": 1}), content_type='application/json')

        pk_list = request.POST.getlist('pk[]')
        product = request.POST.get("product")
        is_range = request.POST.get("is_range")
        active_from = request.POST.get("active_from")
        active_to = request.POST.get('active_to')
        register_from = request.POST.get('register_from')
        register_to = request.POST.get('register_to')
        is_deposit = request.POST.get('is_deposit')

        if is_range == "true":
            is_range = True
        else:
            is_range = False

        if isDateFormat(active_from):
            active_from = datetime.datetime.strptime(active_from, "%m/%d/%Y").date()
        else:
            active_from = None

        if isDateFormat(active_to):
            active_to = datetime.datetime.strptime(active_to, "%m/%d/%Y").date()
        else:
            active_to = None

        if isDateFormat(register_from):
            register_from = datetime.datetime.strptime(register_from, "%m/%d/%Y").date()
        else:
            register_from = None

        if isDateFormat(register_to):
            register_to = datetime.datetime.strptime(register_to, "%m/%d/%Y").date()
        else:
            register_to = None

        if is_deposit == "true":
            is_deposit = True
        else:
            is_deposit = False


        try:
            group.name = group_name
            group.is_range = is_range
            group.product = product
            group.active_from = active_from
            group.active_to = active_to
            group.register_from = register_from
            group.register_to = register_to
            group.is_deposit = is_deposit

            group.save()

            return HttpResponse(status=200)
        except Exception as e:
            logger.error(e)
            return HttpResponse(e, status=500)



class AWSTopicAPIView(GenericAPIView):
    lookup_field = 'pk'
    serializer_class = AWSTopicSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        return AWSTopic.objects.all()

    def get(self, request, *arg, **kwargs):
        queryset = self.get_queryset()
        serializer = AWSTopicSerializer(queryset, many=True)

        return Response(serializer.data)

    def post(self, request, *arg, **kwargs):
        topic_name = request.POST.get('topic_name')
        valid_until = request.POST.get('valid_until')

        serializer = AWSTopicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("saved awstopic")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_sms(content_text, notifier, phone_num):
    # connect AWS S3
    third_party_keys = getThirdPartyKeys("ibet-admin-dev", "config/sns.json")

    # AWS SNS Client
    sns = boto3.resource('sns', region_name=AWS_SMS_REGION)
    client = getAWSClient('sns', third_party_keys, AWS_SMS_REGION)

    try:
        # phone = str(notifier.phone)
        client.publish(PhoneNumber=phone_num, Message=content_text)

        logger.info("Enabled SMS Notification to: {}".format(phone_num))
    except Exception as e:
        logger.error("Unexpected error: %s" % e)

        # data = {
        #     "content_text": content_text,
        #     "is_sms_message": True,
        #     "status": MESSAGE_APPROVED,
        # }

        # serializer = NotificationSerializer(data=data)
        
        # if serializer.is_valid():
        #     notification = serializer.save()
        #     logger.info("create a SMS notification")

        #     notifier = CustomUser.objects.get(pk=notifier)

        #     log = NotificationToUsers(notification_id=notification, notifier_id=CustomUser.objects.get(pk=notifier.pk))

        #     logger.info("Save notification log")

        #     # connect AWS S3
        #     third_party_keys = getThirdPartyKeys("ibet-admin-dev", "config/sns.json")

        #     # AWS SNS Client
        #     sns = boto3.resource('sns', region_name=AWS_SMS_REGION)
        #     client = getAWSClient('sns', third_party_keys, AWS_SMS_REGION)

        #     try:
        #         # phone = str(notifier.phone)
        #         client.publish(PhoneNumber=phone_num, Message=notification.content_text)
    
        #         logger.info("Enabled SMS Notification")
        #     except Exception as e:
        #         logger.error("Unexpected error: %s" % e)
        #         return "AWS ERROR!"

        #     return "Success"
        # else:
        #     logger.error("Sending SMS Notification Data Format Incorrect Error!")
        #     return "Data Format Incorrect!"

'''
TODO: using AWS SES send email for ibet.com in the future. Currently not using this function
'''
@transaction.atomic
def send_email(subject, content_text, notifier):
        data = {
            "subject": subject,
            "content_text": content_text,
            "is_email_message": True,
            "status": MESSAGE_APPROVED,
        }

        serializer = NotificationSerializer(data=data)
        
        if serializer.is_valid():
            notification = serializer.save()
            # logger.info("create a Email notification")

            notifier = CustomUser.objects.get(username=notifier)

            # logger.info("Save notification log")

            try:
                # connect AWS S3
                third_party_keys = getThirdPartyKeys("ibet-admin-dev", "config/sns.json")

                # AWS SES Client
                # ses = boto3.resource('ses', region_name=AWS_SES_REGION)
                client = getAWSClient('ses', third_party_keys, AWS_SES_REGION)

                email = str(notifier.email)
                # client.publish(PhoneNumber=phone, Message=notification.content_text)
                # response = client.send_custom_verification_email(
                #     EmailAddress=email,
                #     TemplateName='EmailVerification'
                # )

                response = client.send_email(
                    Source='claymore@claymoreusa.com',
                    Destination={
                        'ToAddresses': [
                            email,
                        ],
                        'CcAddresses': [
                        ],
                        'BccAddresses': [
                        ]
                    },
                    Message={
                        'Subject': {
                            'Data': subject,
                            'Charset': 'utf-8'
                        },
                        'Body': {
                            'Text': {
                                'Data': content_text,
                                'Charset': 'utf-8'
                            },
                        }
                    }
                )

    
                logger.info("Enabled SES Notification")
            except Exception as e:
                logger.error(repr(e))
                return "AWS ERROR!"

            return "Success"
        else:
            logger.error("Sending Email Notification Data Format Incorrect Error!")
            return "Data Format Incorrect!"


class EmailNotificationTest(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        subject = data["subject"]
        content_text = data["content_text"]
        notifier = data["notifier"]
        send_email(subject, content_text, notifier)
        return HttpResponse(status=200)


class NotificationUserIsReadAPI(View):
    def post(self, request, *args, **kwargs):
        try:
            notification_to_user_id = self.kwargs.get('pk')
            message = NotificationToUsers.objects.get(pk=notification_to_user_id)
            if checkUserBlock(message.notifier_id):
                errorMessage = _('The current user is blocked!')
                data = {
                    "errorCode": ERROR_CODE_BLOCK,
                    "errorMsg": {
                        "detail": [errorMessage]
                    }
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type='application/json', status=200)

            message = NotificationToUsers.objects.get(pk=notification_to_user_id)
            if message.is_read:
                return HttpResponse(status=200)
            else:
                NotificationToUsers.objects.filter(pk=notification_to_user_id).update(is_read=True)
                return HttpResponse(status=201)

        except Exception as e:
            logger.error("reading message error:", repr(e))
            return HttpResponse(status=400)


class NotificationUserIsDeleteAPI(View):
    def post(self, request, *args, **kwargs):
        try:
            notification_to_user_id = self.kwargs.get('pk')
            message = NotificationToUsers.objects.get(pk=notification_to_user_id)
            if checkUserBlock(message.notifier_id):
                errorMessage = _('The current user is blocked!')
                data = {
                    "errorCode": ERROR_CODE_BLOCK,
                    "errorMsg": {
                        "detail": [errorMessage]
                    }
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type='application/json', status=200)
            
            message.is_deleted = True
            message.save()
            return HttpResponse(status=200)
            
        except Exception as e:
            logger.error("delete message error:", e)
            return HttpResponse(status=400)


class NotificationsForUserAPIView(View):
    def get(self, request, *args, **kwargs):
        notification_list = request.GET.get('notification_list')
        queryset = []
        for notification_id in notification_list:
            query = Notification.object.get(pk=notification_id)
            queryset.append(query)
        
        return Response(queryset)


class NotificationDetailAPIView(ListAPIView):
    queryset = ''
    permission_classes = [AllowAny, ]

    def get(self, request, *args, **kwargs):
        notification_id = self.kwargs.get('pk')
        queryset = Notification.objects.get(pk=notification_id)
        serializer = NotificationSerializer(queryset, many=False)

        return Response(serializer.data)


class NotificationLogView(ListAPIView):
    serializer_class = NotificationLogSerializer
    queryset = NotificationLog.objects.all()


class NotificationToUsersView(ListAPIView):
    serializer_class = NotificationToUsersSerializer
    queryset = NotificationToUsers.objects.all()


class NotificationToUsersDetailView(View):
    def get(self, request, *args, **kwargs):
        try:
            notifier_id = self.kwargs.get('pk')

            response = []
            # response['unread_list'] = []
            # response['read_list'] = []
            user = CustomUser.objects.get(pk=notifier_id)
            if checkUserBlock(user):
                errorMessage = _('The current user is blocked!')
                data = {
                    "errorCode": ERROR_CODE_BLOCK,
                    "errorMsg": {
                        "detail": [errorMessage]
                    }
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type='application/json', status=200)
            
            message_list = NotificationToUsers.objects.filter(Q(notifier_id=notifier_id)&Q(is_deleted=False)).order_by('-pk')

            for msg in message_list:
                notification = Notification.objects.get(pk=msg.notification_id.pk)
                message = {}
                message["pk"] = msg.pk
                message["subject"] = notification.subject
                message["content"] = notification.content_text
                publish_on_str = ''
                if notification.publish_on:
                    current_tz = timezone.get_current_timezone()
                    publish_time = notification.publish_on.astimezone(current_tz)
                    publish_on_str = notification.publish_on.astimezone(current_tz).strftime("%b %d, %Y")
                message["publish_on"] = publish_on_str
                message["is_read"] = msg.is_read
                message["is_deleted"] = False
                response.append(message)

            # logger.info('user: ', notifier_id, 'received messages: ',  json.dumps(response))
            return HttpResponse(json.dumps(response), content_type='application/json', status=200)
        except Exception as e:
            logger.error("delete message error:", repr(e))
            return HttpResponse(status=400)


class NotificationToUsersUnreadCountView(ListAPIView):
    permission_classes = [AllowAny, ]

    def get(self, request, *args, **kwargs):
        notifier_id = self.kwargs.get('pk')
        count = NotificationToUsers.objects.filter(Q(notifier_id=notifier_id)&Q(is_read=False)&Q(is_deleted=False)).count()

        return Response(count)


class UserToAWSTopicView(ListAPIView):
    serializer_class = UserToAWSTopicSerializer
    queryset = UserToAWSTopic.objects.all()


        