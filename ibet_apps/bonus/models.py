from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse  # Used to generate urls by reversing the URL patterns
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
import uuid
from datetime import date
import base64
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from system.models import UserGroup
from utils.constants import *
from games.models import Category
from utils.constants import *
from operation.models import Campaign


class Bonus(models.Model):
    bonus_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True)
    start_time = models.DateTimeField('Start Time', blank=False)
    end_time = models.DateTimeField('End Time', blank=False)
    expiration_days = models.IntegerField(null=True)
    status = models.SmallIntegerField(choices=BONUS_STATUS_CHOICES, default=0, verbose_name=_('Bonus Status'))
    ## A comma-separated list of country IDs where this bonus is applicable
    ## The reason that we don't have to normalize it is that we can just do substring matching
    countries = models.CharField(max_length=50, null=True)
    amount = models.FloatField(null=True, blank=True)
    percentage = models.FloatField(null=True, blank=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    is_free_bid = models.BooleanField(default=False)
    type = models.SmallIntegerField(choices=BONUS_TYPE_CHOICES, default=0,
                                    verbose_name=_('Bonus Type'))  # manual bonus doesn't have type
    campaign = models.ForeignKey(Campaign, null=True, on_delete=models.CASCADE)
    affiliate_limit = models.FloatField(null=True, blank=True)
    release_type = models.SmallIntegerField(choices=BONUS_RELEASE_TYPE_CHOICES, default=0,
                                            verbose_name=_('Bonus Release Type'))
    image_s3 = models.CharField(max_length=500, null=True, blank=True)
    currency = models.SmallIntegerField(choices=CURRENCY_CHOICES, default=0, verbose_name=_('Bonus Currency'))
    # category = models.SmallIntegerField(choices=BONUS_CATEGORY, default=0, null=True)  # manual or triggered (bonus 2.0)
    issued = models.BooleanField(default=False, null=True)  # bonus immediately converts to cash when issued (bonus 2.0)
    max_daily_times = models.IntegerField(default=1, null=True)  # per player (bonus 2.0)
    max_total_times = models.IntegerField(default=1, null=True)  # per player (bonus 2.0)
    max_relevant_times = models.IntegerField(default=1, null=True)  # per associated accounts (bonus 2.0)
    max_users = models.IntegerField(null=True, blank=True)  # the maximum number of times this bonus can be claimed (
    # bonus 2.0)
    delivery = models.SmallIntegerField(choices=DELIVERY_CHOICES, default=0)  # release method (bonus 2.0)

    # max_user_amount = models.FloatField(null=True, blank=True)  # the maximum amount a player can get reward for this
    # bonus (bonus 3.0)
    max_amount = models.FloatField(null=True, blank=True)  # maximum amount of bonus could be released (bonus 3.0)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)  # for tiered bonus (bonus 3.0)

    def __str__(self):
        return str(self.name) + str(self.pk)


# Mapping between Bonuses and UserGroups
# if a bonus has no mapping groups, this bonus is open to all (bonus 2.0)
# excluded groups has higher priority than included (bonus 2.0)
class BonusUserGroup(models.Model):
    bonus = models.ForeignKey(Bonus, on_delete=models.CASCADE, verbose_name=_('Bonus'))
    groups = models.ForeignKey(UserGroup, on_delete=models.CASCADE, related_name="groups")
    excluded = models.BooleanField(default=False)


# Mapping between Bonuses and Categories
# This is a 1:n relationship, which indicates which categories a user can use a bonus in
class BonusCategory(models.Model):
    bonus = models.ForeignKey(Bonus, on_delete=models.CASCADE, verbose_name=_('Bonus'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Category'))


class Requirement(models.Model):
    requirement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ## Name of the field in the user_event table where this requirement is based on
    field_name = models.SmallIntegerField(choices=TRANSACTION_TYPE_CHOICES, null=True, default=0,
                                          verbose_name=_('Transaction Type'))
    aggregate_method = models.SmallIntegerField(choices=BONUS_AGGREGATE_METHOD_CHOICES, blank=True, null=True)
    time_limit = models.IntegerField(null=True, blank=True)
    turnover_multiplier = models.IntegerField(null=True, blank=True)
    bonus = models.ForeignKey(Bonus, on_delete=models.CASCADE, verbose_name=_('Bonus'), null=True)
    amount_threshold = models.FloatField(default=0)
    must_have = models.SmallIntegerField(choices=BONUS_MUST_HAVE, default=0, null=True)  # (bonus 2.0)


# Mapping between Requirements and Categories
# This is a 1:n relationship, which indicates which categories the requirement must be satisfied in
class RequirementCategory(models.Model):
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, verbose_name=_('Requirement'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Category'))


# Events that happen on a user with a bonus
class UserBonusEvent(models.Model):
    owner = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name=_('Owner'))
    bonus = models.ForeignKey(Bonus, on_delete=models.CASCADE, verbose_name=_('Bonus'))
    delivery_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    completion_time = models.DateTimeField(null=True, blank=True)
    delivered_by = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name=_('Operator'))
    status = models.SmallIntegerField(choices=USER_BONUS_EVENT_TYPE_CHOICES, default=0,
                                      verbose_name=_('User Bonus Event Type'))
    notes = models.TextField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    # completion_percentage = models.IntegerField(null=True, blank=True, default=0,
    #     validators=[
    #         MaxValueValidator(100),
    #         MinValueValidator(0)
    #     ])
