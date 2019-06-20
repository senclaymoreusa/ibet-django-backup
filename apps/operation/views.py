from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import status
import boto3
import json

from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from .serializers import NoticeMessageSerializer, NotificationSerializer
from .models import NoticeMessage, Notification
from users.models import CustomUser

# from drf_model_pusher.views import ModelPusherViewMixin


class NoticeMessageView(ListAPIView):
    serializer_class = NoticeMessageSerializer
    # push_notify()
    queryset = NoticeMessage.objects.all()
    
    '''
    class PushNoticeMessageView(ListAPIView):
        serializer_class = NoticeMessageSerializer
        queryset = PushNoticeMessage.objects.all()

    def push_notify(self):
        from pusher_push_notifications import PushNotifications

        pn_client = PushNotifications(
            instance_id='',
            secret_key='',
        )

        #msg = NoticeMessage.objects.all() # SELECT * FROM NoticeMessage
        start_time = NoticeMessage.objects.get(pk=1).start_time
        end_time = NoticeMessage.objects.get(pk=1).end_time
        message = NoticeMessage.objects.get(pk=1).message

        response = pn_client.publish_to_interests(
            interests=['hello'],
            publish_body={
                'apns': {
                    'aps': {
                        'alert': 'Hello!'
                    }
                },
                'fcm': {
                    'notification': {
                        'title': str(message),
                        'body': 'Start Time: ' + str(start_time) + 'End Time: ' + str(end_time)
                    }
                }
            }
        )
        
        print(response['publishId'])

    def get_queryset(self):
        self.push_notify()
        return NoticeMessage.objects.all()
    '''

'''
class NotificationView(ListAPIView):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
'''


class NotificationView(GenericAPIView):
    lookup_field = 'pk'
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny, ]
    # queryset = Notification.objects.all()

    def get_queryset(self):
        return Notification.objects.all()

    def get(self, request, *arg, **kwargs):
        queryset = self.get_queryset()
        serializer = NotificationSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *arg, **kwargs):
        serializer = NotificationSerializer(data=request.data)
        content = self.request.POST['content']
        notification_choice = self.request.POST['notification_choice']
        notification_method = self.request.POST['notification_method']
        notifiers = self.request.POST['notifiers']


        if serializer.is_valid():
            client = boto3.client('sns', 'us-west-2')
            # if notification_choice == 'B':
            #     notifiers = CustomUser.objects.all()
            #     for notifier in notifiers:
            #         print(notifier.phone)
            #         client.publish(PhoneNumber=notifier.phone, Message=content)
            if notification_method == 'P':
                pass

            if notification_method == 'S':
                # AWS SNS Client
                notifier = CustomUser.objects.get(pk=notifiers)
                phone = notifier.phone
                print(phone)
                # client.publish(PhoneNumber=Notification.notifiers.objects.get('phone')))
                client.publish(PhoneNumber=phone, Message=content)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)