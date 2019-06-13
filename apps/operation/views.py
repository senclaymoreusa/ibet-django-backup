from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from .serializers import NoticeMessageSerializer, NotificationSerializer
from .models import NoticeMessage, Notification

from drf_model_pusher.views import ModelPusherViewMixin


class NoticeMessageView(ListAPIView):
    serializer_class = NoticeMessageSerializer
    # push_notify()
    # queryset = NoticeMessage.objects.all()

    '''
    class PushNoticeMessageView(ModelPusherViewMixin, ListAPIView):
        serializer_class = NoticeMessageSerializer
        queryset = PushNoticeMessage.objects.all()
    '''
    def push_notify(self):
        from pusher_push_notifications import PushNotifications

        pn_client = PushNotifications(
            instance_id='ef508469-c603-445e-bdfe-c0cd010f138d',
            secret_key='8E3BF7231A817D2870315B23C7E593428B54A1776DE749E96AEE90DD8326589D',
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


class NotificationView(ListAPIView):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
