from rest_framework import serializers, exceptions
from .models import NoticeMessage

class LanguageCodeSerializer(serializers.Serializer):
    languageCode = serializers.CharField()


class NoticeMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeMessage
        fields = ('pk', 'start_time', 'end_time', 'message', 'message_zh', 'message_fr')