import xadmin

from .models import Transaction

class TransactionAdmin(object):
    list_display = ('user_id', 'transaction_type', 'amount', 'status', 'channel', 'request_time')

xadmin.site.register(Transaction,TransactionAdmin)