from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import uuid
# Create your models here.
CHANNEL_CHOICES = (
    (0, 'Alipay'),
    (1, 'Wechat'),
    (2, 'Card'),
    (3, 'Qaicash'),
    (4, 'Asia Pay')
)
CURRENCY_CHOICES = (
    (0, 'CNY'),
    (1, 'USD'),
    (2, 'PHP'),
    (3, 'IDR'),
)
STATE_CHOICES = (
    (0, 'Success'), 
    (1, 'Unsuccess'),
)
REVIEW_STATE_CHOICES = (
    (0, 'Approved'), 
    (1, 'Pending'),
    (2, 'Rejected'),
)
TYPE_CHOICES = (
    (0, 'Deposit'),
    (1, 'Withdraw')
)

class Transaction(models.Model):
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('User'))
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name=_('Amount'))
    request_time = models.DateTimeField(default=timezone.now, verbose_name=_('Request Time'))
    arrive_time = models.DateTimeField(default=timezone.now, verbose_name=_('Arrive Time'))
    status = models.SmallIntegerField(choices=STATE_CHOICES,default=1, verbose_name=_('Status'))
    channel = models.SmallIntegerField(choices=CHANNEL_CHOICES, default=2, verbose_name=_('Channel'))
    transaction_type = models.SmallIntegerField(choices=TYPE_CHOICES, default=0, verbose_name=_('Transaction Type'))
    review_status = models.SmallIntegerField(choices=REVIEW_STATE_CHOICES, default=1, verbose_name=_('Review status'))
    remark = models.CharField(max_length=200, blank=True, verbose_name=_('Note')) 

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}: {1}'.format(self.user_id, self.transaction_type)
    

class ThirdParty(models.Model):
    thridParty_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thridParty_name = models.SmallIntegerField(choices=CHANNEL_CHOICES, default=2, verbose_name=_('Name'))
    method = models.CharField(max_length = 30,  verbose_name =_('Method'))
    currency = models.SmallIntegerField(choices=CURRENCY_CHOICES, default=0, verbose_name=_('Currency'))
    min_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name=_('Min Amount'))
    max_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name=_('Max Amount'))
    switch = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        abstract = True

    def __str__(self):
        return '{0}'.format(self.thridParty_name)
 

class DepositChannel(ThirdParty):
    priority = models.IntegerField(default=0, verbose_name=_('Priority'))

    deposit_channel = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True, 
        related_name = "sb",
        through='DepositAccessManagement',
        through_fields=('deposit_channel', 'user_id'),
    )

    class Meta:
        verbose_name = 'Deposit Channel'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.get_thridParty_name_display()


class WithdrawChannel(ThirdParty):
    transaction_fee = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True, verbose_name=_('Transaction Fee'))
    
    class Meta:
        verbose_name = 'Withdraw Channel'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.get_thridParty_name_display()


class DepositAccessManagement(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE, related_name="deposit_user")
    deposit_channel = models.ForeignKey(DepositChannel, on_delete=models.CASCADE, related_name="deposit_access_channel", verbose_name=_('Channel'))

    class Meta:
        unique_together = (('user_id','deposit_channel'),)
        verbose_name = "Deposit Access management"
        verbose_name_plural = verbose_name


class WithdrawAccessManagement(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE, related_name="withdraw_user")
    withdraw_channel = models.ForeignKey(WithdrawChannel, on_delete=models.CASCADE, related_name="withdraw_access_channel", verbose_name=_('Channel'))

    class Meta:
        unique_together = (('user_id','withdraw_channel'),)
        verbose_name = "Withdraw Access management"
        verbose_name_plural = verbose_name