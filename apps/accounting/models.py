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
)
CURRENCY_CHOICES = (
    (0, 'CNY'),
    (1, 'USD'),
    (2, 'PHP'),
)
class Transaction(models.Model):
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('User'))
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name=_('Amount'))
    request_time = models.DateTimeField(default=timezone.now, verbose_name=_('Request Time'))
    arrive_time = models.DateTimeField(default=timezone.now, verbose_name=_('Arrive Time'))

    STATE_CHOICES = (
        (0, 'Success'), 
        (1, 'Unsuccess'),
    )
    status = models.SmallIntegerField(choices=STATE_CHOICES,default=1, verbose_name=_('Status'))
    channel = models.SmallIntegerField(choices=CHANNEL_CHOICES, default=2, verbose_name=_('Channel'))

    TYPE_CHOICES = (
        (0, 'Deposit'),
        (1, 'Withdraw')
    )
    transaction_type = models.SmallIntegerField(choices=TYPE_CHOICES, default=0, verbose_name=_('Transaction Type'))
    remark = models.CharField(max_length=200, blank=True, verbose_name=_('Note')) 

    def __str__(self):
        return '{0}: {1}'.format(self.user_id, self.transaction_type)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = verbose_name

class ThirdParty(models.Model):
    thridParty_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thridParty_name = models.SmallIntegerField(choices=CHANNEL_CHOICES, default=2, verbose_name=_('Name'))
    currency = models.SmallIntegerField(choices=CURRENCY_CHOICES, default=0, verbose_name=_('Currency'))
    min_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name=_('Min Amount'))
    max_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name=_('Max Amount'))
    transaction_fee = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True, verbose_name=_('Transaction Fee'))
    switch = models.BooleanField(default=True, verbose_name=_('Active'))

    def __str__(self):
        return '{0}'.format(self.thridParty_id)

    class Meta:
        verbose_name = 'ThirdParty'
        verbose_name_plural = verbose_name
