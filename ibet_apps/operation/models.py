from django.db import models
from django.urls import reverse #Used to generate urls by reversing the URL patterns
from django.core.validators import RegexValidator
import uuid
from datetime import date
from django.contrib.auth.models import User
import base64
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from users.models import CustomUser
# Create your models here.


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


class InLineImage(models.Model):
    image = models.BinaryField()


# Notification Content
class Notification(models.Model):
    NOTIFICATION_CHOICE = (
        ('U', _('Unicast')),
        ('M', _('Multicast')),
        ('B', _('Broadcast')),
    )

    NOTIFICATION_TYPE = (
        (1, _('ALERT')),
        (2, _('DIRECT')),
        # (3, 'REFERRAL')
    )

    NOTIFICATION_METHOD = (
        (1, _('direct')),
        (2, _('push')),
        (3, _('sms')),
        (4, _('email'))
    )

    account_type = models.CharField(max_length=200, default='Membership')
    subject = models.CharField(max_length=200, default='')
    content_text = models.CharField(max_length=1000, default='')
    # content_image = models.ForeignKey(InLineImage, blank=False, on_delete=models.CASCADE)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='creator')
    create_on = models.DateTimeField('Create Date', auto_now_add=True, blank=False)
    auditor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='auditor')
    audit_date = models.DateTimeField('Audit Date', null=True)
    notification_choice = models.CharField(max_length=1, default='U', choices=NOTIFICATION_CHOICE)
    notification_type = models.IntegerField(default=1, choices=NOTIFICATION_TYPE)
    notification_method = models.IntegerField(blank=False)
    topic = models.ForeignKey(AWSTopic, blank=True, null=True, on_delete=models.CASCADE)
    notifiers = models.ForeignKey(CustomUser, blank=False, null=True, on_delete=models.CASCADE)
    publish_on = models.DateTimeField('Publish Time', auto_now_add=True, blank=False)

    class Meta:
        verbose_name_plural = _('Notification')

    def __str__(self):
        return self.subject


class NotificationLog(models.Model):
    ACTION_TYPE = (
        ('C', _('CREATE')),
        ('U', _('UPDATE')),
        ('D', _('DELETE')),
    )
    notification_id = models.ForeignKey(Notification, on_delete=models.CASCADE)
    action = models.CharField(max_length=1, choices=ACTION_TYPE)
    # actor_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # act_on = models.DateTimeField('Action Time', auto_now_add=True, blank=False)


class NotificationUsers(models.Model):
    notification_id = models.ForeignKey(Notification, on_delete=models.CASCADE)
    notifier_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)