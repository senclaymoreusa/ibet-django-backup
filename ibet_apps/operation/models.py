from ckeditor_uploader.fields import RichTextUploadingField # Attachment
from django.db import models
from django.urls import reverse #Used to generate urls by reversing the URL patterns
from django.core.validators import RegexValidator, int_list_validator
import uuid
from datetime import date
from django.contrib.auth.models import User
import base64
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from users.models import CustomUser
from bonus.models import Bonus
from system.models import UserGroup
from utils.constants import *


class AWSTopic(models.Model):
    topic_name = models.CharField(max_length=256)
    topic_arn = models.CharField(max_length=500)
    create_on = models.DateField('Create Time', auto_now_add=True, blank=False)
    valid_until = models.DateField('Valid Until', blank=True, null=True)
    creator = models.ForeignKey(CustomUser, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.topic_name


class UserToAWSTopic(models.Model):
    aws_topic = models.ForeignKey(AWSTopic, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


# Notification Content
class Notification(models.Model):
    NOTIFICATION_CHOICE = (
        ('U', _('Unicast')),
        ('M', _('Multicast')),
        ('B', _('Broadcast')),
    )

    subject = models.CharField(max_length=200, default='')
    # content_text = models.CharField(max_length=1000, default='')
    content_text = RichTextUploadingField(blank=True, null=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='creator')
    create_on = models.DateTimeField('Create Date', auto_now_add=True, blank=False)
    auditor = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.CASCADE, related_name='auditor')
    audit_date = models.DateTimeField('Audit Date', null=True)
    campaign = models.CharField(max_length=100, blank=True, null=True)
    bonus = models.ForeignKey(Bonus, blank=True, null=True, on_delete=models.CASCADE)
    # notification_method = models.CharField(max_length=4, default='D', blank=False)
    is_direct_message = models.BooleanField(default=False)
    is_email_message = models.BooleanField(default=False)
    is_sms_message = models.BooleanField(default=False)
    is_push_message = models.BooleanField(default=False)
    # topic = models.ForeignKey(AWSTopic, blank=True, null=True, on_delete=models.CASCADE)
    # notifiers = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.CASCADE)
    publish_on = models.DateTimeField('Publish Time', auto_now_add=True, blank=False)
    status = models.IntegerField(default=1, choices=NOTIFICATION_STATUS)

    class Meta:
        verbose_name_plural = _('Notification')

    def __str__(self):
        return self.subject


class NotificationLog(models.Model):
    notification_id = models.ForeignKey(Notification, on_delete=models.CASCADE)
    actor_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    group_id = models.ForeignKey(AWSTopic, on_delete=models.CASCADE, blank=True, null=True)
    # act_on = models.DateTimeField('Action Time', auto_now_add=True, blank=False)


class NotificationToUsers(models.Model):
    notification_id = models.ForeignKey(Notification, on_delete=models.CASCADE)
    notifier_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
