from django.db import models
from django.urls import reverse #Used to generate urls by reversing the URL patterns
from django.core.validators import RegexValidator
import uuid
from datetime import date
from django.contrib.auth.models import User
import base64
from django.contrib.auth import get_user_model

# Create your models here.


class NoticeMessage(models.Model): 

    start_time = models.DateTimeField('Start Time', blank=False)
    end_time = models.DateTimeField('End Time', blank=False)
    message = models.CharField(max_length=200, default='')
    message_zh = models.CharField(max_length=200, default='')
    message_fr = models.CharField(max_length=200, default='')

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.message