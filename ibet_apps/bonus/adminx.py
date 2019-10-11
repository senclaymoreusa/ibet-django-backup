import xadmin
from .models import Bonus
from .models import Requirement

class BonusAdmin(object):
    list_display = ('name', 'description', 'start_time', 'end_time', 'expiration_days','countries','amount','percentage','coupon_code',
                    'is_free_bid','status','type','campaign','affiliate_limit','release_type','image_s3')

class RequirementAdmin(object):
    list_display = ('field_name', 'aggregate_method', 'time_limit', 'turnover_multiplier', 'amount_threshold')

xadmin.site.register(Bonus,BonusAdmin)
xadmin.site.register(Requirement,RequirementAdmin)
