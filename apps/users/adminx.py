from xadmin import views
import xadmin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import  CustomUser, UserTag, UserWithTag, Category, UserAction
from .forms import UserCreationForm, CustomUserChangeForm, userWithTagCreationForm, userWithTagEditForm
from django.utils.translation import ugettext_lazy as _
from extra_app.xadmin.forms import AdminAuthenticationForm
import datetime
from django.contrib.admin import SimpleListFilter
from django.conf import settings

DOMAIN = settings.DOMAIN


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
    # exclude = ('tag',)
    
# 用户的后台管理
from .admin import UserAdmin
class MyUserAdmin(object):
    # add_form = UserCreationForm
    # form = CustomUserCreationForm

    list_display = ('username','email','is_admin', 'first_name', 'last_name', 'block', 'get_approved_tag', 'login_count', 'bet_count', 'deposit_count', 'withdraw_count', 'bet_count',  'user_action_link')
    list_filter = ('is_admin', 'user_tag', 'useraction__created_time',)

    fieldsets = (
        (None, {'fields': ('username','email','password', 'first_name', 'last_name', 'phone', 'country', 'date_of_birth', 'street_address_1', 'street_address_2', 'city', 'state', 'zipcode', 'block', 'referral_id', 'referred_by', 'reward_points', 'balance', 'active', 'activation_code')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff')})
    )
    search_fields = ('username','email', 'user_tag__name')
    ordering = ('username','email',)
    # list_editable = 'username'
    # readonly_fields = ('username',)

    filter_horizontal = ()
    model_icon = 'fa fa-user fa-fw'
    inlines = (UserWithTagInline,)
    list_per_page = 20
    # refresh_times = [3,5] 
    
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

    get_approved_tag.short_description = _('User Tag')
    get_approved_tag.admin_order_field = 'UserWithTag__user'

    def login_count(self, obj):
        qs = UserAction.objects.filter(user=obj, event_type=0)
        return qs.count()

    login_count.short_description = _("Login")

    def deposit_count(self, obj):
        qs = UserAction.objects.filter(user=obj, event_type=3)
        return qs.count()

    deposit_count.short_description = _("Deposit")

    def withdraw_count(self, obj):
        qs = UserAction.objects.filter(user=obj, event_type=4)
        return qs.count()

    withdraw_count.short_description = _("Withdraw")
    

    def bet_count(self, obj):
        qs = UserAction.objects.filter(user=obj, event_type=6)
        return qs.count()

    bet_count.short_description = _("Bet")

    def user_action_link(self, obj):
        msg = _("More actions for this user")
        return ('<a href="%s">' + str(msg) + '</a>') % (DOMAIN + 'xadmin/users/useraction/?_p_user__id__exact=' + str(obj.id))
    user_action_link.allow_tags = True
    user_action_link.short_description = _("User action link")
    


class TagAdmin(object):
    
    list_display = ('name', 'notes')
    model_icon = 'fa fa-tags'


class UserWithTagAdmin(object):
    

    def make_approved(modeladmin, request, queryset):
        queryset.update(status=1)
    make_approved.short_description = _("Approved tag assign to user")

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
        else:
            self.form = userWithTagEditForm
        return super(UserWithTagAdmin, self).get_model_form(**kwargs)


class UserActionAdmin(object):

    list_display = ('user','event_type', 'ip_addr','dollar_amount', 'created_time', 'user_action_link')
    list_filter = ('user', 'event_type', 'created_time')
    model_icon = 'fa fa-cogs'
    search_fields = ('user__username', 'event_type',)
    list_per_page = 20

    def __init__(self, *args, **kwargs):
        super(UserActionAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def user_action_link(self, obj):
        msg = _("More actions for this user")
        return ('<a href="%s">' + str(msg) + '</a>') % (DOMAIN + 'xadmin/users/useraction/?_p_user__id__exact=' + str(obj.user.id))
    user_action_link.allow_tags = True
    user_action_link.short_description = _("User action link")


xadmin.site.register(views.CommAdminView, GlobalSettings)
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.unregister(CustomUser)
xadmin.site.unregister(Group)
xadmin.site.register(CustomUser, MyUserAdmin)
xadmin.site.register(UserTag,TagAdmin)
xadmin.site.register(UserWithTag,UserWithTagAdmin)
xadmin.site.register(UserAction, UserActionAdmin)
xadmin.site.login_form = AdminAuthenticationForm