from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse #Used to generate urls by reversing the URL patterns
from django.core.validators import RegexValidator
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
import uuid
from datetime import date
import base64
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from utils.constants import *
from games.models import Category
from utils.constants import *
from operation.models import Campaign


class Bonus(models.Model):

    bonus_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField()
    start_time = models.DateTimeField('Start Time', blank=False)
    end_time = models.DateTimeField('End Time', blank=False)
    expiration_days = models.IntegerField()
    status = models.SmallIntegerField(choices=BONUS_STATUS_CHOICES, default=0, verbose_name=_('Bonus Type'))
    ## A comma-separated list of country IDs where this bonus is applicable
    ## The reason that we don't have to normalize it is that we can just do substring matching
    countries = models.CharField(max_length=50)
    amount = models.FloatField(null=True, blank=True)
    percentage = models.FloatField(null=True, blank=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    is_free_bid = models.BooleanField(default=False)
    type = models.SmallIntegerField(choices=BONUS_TYPE_CHOICES, default=0, verbose_name=_('Bonus Type'))
    campaign = models.ForeignKey(Campaign, null=True, on_delete=models.CASCADE)
    affiliate_limit = models.FloatField(null=True, blank=True)
    release_type = models.SmallIntegerField(choices=BONUS_RELEASE_TYPE_CHOICES, default=0, verbose_name=_('Bonus Release Type'))
    image_s3 = models.CharField(max_length=500, null=True, blank=True)


# Mapping between Bonuses and Categories
# This is a 1:n relationship, which indicates which cate`````````````````````````````````````````````````````````````gories a user can use a bonus in
class BonusCategory(models.Model):

    bonus = models.ForeignKey(Bonus, on_delete=models.CASCADE, verbose_name=_('Bonus'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Category'))

class Requirement(models.Model):

    requirement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ## Name of the field in the user_event table where this requirement is based on
    field_name = models.SmallIntegerField(choices=TRANSACTION_TYPE_CHOICES, default=0, verbose_name=_('Transaction Type'))
    aggregate_method = models.SmallIntegerField(choices=BONUS_AGGREGATE_METHOD_CHOICES,blank=True,null=True)
    time_limit = models.IntegerField(null=True,blank=True)
    turnover_multiplier = models.IntegerField(null=True,blank=True)
    bonus = models.ForeignKey(Bonus, on_delete=models.CASCADE, verbose_name=_('Bonus'), null=True)
    amount_threshold = models.FloatField(default=0)

# Mapping between Requirements and Categories
# This is a 1:n relationship, which indicates which categories the requirement must be satisfied in
class RequirementCategory(models.Model):

    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, verbose_name=_('Requirement'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Category'))


# Events that happen on a user with a bonus
class UserBonusEvents(models.Model):

    owner = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name=_('Owner'))
    bonus = models.ForeignKey(Bonus, on_delete=models.CASCADE, verbose_name=_('Bonus'))
    timestamp = models.DateTimeField('Start Time', blank=False)
    delivered_by = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name=_('Operator'))
    status = models.SmallIntegerField(choices=USER_BONUS_EVENT_TYPE_CHOICES, default=0, verbose_name=_('User Bonus Event Type'))
    notes = models.TextField(null=True, blank=True)



