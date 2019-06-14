from django.db import models
import uuid

from users.models import CustomUser
from accounting.models import Transaction
from django.utils.translation import ugettext_lazy as _

# Create your models here.

AGENT_LEVEL_BACK_CHOICES = (
    (0, 'Promo Agent'), 
    (1, 'Affliate'),
    (2, 'Primary Agent'),
)
AGENT_LEVEL_FRONT_CHOICES = (
    (0, 'Normal Agent'), 
    (1, 'Advance Agent'),
)

class Agent(models.Model):
    username = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, editable=False, unique=True)
    agent_level_back = models.SmallIntegerField(choices=AGENT_LEVEL_BACK_CHOICES,default=0, verbose_name=_('Agent Level - Backend'))
    agent_level_front = models.SmallIntegerField(choices=AGENT_LEVEL_FRONT_CHOICES,default=0, verbose_name=_('Agent Level'))
    active_user = models.IntegerField(default=0, verbose_name=_('Active User'))
    downline_deposit = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name=_('Downline Deposit'))
    turnover = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name=_('Turnover'))
    downline_ggr = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name=_('Downline GGR'))
    commission_this_month = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name=_('Commission'))
    commission_last_month = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name=_('Last Month Commission'))
    commission_of_the_month_before = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name=_('Commission Of the Month Before'))

    class Meta:
        verbose_name = "Agent"
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return '{0}'.format(self.username)
    
    # 代理净盈利=（所有平台输赢*85%）－系统红利－调帐－用户存提款总金额*1.5% 