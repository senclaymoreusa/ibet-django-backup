from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import status
from rest_framework.test import APIRequestFactory
import boto3
import json

from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from .serializers import AWSTopicSerializer, NoticeMessageSerializer, NotificationSerializer, NotificationLogSerializer, NotificationUsersSerializer, UserToAWSTopicSerializer
from .models import AWSTopic, NoticeMessage, Notification, NotificationLog, NotificationUsers, UserToAWSTopic
from users.models import CustomUser
# from djauth import third_party_keys
from xadmin.views import CommAdminView
from django.utils import timezone


def getThirdPartyKeys(bucket, file):
    s3client = boto3.client("s3")
    try:
        config_obj = s3client.get_object(Bucket=bucket, Key=file)
        config = json.loads(config_obj['Body'].read())
    except ClientError as e:
        logger.error(e)
        return None
    except NoCredentialsError as e:
        logger.error(e)
        return None
    
    return config


class NoticeMessageView(ListAPIView):
    serializer_class = NoticeMessageSerializer
    queryset = NoticeMessage.objects.all()


class NotificationAPIView(GenericAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny, ]

    def get(self):
        queryset = Notification.objects.all()

    '''
    def post(self, request, *arg, **kwargs):
        subject = request.POST.get('subject')
        content_text = self.request.POST['content_text']
        notification_choice = self.request.POST['notification_choice']
        notification_method = self.request.POST['notification_method']
        topic = request.POST.get('topic')
        notifiers = self.request.POST['notifiers']

        serializer = NotificationSerializer(data=request.data)

        if serializer.is_valid():            
            # AWS SNS Client
            sns = boto3.resource('sns')
            # client = boto3.client('sns', 'us-west-2')
            client = boto3.client(
                'sns',
                aws_access_key_id = third_party_keys.AWS_ACCESS_KEY_ID,
                aws_secret_access_key = third_party_keys.AWS_SECRET_ACCESS_KEY,
                # region_name = third_party_keys.AWS_REGION_NAME
            )

            # Broadcast
            if notification_choice == 'B':
                notifiers = CustomUser.objects.all()

            if notification_choice == 'M':
                if(topic is not None):
                    aws_topic = AWSTopic.objects.get(pk=topic)
                    aws_topic = sns.Topic(aws_topic.topic_arn)
                    aws_topic.publish(
                        Message=content_text,
                        Subject=subject,
                    )

            # Push Notification
            if notification_method == 'P':
                platform_endpoint = sns.PlatformEndpoint(third_party_keys.SNS_PLATFORM_ENDPOINT_ARN)
                
                platform_endpoint.publish(
                    Message=content_text,
                )

            try:
                # SMS Notification
                if notification_method == 'S':
                    notifier = CustomUser.objects.get(pk=notifiers)
                    # for notifier in notifiers:
                    #     phone = notifier.phone
                    #     print(phone)
                    #     client.publish(PhoneNumber=phone, Message=content_text)
                    phone = notifier.phone
                    client.publish(PhoneNumber=phone, Message=content_text)
            except Exception as e:
                print("Unexpected error: %s" % e)
                return Response("INVAILD SNS CLIENT", status=status.HTTP_401_UNAUTHORIZED)

            # Email Notification
            if notification_method == 'E':
                # AWS SNS Topic
                topic = sns.Topic(third_party_keys.SNS_TOPIC_ARN)
                topic.publish(
                    Message=content_text,
                    Subject='iBet Notification',
                )

            notification = serializer.save()
            # store notification data in NotificationLog
            log = NotificationLog(notification_id=notification, actor_id=notification.notifiers, action='C')
            log.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    '''


class NotificationView(CommAdminView):
    lookup_field = 'pk'
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny, ]
    # queryset = Notification.objects.all()

    def get_queryset(self):
        return Notification.objects.all()

    def get(self, request, *arg, **kwargs):
        context = super().get_context()
        title = 'message'
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context["title"] = title
        context['time'] = timezone.now()
        context['current_user'] = self.user
        context['all_user'] = CustomUser.objects.all()
        context['auditors'] = CustomUser.objects.filter(is_admin=True)
        context['topics'] = AWSTopic.objects.all()
        queryset = Notification.objects.all()
        serializer = NotificationSerializer(queryset, many=True)
        context["queryset"] = queryset
        return render(request, 'notification/index.html', context)

    def put(self, request, *arg, **kwargs):
        return self.update(request, *arg, **kwargs)

    def post(self, request, *arg, **kwargs):
        subject = request.POST.get('subject')
        content_text = request.POST.get('content_text')
        creator = self.user
        auditor = request.POST.get('auditor')
        notification_choice = request.POST.get('notification_choice')
        notification_type = request.POST.get('notification_method')
        # topic = request.POST.get('topic')
        # notifiers = self.request.POST['notifiers']
        direct_check = request.POST.get('direct_check')
        email_check = request.POST.get('email_check')
        SMS_check = request.POST.get('SMS_check')
        push_check = request.POST.get('push_check')
        notification_method = [direct_check, email_check, SMS_check, push_check]

        print(str(subject))
        print(str(content_text))
        print(str(auditor))

        print(notification_method)

        third_party_keys = getThirdPartyKeys("ibet-admin-dev", "config/sns.json")
        print(third_party_keys)
        
        
        serializer = NotificationSerializer(data=request.data)

        if serializer.is_valid():
            # connect AWS S3
            third_party_keys = getThirdPartyKeys("ibet-admin-dev", "s3://ibet-admin-dev/config/sns.json")
            print(third_party_keys)

            # AWS SNS Client
            sns = boto3.resource('sns')
            # client = boto3.client('sns', 'us-west-2')
            client = boto3.client(
                'sns',
                aws_access_key_id = third_party_keys.AWS_ACCESS_KEY_ID,
                aws_secret_access_key = third_party_keys.AWS_SECRET_ACCESS_KEY,
                # region_name = third_party_keys.AWS_REGION_NAME
            )
            '''
            
            # Broadcast
            if notification_choice == 'B':
                notifiers = CustomUser.objects.all()

            if notification_choice == 'M':
                if(topic is not None):
                    aws_topic = AWSTopic.objects.get(pk=topic)
                    aws_topic = sns.Topic(aws_topic.topic_arn)
                    aws_topic.publish(
                        Message=content_text,
                        Subject=subject,
                    )
            # Push Notification
            if notification_method[0] is not None:
                # platform_endpoint = sns.PlatformEndpoint(third_party_keys.SNS_PLATFORM_ENDPOINT_ARN)
                
                # platform_endpoint.publish(
                #     Message=content_text,
                # )
                print("Direct Msg")
            try:
                # SMS Notification
                if notification_method == 'S':
                    notifier = CustomUser.objects.get(pk=notifiers)
                    # for notifier in notifiers:
                    #     phone = notifier.phone
                    #     print(phone)
                    #     client.publish(PhoneNumber=phone, Message=content_text)
                    phone = notifier.phone
                    client.publish(PhoneNumber=phone, Message=content_text)
            except Exception as e:
                print("Unexpected error: %s" % e)
                return Response("INVAILD SNS CLIENT", status=status.HTTP_401_UNAUTHORIZED)

            # Email Notification
            if notification_method == 'E':
                # AWS SNS Topic
                topic = sns.Topic(third_party_keys.SNS_TOPIC_ARN)
                topic.publish(
                    Message=content_text,
                    Subject='iBet Notification',
                )
            notification = serializer.save()
            # store notification data in NotificationLog
            log = NotificationLog(notification_id=notification, actor_id=notification.notifiers, action='C')
            log.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *arg, **kwargs):
        serializer = NotificationSerializer(queryset, many=True)
        queryset = Notification.object.get(pk=1)
    '''


class NotificationLogView(ListAPIView):
    serializer_class = NotificationLogSerializer
    queryset = NotificationLog.objects.all()


class NotificationUsersView(ListAPIView):
    serializer_class = NotificationUsersSerializer
    queryset = NotificationUsers.objects.all()


class AWSTopicView(GenericAPIView):
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


class UserToAWSTopicView(ListAPIView):
    serializer_class = UserToAWSTopicSerializer
    queryset = UserToAWSTopic.objects.all()