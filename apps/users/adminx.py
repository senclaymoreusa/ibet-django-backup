from xadmin import views
import xadmin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import  CustomUser, UserTag, UserWithTag, Category
from .forms import UserCreationForm, CustomUserChangeForm, userWithTagCreationForm
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

from django.contrib import admin
class UserWithTagInline(object):
    model = UserWithTag
    extra = 1

# 用户的后台管理
from .admin import UserAdmin
class MyUserAdmin(object):
    # add_form = UserCreationForm
    # form = CustomUserCreationForm
    list_display = ('username','email','is_admin', 'first_name', 'last_name', 'block', 'get_approved_tag')
    list_filter = ('is_admin', 'user_tag')

    fieldsets = (
        (None, {'fields': ('username','email','password', 'first_name', 'last_name', 'phone', 'country', 'date_of_birth', 'street_address_1', 'street_address_2', 'city', 'state', 'zipcode', 'block', 'referral_id', 'referred_by', 'reward_points', 'balance', 'active', 'activation_code')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff')})
    )
    search_fields = ('username','email', 'user_tag__name')
    ordering = ('username','email')

    filter_horizontal = ()
    model_icon = 'fa fa-user fa-fw'
    inlines = (UserWithTagInline,)
    
    def get_model_form(self, **kwargs):
        if self.org_obj is None:
            self.form = UserCreationForm
        else:
            self.form = CustomUserChangeForm
        return super(MyUserAdmin, self).get_model_form(**kwargs)

    def get_approved_tag(self, obj):
        user_with_tags = UserWithTag.objects.filter(user=obj, status=1)
        tag_names = []
        for user_with_tag in user_with_tags:
            tag_names.append(user_with_tag.tag.name)
        return ', '.join(tag_names)

    get_approved_tag.short_description = 'User Tag'
    get_approved_tag.admin_order_field = 'UserWithTag__user'


class TagAdmin(object):
    
    list_display = ('name', 'notes')
    model_icon = 'fa fa-tags'


class UserWithTagAdmin(object):
    

    def make_approved(modeladmin, request, queryset):
        queryset.update(status=1)
    make_approved.short_description = "Approved tag assign to user"

    list_display = ('user','tag','get_status')
    list_filter = ('user', 'tag', 'status')
    model_icon = 'fa fa-tag'
    actions = [make_approved]
    search_fields = ('user__username', 'tag__name')

    def get_status(self, obj):
        return obj.get_status_display()
    get_status.short_description = _('Status')
    get_status.admin_order_field = 'status'
    # readonly_fields = ('get_status_display',)

    def get_model_form(self, **kwargs):
        if self.org_obj is None:
            self.form = userWithTagCreationForm
        # else:
        #     self.form = CustomUserChangeForm
        return super(UserWithTagAdmin, self).get_model_form(**kwargs)


    
xadmin.site.register(views.CommAdminView, GlobalSettings)
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.unregister(CustomUser)
xadmin.site.unregister(Group)
xadmin.site.register(CustomUser, MyUserAdmin)
xadmin.site.register(UserTag,TagAdmin)
xadmin.site.register(UserWithTag,UserWithTagAdmin)

xadmin.site.login_form = AdminAuthenticationForm