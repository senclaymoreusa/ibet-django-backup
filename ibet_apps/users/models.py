from django.db import models, DatabaseError
from django.contrib.auth.models import AbstractUser
from django.urls import reverse  # Used to generate urls by reversing the URL patterns
from django.core.validators import RegexValidator
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
from django.db import transaction
import uuid
from datetime import date
from django.contrib.auth.models import User
import base64
from django.contrib.auth import get_user_model
from accounting.models import DepositChannel, DepositAccessManagement, WithdrawChannel, WithdrawAccessManagement
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from utils.constants import *
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_cryptography.fields import encrypt

import logging

logger = logging.getLogger('django')


class MyUserManager(BaseUserManager):
    """
    This class handles the creation of our users. We need to create this class and extend BaseUserManager
    because our model (CustomUser) has additional fields to Django's default User class.
    """

    def create_user(self, username, email, phone, password=None):
        """
        Create a CustomUser, which are the users on our site.
        """
        if not email:
            raise ValueError('Users must have an email address')

        # Create and save a CustomUser into the database.
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            phone=phone,
        )
        user.set_password(password)  # Hash the password using Django auth; Never use 'user.password = password'
        # user.active = True # Add this only to fix Letou registeration bug, will remove later
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, phone, password=None):
        """
        Create a superuser, which is just a user object with special attributes.
        """
        user = self.create_user(
            username=username, email=email, phone=phone, password=password
        )
        user.is_admin = True
        user.is_staff = True
        user.active = True
        user.save(using=self._db)
        return user


class UserTag(models.Model):
    tag_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, verbose_name=_("Tag name"), unique=True)
    name_zh = models.CharField(max_length=50, null=True, blank=True)
    name_fr = models.CharField(max_length=50, null=True, blank=True)
    notes = models.CharField(max_length=200, verbose_name=_("Notes"))

    class Meta:
        verbose_name_plural = _('User Tag')

    def __str__(self):
        return self.name


class CustomUser(AbstractBaseUser):
    """
    This class represents the users on our site. A custom user is needed because of
    our additional custom fields not in Django's default User. AbstractBaseUser provides a
    core implementation of the User model and features such as hashed passwords.
    The primary attributes of a user are username, password, email, and first & last name.
    """
    USER_ATTRIBUTE = (
        (0, _('Direct User')),
        (1, _('User from Promo')),
        (2, _('Advertisements'))
    )

    LANGUAGE = (
        ('English', 'English'),
        ('Chinese', 'Chinese'),
        ('Thai', 'Thai'),
        ('Vietnamese', 'Vietnamese'),
    )

    # add additional fields in here
    username = models.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex=USERNAME_REGEX,
                message='Username must be alphanumeric or contain numbers',
                code='invalid_username'
            )
        ],
        unique=True
    )
    email = models.EmailField(
        max_length=255,
        verbose_name='email address',
        blank=True
    )
    user_tag = models.ManyToManyField(UserTag, blank=True, through='UserWithTag')
    # user_deposit_channel = models.ManyToManyField(DepositChannel, blank=True, through='accounting.DepositAccessManagement', verbose_name='Deposit Channel')
    # user_withdraw_channel = models.ManyToManyField(WithdrawChannel, blank=True, through='accounting.WithdrawAccessManagement', verbose_name='Withdraw Channel')
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=25)
    country = models.CharField(max_length=100)
    date_of_birth = models.CharField(max_length=100)
    street_address_1 = models.CharField(max_length=100, blank=True)
    street_address_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    zipcode = models.CharField(max_length=100)
    language = models.CharField(max_length=20, choices=LANGUAGE, default='English')

    # verification
    email_verified = models.BooleanField(default=False, null=True, blank=True)
    phone_verified = models.BooleanField(default=False, null=True, blank=True)
    id_verified = models.BooleanField(default=False, null=True, blank=True)
    address_verified = models.BooleanField(default=False, null=True, blank=True)

    # referral program
    referral_code = models.CharField(max_length=10, blank=True, null=True)
    # referrer's path append user.pk/ generate a referral path
    referral_path = models.CharField(max_length=1000, blank=True, null=True)
    referred_by = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, related_name='referees')
    referred_by_channel = models.ForeignKey('users.ReferChannel', null=True, blank=True, on_delete=models.CASCADE)
    reward_points = models.IntegerField(default=0)
    vip_level = models.ForeignKey('users.Segmentation', on_delete=models.CASCADE, null=True)

    # balance = models.FloatField(default=0)
    activation_code = models.CharField(max_length=255, default='', blank=True)
    active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    block = models.BooleanField(default=False)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=True, null=True)
    title = models.CharField(max_length=10, blank=True)
    over_eighteen = models.BooleanField(default=False)
    odds_display = models.FloatField(default=0, blank=True)
    preferred_team = models.CharField(max_length=50, blank=True)
    contact_option = models.CharField(max_length=6, choices=CONTACT_OPTIONS, blank=True)
    deposit_limit = models.FloatField(default=100)
    promo_code = models.IntegerField(blank=True, null=True)
    currency = models.SmallIntegerField(choices=CURRENCY_CHOICES, blank=True, default=0)
    login_times = models.IntegerField(default=0)

    reset_password_code = models.CharField(max_length=4, blank=True)
    user_attribute = models.SmallIntegerField(_('User Attribute'), choices=USER_ATTRIBUTE, default=0)
    product_attribute = models.CharField(_('Product Attribute'), max_length=255, default='', blank=True)
    time_of_registration = models.DateTimeField(_('Time of Registration'), auto_now_add=True, null=True)
    ftd_time = models.DateTimeField(_('Time of FTD'), blank=True, null=True)  # first time deposit
    ftd_time_amount = models.DecimalField(_('Amount of FTD'), max_digits=20, decimal_places=4, default=0)
    verfication_time = models.DateTimeField(_('Time of Verification'), blank=True, null=True)
    id_location = models.CharField(_('Location shown on the ID'), max_length=255, default='')
    last_login_time = models.DateTimeField(_('Last Login Time'), blank=True, null=True)
    last_betting_time = models.DateTimeField(_('Last Betting Time'), blank=True, null=True)
    member_status = models.SmallIntegerField(choices=MEMBER_STATUS, blank=True, null=True, default=0)
    member_changed_time = models.DateTimeField(_('Status Changed Time'), blank=True, null=True)
    member_changed_by = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL,
                                             related_name='MemberChange')
    risk_level = models.SmallIntegerField(choices=RISK_LEVEL, default=0)

    # The following 3 fields store the user's money for playing games. main_wallet is the primary wallet used.
    # balance = main_wallet + other_game_wallet
    main_wallet = models.DecimalField(_('Main Wallet'), max_digits=20, decimal_places=4, default=0)
    other_game_wallet = models.DecimalField(_('Other Game Wallet'), max_digits=20, decimal_places=4, default=0)
    bonus_wallet = models.DecimalField(_('Bonus Wallet'), max_digits=20, decimal_places=4, null=True, default=0)
    user_to_affiliate_time = models.DateTimeField(_('Time of Becoming Agent'), default=None, null=True, blank=True)
    user_application_time = models.DateTimeField(_('Application Time'), default=None, null=True, blank=True)
    user_application_info = models.CharField(_('Application Introduction'), max_length=500, null=True, blank=True)

    affiliate_status = models.CharField(_('Affiliate_status'), max_length=50, choices=AFFILIATE_STATUS, null=True,
                                        blank=True)
    affiliate_level = models.CharField(_('Affiliate_level'), max_length=50, choices=AFFILIATE_LEVEL, default='Normal')
    transerfer_between_levels = models.BooleanField(default=False)
    id_image = models.CharField(max_length=250, blank=True)
    affiliate_managed_by = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL,
                                             related_name='AffiliateManager')
    vip_managed_by = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL,
                                       related_name='VIPManager')

    # commission
    commission_status = models.BooleanField(default=False)  # for current month
    commission_setting = models.CharField(max_length=50, choices=COMMISSION_SET, default='System')

    temporary_block_time = models.DateTimeField(null=True, blank=True)
    temporary_block_timespan = models.DurationField(null=True, blank=True)
    temporary_block_interval = models.SmallIntegerField(choices=TEMPORARY_INTERVAL, null=True, blank=True)

    permanent_block_time = models.DateTimeField(null=True, blank=True)
    permanent_block_timespan = models.DurationField(null=True, blank=True)
    permanent_block_interval = models.SmallIntegerField(choices=PERMANENT_INTERVAL, null=True, blank=True)

    activity_check = models.SmallIntegerField(choices=ACTIVITY_CHECK, default=2)

    ibetMarkets = models.CharField(max_length=100, null=True, blank=True)  # only for admin user market
    letouMarkets = models.CharField(max_length=100, null=True, blank=True)  # only for admin user market
    department = models.SmallIntegerField(null=True, blank=True)

    contact_methods = models.CharField(max_length=100, null=True, blank=True)
    social_media = models.BooleanField(default=False)

    bonusesProgram = models.BooleanField(default=False)
    vipProgram = models.BooleanField(default=False)

    brand = models.CharField(choices=BRAND_OPTIONS, null=True, blank=True, max_length=50)

    # security question and answer and withdraw password
    withdraw_password = models.CharField(_('withdraw password'), max_length=128, blank=True, null=True)
    security_question = models.SmallIntegerField(choices=SECURITY_QUESTION, blank=True, null=True)
    security_answer = models.CharField(_('Security answer'), max_length=128, blank=True, null=True)

    # favorite payment method
    favorite_payment_method = models.CharField(max_length=128, blank=True, null=True)

    created_time = models.DateTimeField(
        _('Created Time'),
        auto_now_add=True,
        editable=False,
    )
    modified_time = models.DateTimeField(
        _('Modified Time'),
        auto_now_add=True,
        editable=False,
    )

    objects = MyUserManager()  # Links our custom UserManager to our CustomUser model.

    USERNAME_FIELD = 'username'  # field to be used as unique identifier for CustomUser
    REQUIRED_FIELDS = ['email', 'phone']  # fields prompted for when creating superuser

    class Meta:
        verbose_name_plural = _('Customer User')

    def get_absolute_url(self):
        return u'/profile/show/%d' % self.id

    def get_user_address(self):
        address = ''
        if self.street_address_1:
            address += str(self.street_address_1) + ', '
        if self.street_address_2:
            address += str(self.street_address_2) + ' '
        if self.city:
            address += str(self.city) + ' '
        if self.state:
            address += str(self.state) + ' '
        if self.zipcode:
            address += str(self.zipcode)
        return address

    def __str__(self):
        return self.username

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def has_perm(self, perm, obj=None):
        # Does the user have a specific permission?
        # Simplest possible answer: Yes, always
        return True

    def has_perms(self, perm_list, obj=None):
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        # Does the user have permissions to view the app `app_label`?
        # Simplest possible answer: Yes, always
        return True


# User Personal Commission
class PersonalCommissionLevel(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    commission_percentage = models.DecimalField(_('commission Percentage'), max_digits=20, decimal_places=4, default=0)
    downline_commission_percentage = models.DecimalField(_('Downline commission Percentage'), max_digits=20,
                                                         decimal_places=4, default=0)
    commission_level = models.IntegerField(default=1)
    active_downline_needed = models.IntegerField(default=6)
    monthly_downline_ftd_needed = models.IntegerField(default=6)
    ngr = models.DecimalField(max_digits=20, decimal_places=4, default=0)

    def save(self, *args, **kwargs):
        if self._state.adding:
            # Get the maximum display_id value from the database
            last_id = PersonalCommissionLevel.objects.filter(user_id=self.user_id).aggregate(largest=models.Max('commission_level'))[
                'largest']

            # aggregate can return None! Check it first.
            # If it isn't none, just use the last ID specified (which should be the greatest) and add one to it
            if last_id is not None:
                self.commission_level = last_id + 1

        super(PersonalCommissionLevel, self).save(*args, **kwargs)


# System default Commission
class SystemCommissionLevel(models.Model):
    commission_level = models.IntegerField(unique=True)
    commission_percentage = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    downline_commission_percentage = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    active_downline_needed = models.IntegerField(default=0)
    monthly_downline_ftd_needed = models.IntegerField(default=0)
    ngr = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    operation_fee = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    payment_fee = models.DecimalField(max_digits=7, decimal_places=4, default=0)


# one user can have up to 10 referral channels
class ReferChannel(models.Model):
    # refer_channel_code is ReferChannel.pk
    user_id = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    refer_channel_name = models.CharField(max_length=100)
    # time of this channel was created
    generated_time = models.DateTimeField(_('Created Time'), auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'refer_channel_name',)

    def __str__(self):
        return self.refer_channel_name


class UserWithTag(models.Model):
    STATUS_CHOICES = (
        (0, _('pending')),
        (1, _('approved')),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('User'))
    tag = models.ForeignKey(UserTag, on_delete=models.CASCADE, verbose_name=_('Tag'))
    status = models.SmallIntegerField(default=0, choices=STATUS_CHOICES, verbose_name=_('Status'))

    def __str__(self):
        return '{0}'.format(self.tag)

    class Meta:
        unique_together = (('user', 'tag'),)
        verbose_name = "Tag"
        verbose_name_plural = _('Assign tag to user')


class Status(models.Model):
    status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    notes = models.CharField(max_length=200)

    def __str__(self):
        return '{0}'.format(self.name)


class Language(models.Model):
    """
    Model representing a Language (e.g. English, French, Japanese, etc.)
    """
    name = models.CharField(max_length=200,
                            help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    # name = models.CharField(max_length=200, choices= ((u'en', u'English'), (u'zh', u'Chinese',), (u'fr', u'Franch')))
    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name


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


class Config(models.Model):
    name = models.CharField(max_length=50, default='General')
    referral_award_points = models.IntegerField(default=5)
    referral_accept_points = models.IntegerField(default=3)
    referral_limit = models.IntegerField(default=10)
    level = models.IntegerField(default=2)
    Referee_add_balance_reward = models.IntegerField(default=1)

    def __str__(self):
        return self.name


class UserAction(models.Model):
    ip_addr = models.GenericIPAddressField(_('Action Ip'), blank=True, null=True)
    event_type = models.SmallIntegerField(choices=EVENT_CHOICES, verbose_name=_('Event Type'))
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('User'))
    device = models.CharField(_('Device'), max_length=50, blank=True, null=True)
    browser = models.CharField(_('Browser'), max_length=200, blank=True, null=True)
    refer_url = models.CharField(_('Refer URL'), max_length=255, blank=True, null=True)
    # dollar_amount = models.DecimalField(_('Amount'), max_digits=20, decimal_places=4, blank=True, null=True)
    page_id = models.IntegerField(_('Page'), blank=True, null=True)
    result = models.CharField(max_length=10, null=True, blank=True)
    ip_location = JSONField(null=True, default=dict)
    other_info = JSONField(null=True, default=dict)
    created_time = models.DateTimeField(
        _('Created Time'),
        default=timezone.now,
        editable=False,
    )

    class Meta:
        verbose_name_plural = _('User action history')


class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user")
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="admin")
    message = models.CharField(max_length=250)
    activity_type = models.SmallIntegerField(choices=ACTIVITY_TYPE, default=0)
    created_time = models.DateTimeField(
        _('Created Time'),
        auto_now_add=True,
        editable=False,
    )


class Limitation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('User'), related_name="limit_user")
    limit_type = models.SmallIntegerField(choices=LIMIT_TYPE, default=0)
    amount = models.DecimalField(decimal_places=4, max_digits=20, null=True, blank=True)
    temporary_amount = models.DecimalField(decimal_places=4, max_digits=20, null=True, blank=True, default=0)
    product = models.SmallIntegerField(choices=GAME_PRODUCT, default=0, null=True)
    interval = models.SmallIntegerField(choices=TEMPORARY_INTERVAL, default=0, null=True)
    expiration_time = models.DateTimeField(null=True, blank=True)

    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name="limit_admin")

    created_time = models.DateTimeField(
        _('Created Time'),
        auto_now_add=True,
        editable=False,
    )
    modified_time = models.DateTimeField(
        _('Modified Time'),
        auto_now_add=True,
        editable=False,
    )


# Member VIP System

class Segmentation(models.Model):
    name = models.CharField(max_length=50)
    level = models.IntegerField()
    turnover_threshold = models.DecimalField(max_digits=20, decimal_places=4)
    annual_threshold = models.DecimalField(max_digits=20, decimal_places=4)
    platform_turnover_daily = models.DecimalField(max_digits=20, decimal_places=4)
    deposit_amount_daily = models.DecimalField(max_digits=20, decimal_places=4)
    deposit_amount_monthly = models.DecimalField(max_digits=20, decimal_places=4)
    general_bonuses = models.BooleanField(default=False)
    product_turnover_bonuses = models.BooleanField(default=False)

    def __str__(self):
        return str(self.level)


class UserWallet(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    provider = models.ForeignKey('games.GameProvider', on_delete=models.CASCADE)
    wallet_amount = models.DecimalField(_('Wallet'), max_digits=20, decimal_places=4, default=0)


class UserBonusWallet(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    category = models.ForeignKey('games.Category', on_delete=models.CASCADE)
    wallet_amount = models.DecimalField(_('Wallet'), max_digits=20, decimal_places=4, default=0)

    class Meta:
        unique_together = ('user', 'category',)

class WithdrawAccounts(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    account_no = encrypt(models.CharField(max_length=50))
