from django.contrib import admin
from accounting.models import *

# Register your models here.
admin.site.register(Transaction)
admin.site.register(DepositChannel)
admin.site.register(WithdrawChannel)

