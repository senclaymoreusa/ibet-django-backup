from rest_framework import serializers, exceptions
from .models import NoticeMessage, Notification, NotificationLog, NotificationUsers


class LanguageCodeSerializer(serializers.Serializer):
    languageCode = serializers.CharField()


class NoticeMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeMessage
        fields = ('pk', 'start_time', 'end_time', 'message', 'message_zh', 'message_fr')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('pk',  'content', 'notification_choice', 'notification_type', 'notification_method', 'notifiers', 'create_on', 'publish_on')
        read_only_fields = ['pk', 'publish_on']


'''
class NotificationSerializer(serializers.Serializer):
    content = serializers.CharField(required=True)
    
    def create(self, validated_data):
        return Notification.objects.get_or_create(**validated_data)
'''

class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog


class NotificationUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationUsers