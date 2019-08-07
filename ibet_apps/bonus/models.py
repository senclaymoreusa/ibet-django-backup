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


class Bonus(models.Model):

    bonus_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField()
    start_time = models.DateTimeField('Start Time', blank=False)
    end_time = models.DateTimeField('End Time', blank=False)
    expiration_days = models.IntegerField()
    is_valid = models.BooleanField(default=False)
    ## A comma-separated list of country IDs where this bonus is applicable
    ## The reason that we don't have to normalize it is that we can just do substring matching
    countries = models.CharField(max_length=50)
    amount = models.FloatField()
    percentage = models.FloatField()
    coupon_code = models.CharField(max_length=50)
    is_free_bid = models.BooleanField(default=False)

# Mapping between Bonuses and Categories
# This is a 1:n relationship, which indicates which categories a user can use a bonus in
class BonusCategory(models.Model):

    bonus = models.ForeignKey(Bonus, on_delete=models.CASCADE, verbose_name=_('Bonus'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Category'))

class Requirement(models.Model):

    requirement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ## Name of the field in the user_event table where this requirement is based on
    field_name = models.SmallIntegerField(choices=TRANSACTION_TYPE_CHOICES, default=0, verbose_name=_('Transaction Type'))
    ## sum or count or single
    aggregate_method = models.CharField(max_length=50)
    time_limit = models.IntegerField()
    turnover_multiplier = models.IntegerField()

# Mapping between Requirements and Categories
# This is a 1:n relationship, which indicates which categories the requirement must be satisfied in
class RequirementCategory(models.Model):

    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, verbose_name=_('Requirement'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Category'))

# Mapping between Bonuses and Requirements
# This is an m:n relationship
class BonusRequirement(models.Model):

    bonus = models.ForeignKey(Bonus, on_delete=models.CASCADE, verbose_name=_('Bonus'))
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, verbose_name=_('Requirement'))