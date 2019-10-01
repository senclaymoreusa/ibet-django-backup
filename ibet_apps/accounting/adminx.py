import xadmin
from xadmin.layout import Main, Side, Fieldset

from .models import *
# from .forms import DepositReviewForm, WithdrawReviewForm, TransactionForm
from .admin_views.deposit_views import *
from .admin_views.psp_views import *
from .admin_views.withdrawal_views import *
from .admin_views.channel_list import *

xadmin.site.register_view(r'deposit/$', DepositView, name='deposit_view')
xadmin.site.register_view(r'user_info/', UserInfo, name='user_info')
xadmin.site.register_view(r'payment_config/', PaymentConfig, name='psp_config')
xadmin.site.register_view(r'withdrawal/$', WithdrawalView, name='withdrawal_view')
xadmin.site.register_view(r'channel_list/$', ChannelListView, name='channel_list')
# xadmin.site.register_view(r'deposits/$', GetDeposits, name='get_deposits')
