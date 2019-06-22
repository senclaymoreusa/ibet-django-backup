from .models import Transaction
from table import Table
from table.columns import Column

class DepositTable(Table):
    id = Column(field='transaction_id')
    username = Column(field='user_id')
    payment = Column(field='channel')

        class Meta:
            model = Transaction
            ajax = True
            ajax_source = reverse_lazy('table_data')