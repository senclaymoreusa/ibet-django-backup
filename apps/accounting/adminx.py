import xadmin
from xadmin.layout import Main, Side, Fieldset

from .models import Transaction, DepositAccessManagement, DepositChannel, WithdrawAccessManagement, WithdrawChannel
from .forms import DepositReviewForm, WithdrawReviewForm, TransactionForm

class TransactionAdmin(object):
    list_display = ('user_id', 'transaction_type', 'amount', 'status', 'channel', 'request_time', 'arrive_time', 'review_status', 'remark')
    list_filter = ('transaction_type', 'status', 'channel', 'review_status', 'request_time', 'arrive_time')
    search_fields = ('user_id__username',)
    model_icon = 'fa fa-money'

    def get_model_form(self, **kwargs):
        return TransactionForm

class DepositReview(Transaction):
    class Meta:
        verbose_name = 'Deposit Review'
        verbose_name_plural = verbose_name
        proxy=True

class DepositReviewAdmin(object):
    list_display = ('user_id', 'channel', 'amount', 'request_time', 'review_status', 'remark')
    list_filter = ('channel', 'review_status',)
    model_icon='fa fa-user'
    search_fields = ['user_id']

    form_layout = (
        Main(
            Fieldset("General Info",
                    'user_id', 'amount', 'status', 'channel', 'request_time', 'arrive_time',
            ),
            Fieldset("Review",
                    'review_status', 'remark',
            ),
        ),
    )

    def queryset(self):
        deposit = super().queryset()
        deposit = deposit.filter(transaction_type=0)
        return deposit
    
    def get_model_form(self, **kwargs):
        if self.org_obj is None:
            self.form = DepositReviewForm
        else:
            self.form = DepositReviewForm
        return super().get_model_form(**kwargs)

class WithdrawReview(Transaction):
    class Meta:
        verbose_name = 'Withdraw Review'
        verbose_name_plural = verbose_name
        proxy=True

class WithdrawReviewAdmin(object):
    list_display = ('user_id', 'channel', 'amount', 'request_time', 'review_status', 'remark')
    list_filter = ('channel', 'review_status',)
    model_icon='fa fa-users'
    search_fields = ['user_id']

    form_layout = (
        Main(
            Fieldset("General Info",
                    'user_id', 'amount', 'status', 'channel', 'request_time', 'arrive_time',
            ),
            Fieldset("Review",
                    'review_status', 'remark',
            ),
        ),
    )

    def queryset(self):
        deposit = super().queryset()
        deposit = deposit.filter(transaction_type=1)
        return deposit
    
    def get_model_form(self, **kwargs):
        if self.org_obj is None:
            self.form = WithdrawReviewForm
        else:
            self.form = WithdrawReviewForm
        return super().get_model_form(**kwargs)

class WithdrawChannelAdmin(object):
    list_display = ('thridParty_name', 'min_amount', 'max_amount', 'transaction_fee', 'currency', 'switch',)
    model_icon = 'fa fa-credit-card'

class DepositChannelAdmin(object):
    list_display = ('thridParty_name', 'min_amount', 'max_amount', 'currency', 'priority', 'switch',)
    model_icon = 'fa fa-won'


# class DepositAccessManagementInline(object):
#     model = DepositAccessManagement
#     extra = 1

class DepositAccessManagementAdmin(object):
    list_display = ('user_id', 'deposit_channel')
    model_icon='fa fa-cog'
    # inlines = [DepositAccessManagementInline,]

    def __str__(self):
        return '{0}'.format(self.user_id)

class WithdrawAccessManagementAdmin(object):
    list_display = ('user_id', 'withdraw_channel')
    model_icon='fa fa-cog'
    # inlines = [WithdrawAccessManagementAdmin,]

    def __str__(self):
        return '{0}'.format(self.user_id)

xadmin.site.register(Transaction,TransactionAdmin)

xadmin.site.register(DepositChannel,DepositChannelAdmin)
xadmin.site.register(WithdrawChannel,WithdrawChannelAdmin)
xadmin.site.register(DepositReview,DepositReviewAdmin)
xadmin.site.register(WithdrawReview,WithdrawReviewAdmin)
xadmin.site.register(DepositAccessManagement,DepositAccessManagementAdmin)
xadmin.site.register(WithdrawAccessManagement,WithdrawAccessManagementAdmin)


