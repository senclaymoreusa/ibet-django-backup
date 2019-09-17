import logging

from rest_framework import serializers, exceptions
from users.serializers import UserDetailsSerializer
from .models import AWSTopic, Notification, NotificationLog, NotificationToUsers, UserToAWSTopic
from system.models import UserGroup

logger = logging.getLogger("notification.create.error")

class LanguageCodeSerializer(serializers.Serializer):
    languageCode = serializers.CharField()


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
        fields = ('pk', 'subject', 'content_text', 'creator', 'create_on', 'auditor', 'audit_date', 'campaign','bonus', 
        'is_direct_message','is_email_message', 'is_sms_message', 'is_push_message', 'publish_on', 'status')
        read_only_fields = ['pk', 'account_type', 'audit_date', 'create_on']


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = ('pk', 'notification_id', 'actor_id')
        read_only_fields = ['pk', 'notification_id', 'actor_id']


class NotificationToUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationToUsers
        fields = ('pk', 'notification_id', 'notifier_id', 'is_read', "is_deleted")
        read_only_fields = ['pk', 'notification_id', 'notifier_id', 'is_read', "is_deleted"]


class MessageUserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = ('pk', 'name', 'description', 'creator', 'groupType', 'created_time', 'approvals')
        read_only_fields = ['pk', 'created_time', 'approvals']