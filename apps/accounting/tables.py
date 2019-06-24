from .models import Transaction
from table import Table
from table.columns import Column
from django.urls import reverse_lazy

class DepositTable(Table):
    username = Column(field='user_id')
    payment = Column(field='channel')
    transaction_no = Column(field='transaction_id')

    class Meta:
        model = Transaction
        ajax = True
        ajax_source = reverse_lazy('table_data')