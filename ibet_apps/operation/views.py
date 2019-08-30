from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.db.models import Q
from django.views import View
from django.core import serializers
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import status
from rest_framework.test import APIRequestFactory
import boto3
import json
import logging

from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from .serializers import AWSTopicSerializer, NotificationSerializer, NotificationLogSerializer, NotificationToUsersSerializer, UserToAWSTopicSerializer
from .models import AWSTopic, Notification, NotificationLog, NotificationToUsers, UserToAWSTopic
from users.models import CustomUser
from xadmin.views import CommAdminView
from utils.constants import *
from utils.aws_helper import getThirdPartyKeys, getAWSClient

logger = logging.getLogger('django')


def send_message(notification_id):
    notification = Notification.objects.get(pk=notification_id)
    # All messages
    queryset = NotificationToUsers.objects.filter(notification_id=notification_id)

    # connect AWS S3
    third_party_keys = getThirdPartyKeys("ibet-admin-dev", "config/sns.json")

    # AWS SNS Client
    sns = boto3.resource('sns')
    client = getAWSClient('sns', third_party_keys)

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
        if NOTIFICATION_EMAIL in notification_methods:
            # AWS SNS Topic
            topic = sns.Topic(third_party_keys["SNS_TOPIC_ARN"])
            topic.publish(
                Message=message.content_text,
                Subject='iBet Notification',
            )
            logger.info("Enabled Email Notification")

        Notification.objects.filter(pk=notification_id).update(status=MESSAGE_APPROVED)
        logger.info('create notification message')
        # return HttpResponseRedirect(reverse('xadmin:notification'))
    else:
        logger.error("Sending Message API error!:")
        return HttpResponse("Can not send Message!")


'''
class createMessage(View):
    self, subject, content, creator, notifiers, groups, is_direct=False, is_sms=False, is_email=False, is_push=False
    # create Notification Object
    message = {
        "subject": request.POST.get('subject'),
        "content_text": request.POST.get('content_text'),
        "creator": self.user,
        "notifiers": request.POST.getlist('notifiers'),
        "groups": request.POST.getlist('notifiers'),
    }

    notification_serializer = NotificationSerializer(data=message)

    if serializer.is_valid():
        notification = serializer.save()
        logger.info("create a notification")
        return HttpResponse(json.dumps(response), content_type='application/json')
    else:
        return 


    # n_user_serializer = NotificationToUsersSerializer()
    for notifier in notifiers:
        log = NotificationToUsers(notification_id=notification.pk, notifier_id=notifier.pk)

    logger.info("added notification-to-users log")

    '''
class NotificationSearchAutocomplete(View):
    def get(self, request, *args, **kwargs):
        search = request.GET.get('search')
        block = request.GET.get('block')

        logger.info('Search notification, key: ' + search)

        search_subject = Notification.objects.filter(Q(subject__contains=search)&Q(status=block))
        # search_body = Notification.objects.filter(content_text__contains=search)

        search_subject = serializers.serialize('json', search_subject)
        # search_body = serializers.serialize('json', search_body)

        search_subject = json.loads(search_subject)
        # search_body = json.loads(search_body)

        response = {}

        subject_data = []
        for notification in search_subject:
            notificationMap = {}
            notificationMap["subject"] = notification["fields"]["subject"]
            subject_data.append(notificationMap)
        response["subject"] = subject_data

        # body_data = []
        # for notification in search_body:
        #     notificationMap = {}
        #     notificationMap['body'] = notification['body']
        #     body_data.append(notificationMap)
        # response['body'] = body_data

        logger.info('Search response: ' + json.dumps(response))
        return HttpResponse(json.dumps(response), content_type='application/json')


class NotificationView(CommAdminView):
    lookup_field = 'pk'
    serializer_class = NotificationSerializer

    def get(self, request, *arg, **kwargs):
        search = request.GET.get('search')
        pageSize = request.GET.get('pageSize')
        offset = request.GET.get('offset')
        block = request.GET.get('block')

        if pageSize is None:
            pageSize = 20
        else: 
            pageSize = int(pageSize)

        if offset is None:
            offset = 1
        else:
            offset = int(offset)

        if block is None:
            block = MESSAGE_APPROVED
        else:
            block = int(block)

        # set context
        context = super().get_context()
        title = 'message'
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context["title"] = title
        context['time'] = timezone.now()

        context['all_user'] = CustomUser.objects.all()
        context['waiting_list'] = Notification.objects.filter(auditor=self.user.pk).count()
        if search:
            logger.info('Search notification, key: ' + search)
            queryset = Notification.objects.filter(Q(subject__contains=search)&Q(status=block))
        else:
            queryset = Notification.objects.filter(status=block)

        notification_list = []
        for msg in queryset:
            notification_item = {}
            notification_item['pk'] = msg.pk
            notification_item['subject'] = msg.subject
            notification_item['campaign'] = msg.campaign
            notification_item["creator"] = msg.creator
            notification_item["publish_on"] = msg.publish_on
            notification_item["status"] = msg.status
            notifiers = NotificationToUsers.objects.filter(notification_id=msg.pk)
            if len(notifiers) > 1:
                notification_item["notifiers"] = len(notifiers)
            else:
                notification_item["notifiers"] = notifiers
            notification_item["sent_count"] = NotificationToUsers.objects.filter(notification_id=msg.pk).count()

            notification_list.append(notification_item)

        paginator = Paginator(notification_list, pageSize)
        context["notifications"] = paginator.get_page(offset)

        # auto_messages = Notification.objects.all()
        # paginator = Paginator(auto_messages, pageSize)
        # context['auto_messages'] = paginator.get_page(page)

        # drafts = Notification.objects.filter(status=MESSAGE_PENDING)
        # context["drafts"] = drafts

        # serializer = NotificationSerializer(queryset, many=True)

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

        notification_method = ""

        if direct_check != None:
            data["is_direct_message"] = True

        if email_check != None:
            data["is_email_message"] = True

        if SMS_check != None:
            data["is_sms_message"] = True

        if push_check != None:
            data["is_push_message"] = True

        notifiers = request.POST.getlist("notifiers")

        if len(notifiers) < 2:
            data["status"] = MESSAGE_APPROVED

        serializer = NotificationSerializer(data=data)

        if serializer.is_valid():           
            notification = serializer.save()
            logger.info("Save notification message")
            # store notification data in NotificationLog
            for notifier in notifiers:
                log = NotificationToUsers(notification_id=notification, notifier_id=CustomUser.objects.get(pk=notifier))
                log.save()
            logger.info("Save notification log")

            if(notification.status == MESSAGE_APPROVED):
                send_message(notification.pk)

            return HttpResponseRedirect(reverse('xadmin:notification'))
        else:
            logger.error(serializer.errors)
            return HttpResponse(serializer.errors)


class NotificationDetailView(CommAdminView):
    def get(self, request, *args, **kwargs):
        notification_id = self.kwargs.get('pk')
        context = super().get_context()
        title = 'message'
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context["title"] = title
        context['time'] = timezone.now()
        context['current_user'] = self.user
        context['all_user'] = CustomUser.objects.all()
        # context['auditors'] = CustomUser.objects.filter(is_admin=True)
        # context['topics'] = AWSTopic.objects.all()
        
        queryset = Notification.objects.get(pk=notification_id)

        serializer = NotificationSerializer(queryset, many=False)
        context["queryset"] = queryset

        try:
            logger.info("GET NotificationDetailView")
            return render(request, 'notification/detail.html', context)
        except:
            logger.error("can not reach notification detail")


class AuditNotificationView(CommAdminView):
    lookup_field = 'pk'
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny, ]

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
        sns = boto3.resource('sns')
        client = getAWSClient('sns', third_party_keys)

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


class AWSTopicView(CommAdminView):
    lookup_field = 'pk'
    serializer_class = AWSTopicSerializer

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
        client = getAWSClient("sns", third_party_keys)
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

        if serializer.is_valid():
            notification = serializer.save()
            logger.info("Save notification message")
            # store notification data in NotificationLog
            log = NotificationLog(notification_id=notification, actor_id=notification.notifiers, group_id = notification.topic)

            log.save()
            logger.info("Save notification log")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error("can not create notification message! " + serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateNotificationAPIView(CreateAPIView):
    lookup_field = 'pk'
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *arg, **kwargs):
        data = {
            "campaign": request.POST.get('campaign'),
            "subject": request.POST.get('subject'),
            "content_text": request.POST.get('content_text'),
            "creator": request.POST.get('creator'),
            "auditor": request.POST.get('auditor'),
            "notification_method": request.POST.get("notification_method"),
            "notifiers": request.POST.get("notifiers"),
            "topic": request.POST.get("topic")
        }

        serializer = NotificationSerializer(data=data)
        notification_methods = data["notification_method"]

        if serializer.is_valid():
            notification = serializer.save()
            logger.info("Save notification message")
            # store notification data in NotificationLog
            log = NotificationLog(notification_id=notification, actor_id=notification.notifiers, group_id = notification.topic)

            log.save()
            logger.info("Save notification log")

            if notification_methods != None:
                # connect AWS S3
                third_party_keys = getThirdPartyKeys("ibet-admin-dev", "config/sns.json")

                # AWS SNS Client
                sns = boto3.resource('sns')
                client = getAWSClient('sns', third_party_keys)

                # Push Notification
                if NOTIFICATION_PUSH in notification_methods:
                    platform_endpoint = sns.PlatformEndpoint(third_party_keys["SNS_PLATFORM_ENDPOINT_ARN"])
                    
                    platform_endpoint.publish(
                        Message=notification.content_text,
                    )
                    logger.info("Enabled Push Notification")
                
                # SMS Notification
                if NOTIFICATION_SMS in notification_methods:
                    try:
                        notifier = CustomUser.objects.get(pk=notification.notifiers.pk)
                        phone = notifier.phone
                        client.publish(PhoneNumber=phone, Message=notification.content_text)
                        logger.info("Enabled SMS Notification")
                    except Exception as e:
                        logger.error("Unexpected error: %s" % e)
                        return Response("INVAILD SNS CLIENT", status=status.HTTP_401_UNAUTHORIZED)

                # Email Notification
                if NOTIFICATION_EMAIL in notification_methods:
                    # AWS SNS Topic
                    topic = sns.Topic(third_party_keys["SNS_TOPIC_ARN"])
                    topic.publish(
                        Message=notification.content_text,
                        Subject='iBet Notification',
                    )
                    logger.info("Enabled Email Notification")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error("can not create notification message! " + serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationLogView(ListAPIView):
    serializer_class = NotificationLogSerializer
    queryset = NotificationLog.objects.all()


class NotificationToUsersView(ListAPIView):
    serializer_class = NotificationToUsersSerializer
    queryset = NotificationToUsers.objects.all()


class UserToAWSTopicView(ListAPIView):
    serializer_class = UserToAWSTopicSerializer
    queryset = UserToAWSTopic.objects.all()