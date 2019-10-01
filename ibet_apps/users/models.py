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

from django.db.models.signals import post_save
from django.dispatch import receiver

import logging

logger = logging.getLogger('django')

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

    LANGUAGE = (
        ('English', 'English'),
        ('Chinese', 'Chinese'),
        ('French', 'French')
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
        unique=True,
        verbose_name='email address'
    )
    user_tag = models.ManyToManyField(UserTag, blank=True, through='UserWithTag')
    user_deposit_channel = models.ManyToManyField(DepositChannel, blank=True, through='accounting.DepositAccessManagement', verbose_name='Deposit Channel')
    user_withdraw_channel = models.ManyToManyField(WithdrawChannel, blank=True, through='accounting.WithdrawAccessManagement', verbose_name='Withdraw Channel')
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
    # referral_id = models.CharField(max_length=300, blank=True, null=True)
    reward_points = models.IntegerField(default=0)
    referred_by = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, related_name='referees')
    # balance = models.FloatField(default=0)
    activation_code = models.CharField(max_length=255, default='', blank=True)
    active = models.BooleanField(default=False)
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
    member_status = models.SmallIntegerField(choices=MEMBER_STATUS, blank=True, null=True, default=0)
    risk_level = models.SmallIntegerField(choices=RISK_LEVEL, default=0)

    # balance = main_wallet + other_game_wallet
    main_wallet = models.DecimalField(_('Main Wallet'), max_digits=20, decimal_places=4, default=0)
    other_game_wallet = models.DecimalField(_('Other Game Wallet'), max_digits=20, decimal_places=2, default=0)
    bonus_wallet = models.DecimalField(_('Bonus Wallet'), max_digits=20, decimal_places=4, null=True, default=0)
    
    # agent
    # affiliate = models.BooleanField(default=False)              #if a user is agent or not
    user_to_affiliate_time = models.DateTimeField(_('Time of Becoming Agent'), default=None, null=True)
    user_application_time = models.DateTimeField(_('Application Time'), default=None, null=True)
    user_application_info = models.CharField(_('Application Introduction'), max_length=500, null=True, blank=True)

    affiliate_status = models.CharField(_('Affiliate_status'), max_length=50, choices=AFFILIATE_STATUS, null=True, blank=True)
    affiliate_level = models.CharField(_('Affiliate_level'), max_length=50, choices=AFFILIATE_LEVEL, default='Normal')
    transerfer_between_levels = models.BooleanField(default=False)
    id_image = models.CharField(max_length=250, blank=True)
    managed_by = models.ForeignKey('self', blank=True, null=True, on_delete = models.SET_NULL, related_name='manage')

    #commission
    commision_status = models.BooleanField(default=False)               # for current month
    commission_setting = models.CharField(max_length=50, choices=COMMISSION_SET, default='System')

    temporary_block_time = models.DateTimeField(null=True, blank=True)
    temporary_block_timespan = models.DurationField(null=True, blank=True)
    temporary_block_interval = models.SmallIntegerField(choices=TEMPORARY_INTERVAL, null=True, blank=True)

    permanent_block_time = models.DateTimeField(null=True, blank=True)
    permanent_block_timespan = models.DurationField(null=True, blank=True)
    permanent_block_interval = models.SmallIntegerField(choices=PERMANENT_INTERVAL, null=True, blank=True)

    activity_check = models.SmallIntegerField(choices=ACTIVITY_CHECK, default=2)

    ibetMarkets = models.CharField(max_length=100, null=True, blank=True)
    letouMarkets = models.CharField(max_length=100, null=True, blank=True)
    department = models.SmallIntegerField(null=True, blank=True)

    contact_methods = models.CharField(max_length=100, null=True, blank=True)
    social_media = models.BooleanField(default=False)

    bonusesProgram = models.BooleanField(default=False)
    vipProgram = models.BooleanField(default=False)
    
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

class Commission(models.Model):
    
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    commision_percentage = models.DecimalField(_('Commision Percentage'), max_digits=20, decimal_places=2, default=0)
    downline_commision_percentage = models.DecimalField(_('Downline Commision Percentage'), max_digits=20, decimal_places=2, default=0)
    commission_level = models.IntegerField(default=1)
    active_downline_needed = models.IntegerField(default=6)
    monthly_downline_ftd_needed = models.IntegerField(default=6)
    
    def save(self, *args, **kwargs):
        if self._state.adding:
            # Get the maximum display_id value from the database
            last_id = Commission.objects.filter(user_id=self.user_id).aggregate(largest=models.Max('commission_level'))['largest']

            # aggregate can return None! Check it first.
            # If it isn't none, just use the last ID specified (which should be the greatest) and add one to it
            if last_id is not None:
                self.commission_level = last_id + 1

        super(Commission, self).save(*args, **kwargs)

class ReferLink(models.Model):
    
    refer_link_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    refer_link_url = models.URLField(max_length=200, unique=True, null=True, blank=True)
    refer_link_name = models.CharField(max_length=50, default="default")
    ## time of this link was created
    genarated_time = models.DateTimeField(_('Created Time'), auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk:
            code = generate_unique_verification_code()
            self.refer_link_url = code
        return super(ReferLink, self).save(*args, **kwargs)


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
    image_url = models.CharField(max_length=500, null=True, blank=True)
    game_url = models.CharField(max_length=1000, null=True, blank=True)
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



class LinkHistory(models.Model):

    history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    link = models.ForeignKey(ReferLink, on_delete=models.CASCADE, verbose_name=_('Link'))
    ## time of this link was clicked
    timestamp = models.DateTimeField(_('User Click Time'), auto_now_add=True)
    ## click by ip
    user_ip = models.GenericIPAddressField(_('Action Ip'), null=True)

class Limitation(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('User'), related_name="limit_user")
    limit_type = models.SmallIntegerField(choices=LIMIT_TYPE, default=0)
    amount = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    temporary_amount = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True, default=0)
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
class GameRequestsModel(models.Model):

    Success_Status = [
        ('1', '1'),
        ('0', '0'),
    ]

    # GB Sports and AG

    MemberID       = models.CharField(max_length=30)                 # Same as Username
    TransType      = models.CharField(max_length=30)                 # Transaction Type
    time            = models.CharField(max_length=100, blank=True)   # Current Time

    # GB Sports only

    Method         = models.CharField(max_length=30)                            
    Success        = models.CharField(choices=Success_Status, max_length=1)
                              
    ThirdPartyCode = models.CharField(max_length=30)
    BetTotalCnt    = models.CharField(max_length=30)
    BetTotalAmt    = models.CharField(max_length=30)
    BetID          = models.CharField(max_length=20)
    SettleID       = models.CharField(max_length=20)
    BetGrpNO       = models.CharField(max_length=50)
    TPCode         = models.CharField(max_length=30)
    GBSN           = models.CharField(max_length=30)
    CurCode        = models.CharField(max_length=30)
    BetType        = models.CharField(max_length=20)
    BetTypeParam1  = models.CharField(max_length=20)
    BetTypeParam2  = models.CharField(max_length=20)
    Wintype        = models.CharField(max_length=20)
    HxMGUID        = models.CharField(max_length=20)
    InitBetAmt     = models.CharField(max_length=30)
    RealBetAmt     = models.CharField(max_length=30)
    HoldingAmt     = models.CharField(max_length=30)
    InitBetRate    = models.CharField(max_length=30)
    RealBetRate    = models.CharField(max_length=20)
    PreWinAmt      = models.CharField(max_length=30)
    BetResult      = models.CharField(max_length=30)
    WLAmt          = models.CharField(max_length=30)
    RefundBetAmt   = models.CharField(max_length=30)
    TicketBetAmt   = models.CharField(max_length=30)
    TicketResult   = models.CharField(max_length=30)
    TicketWLAmt    = models.CharField(max_length=30)
    SettleDT       = models.CharField(max_length=30)

    # AG only

    sessionToken    = models.CharField(max_length=100, blank=True)
    currency        = models.CharField(max_length=100, blank=True)
    value           = models.CharField(max_length=100, blank=True)
    agentCode       = models.CharField(max_length=100, blank=True)
    transactionID   = models.CharField(max_length=100, blank=True)
    platformType    = models.CharField(max_length=100, blank=True)
    Round           = models.CharField(max_length=100, blank=True)
    gametype        = models.CharField(max_length=100, blank=True)
    gameCode        = models.CharField(max_length=100, blank=True)
    tableCode       = models.CharField(max_length=100, blank=True)
    transactionCode = models.CharField(max_length=100, blank=True)
    deviceType      = models.CharField(max_length=100, blank=True)
    playtype        = models.CharField(max_length=100, blank=True)
    netAmount       = models.CharField(max_length=100, blank=True)
    validBetAmount  = models.CharField(max_length=100, blank=True)
    billNo          = models.CharField(max_length=100, blank=True)
    ticketStatus    = models.CharField(max_length=100, blank=True)
    gameResult      = models.CharField(max_length=100, blank=True)
    finish          = models.CharField(max_length=100, blank=True)
    remark          = models.CharField(max_length=100, blank=True)
    amount          = models.CharField(max_length=100, blank=True)
    gameId          = models.CharField(max_length=100, blank=True)
    roundId         = models.CharField(max_length=100, blank=True)

    # Yggdrasil

    organization    = models.CharField(max_length=100, blank=True)
    version         = models.CharField(max_length=100, blank=True)
    reference       = models.CharField(max_length=100, blank=True)
    subreference    = models.CharField(max_length=100, blank=True)
    description     = models.CharField(max_length=100, blank=True)
    prepaidticketid = models.CharField(max_length=100, blank=True)
    prepaidvalue    = models.CharField(max_length=100, blank=True)
    prepaidcost     =models.CharField(max_length=100, blank=True)
    prepaidref      = models.CharField(max_length=100, blank=True)
    jackpotcontribution = models.CharField(max_length=100, blank=True)
    isJackpotWin    = models.CharField(max_length=100, blank=True)
    bonusprize      = models.CharField(max_length=100, blank=True)
    tickets         = models.CharField(max_length=100, blank=True)
    singleWin       = models.CharField(max_length=100, blank=True)
    totalWin        = models.CharField(max_length=100, blank=True)
    roundCount      = models.CharField(max_length=100, blank=True)
    ruleType        = models.CharField(max_length=100, blank=True)
    cash            = models.CharField(max_length=100, blank=True)
    bonus           = models.CharField(max_length=100, blank=True)
    campaignref     = models.CharField(max_length=100, blank=True)
    lang            = models.CharField(max_length=100, blank=True)
    last            = models.CharField(max_length=100, blank=True)

    # SA

    txnid           = models.CharField(max_length=100, blank=True)
    hostid          = models.CharField(max_length=100, blank=True)
    txn_reverse_id  = models.CharField(max_length=100, blank=True)



    def __str__(self):
        return  self.MemberID + ' ' + self.TransType



@receiver(post_save, sender=CustomUser)
def my_handler(sender, **kwargs):
    if kwargs['created']:
        user=kwargs['instance']
        temp_refer_link_url = generate_unique_verification_code()
        refer_link = ReferLink.objects.create(
            user_id = user,
        )
        logger.info("Auto created a refer link for new user" + str(user.username))
    

def generate_verification_code():
    return base64.urlsafe_b64encode(uuid.uuid1().bytes.rstrip())[:25]

def generate_unique_verification_code():
    temp_refer_link_url = str(generate_verification_code())[2:-1]
    while ReferLink.objects.filter(refer_link_url=temp_refer_link_url):   # make sure no duplicates
        temp_refer_link_url = str(generate_verification_code())[2:-1]
    return temp_refer_link_url


#  def save(self, *args, **kwargs):
#         if self.pk:
#             temp = str(self.generate_verification_code())[2:-1]
#             while ReferLink.objects.filter(refer_link_url=temp):   # make sure no duplicates
#                 temp = str(self.generate_verification_code())[2:-1]
#             self.refer_link_url = temp

#         return super(ReferLink, self).save(*args, **kwargs)

    