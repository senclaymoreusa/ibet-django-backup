from rest_framework import serializers, exceptions
from .models import NoticeMessage, Notification, NotificationLog, NotificationUsers

from drf_model_pusher.backends import PusherBackend

class LanguageCodeSerializer(serializers.Serializer):
    languageCode = serializers.CharField()


class NoticeMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeMessage
        fields = ('pk', 'start_time', 'end_time', 'message', 'message_zh', 'message_fr')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('pk', 'content', 'create_on', 'publish_on')


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog


class NotificationUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationUsers