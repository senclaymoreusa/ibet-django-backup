import xadmin

from .models import Transaction, ThirdParty

class TransactionAdmin(object):
    list_display = ('user_id', 'transaction_type', 'amount', 'status', 'channel', 'request_time', 'arrive_time')
    list_filter = ('transaction_type', 'status', 'channel', 'request_time', 'arrive_time')

    search_fields = ('user_id__username',)
    
class ThirdPartyAdmin(object):
    list_display = ('thridParty_name', 'min_amount', 'max_amount', 'transaction_fee', 'currency', 'switch',)

class Deposit(Transaction):
    class Meta:
        verbose_name = 'Deposit Review'
        verbose_name_plural = verbose_name
        proxy=True

class DepositAdmin(object):
    list_display = ('user_id', 'channel', 'amount', 'request_time')
    search_fields = ['user_id']
    def queryset(self):
        deposit = super().queryset()
        deposit = deposit.filter(transaction_type=0)
        return deposit

class Withdraw(Transaction):
    class Meta:
        verbose_name = 'Withdraw Review'
        verbose_name_plural = verbose_name
        proxy=True

class WithdrawAdmin(object):
    list_display = ('user_id', 'channel', 'amount', 'request_time')
    search_fields = ['user_id']
    def queryset(self):
        deposit = super().queryset()
        deposit = deposit.filter(transaction_type=1)
        return deposit

xadmin.site.register(Transaction,TransactionAdmin)
xadmin.site.register(ThirdParty,ThirdPartyAdmin)
xadmin.site.register(Deposit,DepositAdmin)
xadmin.site.register(Withdraw,WithdrawAdmin)