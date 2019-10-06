import xadmin
from .models import Bonus

class BonusAdmin(object):
    list_display = ('name', 'description', 'start_time', 'end_time', 'expiration_days','countries','amount','percentage','coupon_code',
                    'is_free_bid','status','type','campaign','affiliate_limit','release_type','image_s3')








xadmin.site.register(Bonus,BonusAdmin)
