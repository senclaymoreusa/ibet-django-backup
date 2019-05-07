import xadmin

from .models import Transaction, ThirdParty

class TransactionAdmin(object):
    list_display = ('user_id', 'transaction_type', 'amount', 'status', 'channel', 'request_time')
    
class ThirdPartyAdmin(object):
    list_display = ('thridParty_name', 'min_amount', 'max_amount', 'transaction_fee', 'currency', 'switch',)


xadmin.site.register(Transaction,TransactionAdmin)
xadmin.site.register(ThirdParty,ThirdPartyAdmin)