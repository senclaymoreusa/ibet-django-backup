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
        String for representing the Model object (in Admin site etc.)
        """
        return self.message


class Notification(models.Model):
    content = models.CharField(max_length=100, default='')
    notification_type = models.IntegerField()
    #admin_id = models.CharField(max_length=50, default='')
    #user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    create_on = models.DateTimeField('Create Time', blank=False)
    publish_on = models.DateTimeField('Publish Time', blank=False)

    # pusher_client = Pusher("798093", "38f4171aa9ce43f0b1bf", "f4babe8983a71c89b268", "us3")

    # class Meta:
        # pusher_client
        #verbose_name_plural = _('Push Notice Message')

    def __str__(self):
        return self.content


class NotificationLog(models.Model):
    notification_id = models.ForeignKey(Notification, on_delete=models.CASCADE)
    actor_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=30, default='')
    act_on = models.DateTimeField('Action Time')


class NotificationUsers(models.Model):
    notification_id = models.ForeignKey(Notification, on_delete=models.CASCADE)
    notifier_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)