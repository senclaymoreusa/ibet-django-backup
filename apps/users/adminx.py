from xadmin import views
import xadmin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import  CustomUser, UserTag, Category
from .forms import UserCreationForm, CustomUserChangeForm
from django.utils.translation import ugettext_lazy as _
from extra_app.xadmin.forms import AdminAuthenticationForm


class BaseSetting(object):
    enable_themes = True    # 使用主题
    use_bootswatch = True

# 全局设置
class GlobalSettings(object):
    site_title = _('IBET Administration')  # 标题
    site_footer = 'Ibet'  # 页尾
    site_url = '/'
    menu_style = 'accordion'  # 设置左侧菜单  折叠样式

# 用户的后台管理
from .admin import UserAdmin
class MyUserAdmin(object):
    # add_form = UserCreationForm
    # form = CustomUserCreationForm
    list_display = ('username','email','is_admin', 'first_name', 'last_name', 'block')
    list_filter = ('is_admin',)

    fieldsets = (
        (None, {'fields': ('username','email','password', 'first_name', 'last_name', 'phone', 'country', 'date_of_birth', 'street_address_1', 'street_address_2', 'city', 'state', 'zipcode', 'block', 'referral_id', 'referred_by', 'reward_points', 'balance', 'active', 'activation_code')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff')})
    )
    search_fields = ('username','email')
    ordering = ('username','email')

    filter_horizontal = ()
    model_icon = 'fa fa-user fa-fw'
    
    def get_model_form(self, **kwargs):
        if self.org_obj is None:
            self.form = UserCreationForm
        # else:
        #     self.form = CustomUserChangeForm
        return super(MyUserAdmin, self).get_model_form(**kwargs)



class TagAdmin(object):
    
    model_icon = 'fa fa-tag'


xadmin.site.register(views.CommAdminView, GlobalSettings)
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.unregister(CustomUser)
xadmin.site.unregister(Group)
xadmin.site.register(CustomUser, MyUserAdmin)
xadmin.site.register(UserTag,TagAdmin)

xadmin.site.login_form = AdminAuthenticationForm