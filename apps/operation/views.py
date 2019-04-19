from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from .serializers import NoticeMessageSerializer
from .models import NoticeMessage

class NoticeMessageView(ListAPIView):
    serializer_class = NoticeMessageSerializer
    queryset = NoticeMessage.objects.all()