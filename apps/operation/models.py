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


'''
The NoticeMessage Class will depricate soon, please ignore this function
'''
class NoticeMessage(models.Model): 

    start_time = models.DateTimeField('Start Time', blank=False)
    end_time = models.DateTimeField('End Time', blank=False)
    message = models.CharField(max_length=200, default='')
    message_zh = models.CharField(max_length=200, default='')
    message_fr = models.CharField(max_length=200, default='')

    class Meta:
        verbose_name_plural = _('Notice Message')

    def __str__(self):
        """
        # String for representing the Model object (in Admin site etc.)
        """
        return self.message


class Notification(models.Model):
    NOTIFICATION_CHOICE = (
        ('U', _('Unicast')),
        # ('M', 'Multicast'),
        ('B', _('Broadcast')),
    )

    NOTIFICATION_TYPE = (
        (1, _('ALERT')),
        # (2, 'GAME'),
        # (3, 'REFERRAL')
    )

    NOTIFICATION_METHOD = (
        ('P', _('push')),
        ('S', _('sms')),
        ('E', _('email'))
    )

    content = models.CharField(max_length=200, default='')
    notification_choice = models.CharField(max_length=1, default='U', choices=NOTIFICATION_CHOICE)
    notification_type = models.IntegerField(default=1, choices=NOTIFICATION_TYPE)
    notification_method = models.CharField(max_length=3, default='P', choices=NOTIFICATION_METHOD)
    notifiers = models.ForeignKey(CustomUser, blank=False, on_delete=models.CASCADE)
    create_on = models.DateTimeField('Create Time', auto_now_add=True, blank=False)
    publish_on = models.DateTimeField('Publish Time', auto_now_add=True, blank=False)

    # pusher_client = Pusher("", "", "", "")

    class Meta:
        verbose_name_plural = _('Notification')

    def __str__(self):
        return self.content


class NotificationLog(models.Model):
    ACTION_TYPE = (
        ('C', _('CREATE')),
        ('U', _('UPDATE')),
        ('D', _('DELETE')),
    )
    notification_id = models.ForeignKey(Notification, on_delete=models.CASCADE)
    # actor_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    actor_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=1, choices=ACTION_TYPE)
    act_on = models.DateTimeField('Action Time', blank=False)


class NotificationUsers(models.Model):
    notification_id = models.ForeignKey(Notification, on_delete=models.CASCADE)
    notifier_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)