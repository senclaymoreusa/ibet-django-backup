import xadmin
from xadmin.layout import Main, Side, Fieldset

from .models import *
# from .forms import DepositReviewForm, WithdrawReviewForm, TransactionForm
from .admin_views.deposit_views import *
from .admin_views.psp_views import *
from .admin_views.withdrawal_views import *
from .admin_views.channel_list import *
from .models import Transaction, DepositAccessManagement, DepositChannel, WithdrawAccessManagement, WithdrawChannel
from .forms import DepositReviewForm, WithdrawReviewForm, TransactionForm
from accounting.admin_views.deposit_views import *
from accounting.admin_views.withdrawal_views import *
from accounting.admin_views.channel_list import *


xadmin.site.register_view(r'deposits/modify', DepositView, name='modify_deposit')
xadmin.site.register_view(r'user_info/', UserInfo, name='user_info')
xadmin.site.register_view(r'get_transactions/', GetTransactions, name='get_transactions')
xadmin.site.register_view(r'payment_config/', PaymentConfig, name='psp_config')
xadmin.site.register_view(r'withdrawals/(?P<page>-?\d*)/$', GetWithdrawals, name='get_withdrawals')
xadmin.site.register_view(r'withdrawals/modify/', WithdrawalView, name='modify_withdrawal')
xadmin.site.register_view(r'channel_list/$', ChannelListView, name='channel_list')
xadmin.site.register_view(r'^deposits/(?P<page>-?\d*)/$', GetDeposits, name='get_deposits')

# xadmin.site.register_view('deposits/$', GetDeposits, name='get_deposits')















# class TransactionAdmin(object):
#     list_display = ('user_id', 'order_id','transaction_id','transaction_type', 'amount', 'status',
#     'method','channel', 'request_time', 'arrive_time', 'review_status', 'remark', 'currency')
#     list_filter = ('transaction_type', 'status', 'channel', 'review_status', 'request_time', 'arrive_time')
#     search_fields = ('user_id__username',)
#     model_icon = 'fa fa-money'
#
#     def get_model_form(self, **kwargs):
#         return TransactionForm
#
# class DepositReview(Transaction):
#     class Meta:
#         verbose_name = 'Deposit Review'
#         verbose_name_plural = verbose_name
#         proxy=True
#
# class DepositReviewAdmin(object):
#     list_display = ('user_id', 'amount', 'request_time', 'review_status', 'remark')
#     list_filter = ('review_status',)
#     model_icon='fa fa-user'
#     search_fields = ['user_id']
#
#     form_layout = (
#         Main(
#             Fieldset("General Info",
#                     'user_id', 'amount', 'status', 'channel', 'request_time', 'arrive_time',
#             ),
#             Fieldset("Review",
#                     'review_status', 'remark',
#             ),
#         ),
#     )
#
#     def queryset(self):
#         deposit = super().queryset()
#         deposit = deposit.filter(transaction_type=0)
#         return deposit
#
#     def get_model_form(self, **kwargs):
#         if self.org_obj is None:
#             self.form = DepositReviewForm
#         else:
#             self.form = DepositReviewForm
#         return super().get_model_form(**kwargs)
#
# class WithdrawReview(Transaction):
#     class Meta:
#         verbose_name = 'Withdraw Review'
#         verbose_name_plural = verbose_name
#         proxy=True
#
# class WithdrawReviewAdmin(object):
#     list_display = ('user_id', 'amount', 'request_time', 'review_status', 'remark')
#     list_filter = ('review_status',)
#     model_icon='fa fa-users'
#     search_fields = ['user_id']
#
#     form_layout = (
#         Main(
#             Fieldset("General Info",
#                     'user_id', 'amount', 'status', 'request_time', 'arrive_time',
#             ),
#             Fieldset("Review",
#                     'review_status', 'remark',
#             ),
#         ),
#     )
#
#     def queryset(self):
#         deposit = super().queryset()
#         deposit = deposit.filter(transaction_type=1)
#         return deposit
#
#     def get_model_form(self, **kwargs):
#         if self.org_obj is None:
#             self.form = WithdrawReviewForm
#         else:
#             self.form = WithdrawReviewForm
#         return super().get_model_form(**kwargs)
#
# class WithdrawChannelAdmin(object):
#     list_display = ('thirdParty_name', 'min_amount', 'max_amount', 'transaction_fee', 'currency', 'switch',)
#     model_icon = 'fa fa-credit-card'
#
# class DepositChannelAdmin(object):
#     list_display = ('thirdParty_name', 'min_amount', 'max_amount', 'currency', 'priority', 'switch',)
#     model_icon = 'fa fa-won'


# class DepositAccessManagementInline(object):
#     model = DepositAccessManagement
#     extra = 1

# class DepositAccessManagementAdmin(object):
#     list_display = ('user_id', 'deposit_channel')
#     model_icon='fa fa-cog'
#     # inlines = [DepositAccessManagementInline,]
#
#     def __str__(self):
#         return '{0}'.format(self.user_id)
#
# class WithdrawAccessManagementAdmin(object):
#     list_display = ('user_id', 'withdraw_channel')
#     model_icon='fa fa-cog'
#     # inlines = [WithdrawAccessManagementAdmin,]
#
#     def __str__(self):
#         return '{0}'.format(self.user_id)
# xadmin.site.register(Transaction,TransactionAdmin)

# xadmin.site.register(DepositChannel,DepositChannelAdmin)
# xadmin.site.register(WithdrawChannel,WithdrawChannelAdmin)
# xadmin.site.register(DepositReview,DepositReviewAdmin)
# xadmin.site.register(WithdrawReview,WithdrawReviewAdmin)
# xadmin.site.register(DepositAccessManagement,DepositAccessManagementAdmin)
# xadmin.site.register(WithdrawAccessManagement,WithdrawAccessManagementAdmin)

