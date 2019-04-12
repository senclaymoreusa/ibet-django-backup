from rest_framework import serializers, exceptions


class LanguageCodeSerializer(serializers.Serializer):
    languageCode = serializers.CharField()