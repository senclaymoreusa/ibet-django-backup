import xadmin

from .models import *
from bonus.adminview import *

class BonusAdmin(object):
    list_display = ('name', 'description', 'start_time', 'end_time', 'expiration_days','countries','amount','percentage','coupon_code',
                    'is_free_bid','status','type','campaign','affiliate_limit','release_type','image_s3')

class RequirementAdmin(object):
    list_display = ('field_name', 'aggregate_method', 'time_limit', 'turnover_multiplier', 'amount_threshold')

class UserBonusEventAdmin(object):
    list_display = ('owner', 'bonus', 'timestamp', 'delivered_by', 'status', 'notes')

class BonusCategoryAdmin(object):
    list_display = ('bonus', 'category')


# xadmin.site.register(Bonus,BonusAdmin)
# xadmin.site.register(Requirement,RequirementAdmin)
# xadmin.site.register(UserBonusEvent,UserBonusEventAdmin)
# xadmin.site.register(BonusCategory,BonusCategoryAdmin)

xadmin.site.register_view(r'bonus_records/$', BonusRecordsView, name='bonus_records')
xadmin.site.register_view(r'bonus_transactions/$', BonusTransactionsView, name='bonus_transactions')
