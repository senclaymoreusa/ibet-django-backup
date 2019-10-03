import xadmin
from .models import Bonus



class BonusAdmin(object):
    list_display = ('name', 'description', 'start_time', 'end_time', 'expiration_days', 'is_valid','countries','amount','percentage','coupon_code','is_free_bid')
    model_icon = 'fa fa-money'

# xadmin.site.register(Bonus,BonusAdmin)