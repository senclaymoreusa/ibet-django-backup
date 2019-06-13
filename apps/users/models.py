from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse #Used to generate urls by reversing the URL patterns
from django.core.validators import RegexValidator
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
import uuid
from datetime import date
from django.contrib.auth.models import User
import base64
from django.contrib.auth import get_user_model
from accounting.models import DepositChannel, DepositAccessManagement, WithdrawChannel, WithdrawAccessManagement
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from utils.constants import *

class MyUserManager(BaseUserManager):
    def create_user(self, username, email, phone, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
					username = username,
					email = self.normalize_email(email),
                    phone = phone
				)
        user.set_password(password)
        user.save(using=self._db)
        return user
		# user.password = password # bad - do not do this

    def create_superuser(self, username, email, phone, password=None):
        user = self.create_user(
            username = username, email = email, phone = phone, password = password
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

    USER_ATTRIBUTE = (
        (0, _('Direct User')),
        (1, _('User from Promo')),
        (2, _('Advertisements'))
    )

    MEMBER_STATUS = (
        (0, _('Active')),
        (1, _('Inactive')),
        (2, _('Blocked'))
    )
    # add additional fields in here
    username = models.CharField(
					max_length=255,
					validators = [
						RegexValidator(regex = USERNAME_REGEX,
										message='Username must be alphanumeric or contain numbers',
										code='invalid_username'
							)],
					unique=True
				)
    email = models.EmailField(
			max_length=255,
			unique=True,
			verbose_name='email address'
		)
    user_tag = models.ManyToManyField(UserTag, blank=True, through='UserWithTag')
    user_deposit_channel = models.ManyToManyField(DepositChannel, blank=True, through='accounting.DepositAccessManagement', verbose_name='Deposit Channel')
    user_withdraw_channel = models.ManyToManyField(WithdrawChannel, blank=True, through='accounting.WithdrawAccessManagement', verbose_name='Withdraw Channel')
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, unique=True)
    country = models.CharField(max_length=100)
    date_of_birth = models.CharField(max_length=100)
    street_address_1 = models.CharField(max_length=100, blank=True)
    street_address_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    referral_id = models.CharField(max_length=300, blank=True, null=True)
    reward_points = models.IntegerField(default=0)
    referred_by = models.ForeignKey('self', blank=True, null=True, on_delete = models.SET_NULL, related_name='referees')
    # balance = models.FloatField(default=0)
    activation_code = models.CharField(max_length=255, default='', blank=True)
    active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    block = models.BooleanField(default=False)
        
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=True)
    title = models.CharField(max_length=10, blank=True)
    over_eighteen = models.BooleanField(default=False)
    odds_display = models.FloatField(default=0, blank=True)
    preferred_team = models.CharField(max_length=50, blank=True)
    contact_option = models.CharField(max_length=6, choices=CONTACT_OPTIONS, blank=True)
    deposit_limit = models.FloatField(default=100)
    promo_code = models.IntegerField(blank=True, null=True)
    currency = models.CharField(max_length=30, choices=CURRENCY_TYPES, blank=True, default='USD')
    login_times = models.IntegerField(default=0)

    reset_password_code = models.CharField(max_length=4, blank=True)
    user_attribute = models.SmallIntegerField(_('User Attribute'), choices=USER_ATTRIBUTE, default=0)
    product_attribute = models.CharField(_('Product Attribute'), max_length=255, default='', blank=True)
    time_of_registration = models.DateTimeField(_('Time of Registration'), auto_now_add=True, null=True)
    ftd_time = models.DateTimeField(_('Time of FTD'), blank=True, null=True)      # first time deposit
    verfication_time = models.DateTimeField(_('Time of Verification'), blank=True, null=True)
    id_location = models.CharField(_('Location shown on the ID'), max_length=255, default='') 
    last_login_time = models.DateTimeField(_('Last Login Time'), blank=True, null=True)
    last_betting_time = models.DateTimeField(_('Last Betting Time'), blank=True, null=True)
    member_status = models.SmallIntegerField(choices=MEMBER_STATUS, blank=True, null=True)

    # balance = main_wallet + other_game_wallet
    main_wallet = models.DecimalField(_('Main Wallet'), max_digits=20, decimal_places=2, default=0)
    other_game_wallet = models.DecimalField(_('Other Game Wallet'), max_digits=20, decimal_places=2, default=0)

    id_image = models.CharField(max_length=250, blank=True)

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

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone']

    class Meta:
        verbose_name_plural = _('Customer User')

    def get_absolute_url(self):
        return u'/profile/show/%d' % self.id

    def generate_verification_code(self):
        return base64.urlsafe_b64encode(uuid.uuid1().bytes.rstrip())[:25]

    def save(self, *args, **kwargs):
        if not self.pk:
            temp =  str(self.generate_verification_code())[2:-1]
            while get_user_model().objects.filter(referral_id=temp):   # make sure no duplicates
                temp = str(self.generate_verification_code())[2:-1]
            self.referral_id = temp

        return super(CustomUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

    def get_short_name(self):
	    # The user is identified by their email address
	    return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
		# Simplest possible answer: Yes, always
        return True

    def has_perms(self, perm_list, obj=None):
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    

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
        unique_together = (('user','tag'),)
        verbose_name = "Tag"
        verbose_name_plural = _('Assign tag to user')

    
class Status(models.Model):
    status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    notes = models.CharField(max_length=200)
    def __str__(self):
        return '{0}'.format(self.name)


class Category(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    name_zh = models.CharField(max_length=50, null=True, blank=True)
    name_fr = models.CharField(max_length=50, null=True, blank=True)
    parent_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.CharField(max_length=200)
    def __str__(self):
        return '{0}, parent: {1}'.format(self.name, self.parent_id)


class Game(models.Model):
    name = models.CharField(max_length=50)
    name_zh = models.CharField(max_length=50, null=True, blank=True)
    name_fr = models.CharField(max_length=50, null=True, blank=True)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    start_time = models.DateTimeField('Start Time', null=True, blank=True)
    end_time = models.DateTimeField('End Time', null=True, blank=True)
    opponent1 = models.CharField(max_length=200, null=True, blank=True)
    opponent2 = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=200)
    description_zh = models.CharField(max_length=200, null=True, blank=True)
    description_fr = models.CharField(max_length=200, null=True, blank=True)
    status_id = models.ForeignKey(Status, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='game_image', blank=True)
    #game_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #category = models.CharField(max_length=20)
    
    def __str__(self):
        return '{0}: {1}'.format(self.name, self.category_id)

    def get_absolute_url(self):
        """
        Returns the url to access a particular game instance.
        """
        return reverse('game-detail', args=[str(self.id)])


class Language(models.Model):
    """
    Model representing a Language (e.g. English, French, Japanese, etc.)
    """
    name = models.CharField(max_length=200, help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")
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
    
    EVENT_CHOICES = (
        (0, _('Login')),
        (1, _('Logout')),
        (2, _('Register')),
        # (3, _('Deposit')),
        # (4, _('Withdraw')),
        (3, _('Page Visit')),
        # (6, _('bet'))
    )

    ip_addr = models.GenericIPAddressField(_('Action Ip'), blank=True, null=True)
    event_type = models.SmallIntegerField(choices=EVENT_CHOICES, verbose_name=_('Event Type'))
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('User'))
    device = models.CharField(_('Device'), max_length=50, blank=True, null=True)
    browser = models.CharField(_('Browser'), max_length=50, blank=True, null=True)
    refer_url = models.CharField(_('Refer URL'), max_length=255, blank=True, null=True)
    # dollar_amount = models.DecimalField(_('Amount'), max_digits=20, decimal_places=2, blank=True, null=True)
    page_id = models.IntegerField(_('Page'), blank=True, null=True)
    created_time = models.DateTimeField(
        _('Created Time'),
        auto_now_add=True,
        editable=False,
    )
    class Meta:
        verbose_name_plural = _('User action history')



class Bonus(models.Model):

    bonus_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    start_time = models.DateTimeField('Start Time', blank=False)
    end_time = models.DateTimeField('End Time', blank=False)
    expiration_days = models.IntegerField()
    is_valid = models.BooleanField(default=False)
    ## A comma-separated list of country IDs where this bonus is applicable (to be normalized)
    countries = models.CharField(max_length=255)
    ## A comma-separated list of category IDs where this bonus is applicable (to be normalized)
    categories = models.CharField(max_length=255)
    ## A comma-separated list of requirement IDs that we need to apply (to be normalized)
    requirement_ids = models.CharField(max_length=255)  
    amount = models.FloatField()
    percentage = models.FloatField()
    is_free_bid = models.BooleanField(default=False)


class BonusRequirement(models.Model):

    requirement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ## Name of the field in the user_event table where this requirement is based on
    field_name = models.CharField(max_length=50)
    ## sum or count or single
    aggregate_method = models.CharField(max_length=50)
    time_limit = models.IntegerField()
    turnover_multiplier = models.IntegerField()
    ## A comma-separated list of category IDs where this requirement is applicable (to be normalized)
    categories = models.CharField(max_length=255)

class UserBonus(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('User'))
    bonus = models.ForeignKey(Bonus, on_delete=models.CASCADE, verbose_name=_('Bonus'))
    start_time = models.DateTimeField('Start Time', blank=False)
    is_successful = models.BooleanField(default=False)


class ReferLink(models.Model):

    refer_link_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    refer_link_url = models.URLField(max_length=200, unique=True)
    refer_link_name = models.CharField(max_length=50, default="Default")
    ## time of this link was created
    genarate_time = models.DateTimeField(_('Created Time'), auto_now_add=True)
    ## the frequences downline clicked
    click_freq = models.IntegerField(_('User Click Frequence', default=0))
    ## the frequences downline use this link to register
    register_freq = models.IntegerField(_('User Register Frequence', default=0))
    
# Mapping between Users and ReferLink
# This is a 1:n relationship, a user can have at most 10 refer links
class UserReferLink(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('User'))
    link = models.ForeignKey(ReferLink, on_delete=models.CASCADE, verbose_name=_('Link'))


class LinkHistory(models.Model):

    history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    link = models.ForeignKey(ReferLink, on_delete=models.CASCADE, verbose_name=_('Link'))
    ## time of this link was clicked
    timestamp = models.DateTimeField(_('User Click Time'), auto_now_add=True)
    ## click by ip
    user_ip = models.GenericIPAddressField(_('Action Ip'), null=True)