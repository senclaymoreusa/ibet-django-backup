import boto3

from rest_framework import serializers, exceptions
from users.serializers import UserDetailsSerializer
from .models import AWSTopic, NoticeMessage, Notification, NotificationLog, NotificationUsers, UserToAWSTopic
# from .views import getThirdPartyKeys

class LanguageCodeSerializer(serializers.Serializer):
    languageCode = serializers.CharField()


class NoticeMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeMessage
        fields = ('pk', 'start_time', 'end_time', 'message', 'message_zh', 'message_fr')

'''
class AWSTopicSerializer(serializers.ModelSerializer):
    topic_name = serializers.CharField()
    
    def create(self, validated_data):
        # set up AWS
        sns = boto3.resource('sns')
        client = boto3.client(
            'sns',
            aws_access_key_id = third_party_keys.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = third_party_keys.AWS_SECRET_ACCESS_KEY,
            # region_name = third_party_keys.AWS_REGION_NAME
        )
        topicArn = client.create_topic(Name=self.validated_data['topic_name'])
        topic_arn = topicArn["TopicArn"]

        return AWSTopic.objects.create(
            topic_name = self.validated_data['topic_name'],
            topic_arn = topic_arn,
            #create_on = self.validated_data['create_on'],
            valid_until = self.validated_data['valid_until']
        )

    class Meta:
        model = AWSTopic
        fields = ('pk', 'topic_name', 'topic_arn', 'create_on', 'valid_until', 'creator')
        read_only_fields = ['pk', 'topic_arn', 'create_on']
'''

class AWSTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = AWSTopic
        fields = ('pk', 'topic_name', 'topic_arn', 'create_on', 'valid_until', 'creator')
        read_only_fields = ['pk', 'topic_arn', 'create_on']


class UserToAWSTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToAWSTopic
        fields = ('pk', 'aws_topic', 'user')
    

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('pk', 'account_type', 'subject', 'content_text', 'creator', 'create_date', 'auditor', 'audit_date',
         'notification_choice', 'notification_type', 'notification_method', 'topic', 'notifiers',  'publish_on')
        read_only_fields = ['pk', 'create_date']


'''
class NotificationSerializer(serializers.Serializer):
    content = serializers.CharField(required=True)
    
    def create(self, validated_data):
        return Notification.objects.get_or_create(**validated_data)
'''

class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = ('pk', 'notification_id', 'action')
        read_only_fields = ['pk', 'notification_id', 'actor_id', 'action', 'act_on']


class NotificationUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationUsers
        fields = ('pk', 'notification_id', 'notifier_id')