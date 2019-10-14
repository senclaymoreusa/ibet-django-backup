from xadmin import views
import xadmin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import  CustomUser, UserTag, UserWithTag, Category, UserAction
from .forms import UserCreationForm, CustomUserChangeForm, userWithTagCreationForm, userWithTagEditForm
from users.views.adminview import *
from users.views.views import *
from users.views.agentview import *
from users.views.vipview import *
from django.utils.translation import ugettext_lazy as _
from extra_app.xadmin.forms import AdminAuthenticationForm
import datetime
from django.contrib.admin import SimpleListFilter
from django.conf import settings
# from xadmin.layout import Main, Fieldset, Row
from xadmin.layout import *
from xadmin.plugins.inline import Inline
from django.contrib.auth.models import Permission


DOMAIN = settings.DOMAIN


class BaseSetting(object):
    # enable_themes = True    # 使用主题
    use_bootswatch = True

# 全局设置
class GlobalSettings(object):
    site_title = _('iBet Administration') 
    site_footer = 'iBet'  
    site_url = '/'
    menu_style = 'accordion'  
    def get_site_menu(self): 
        return [
            {
                'title': _('Players'),
                'icon': 'fa fa-user fa-fw',
                'menus': (
                    {
                        'title': _('Player directory'),
                        'url': '/xadmin/users',
                        'icon': 'fas fa-book'
                    },
                    {
                        'title':  _('Player groups'),
                        'url': '/xadmin/operation/messagegroups/',
                        'icon': 'fas fa-user-friends'
                    },
                )
            },
            {
                'title': _('Affiliate'),
                'icon': 'fa fa-smile-o',
                'url': '/xadmin/agentview',
            },
            {
                'title': _('Marketing'),
                'icon': 'fa fa-bullhorn',
                'menus': (
                    {
                        'title': _('VIP Management'),
                        'url': '/xadmin/vip',
                        'icon': 'fa fa-diamond'
                    },
                    # {
                    #     'title': _('Referral Program'),
                    #     'icon': 'fa fa-thumbs-o-up'
                    # },
                    # {
                    #     'title': _('Media Channels'),
                    #     'icon': 'fa fa-share-square-o'
                    # },
                    # {
                    #     'title': _('Segmentation Settings'),
                    #     'icon': 'fa fa-cogs'
                    # },
                )
            },
            {
                'title': _('Finance'),
                'icon': 'fa fa-credit-card',
                'menus': (
                    {
                        'title': _('Deposits'),
                        'url': '/xadmin/deposit',
                        'icon': 'fa fa-arrow-right'
                    },
                    {
                        'title': _('Withdrawals'),
                        'url': '/xadmin/withdrawal',
                        'icon': 'fa fa-arrow-left'
                    },
                    {
                        'title': _('Settings'),
                        'url': '/xadmin/channel_list',
                        'icon': 'fa fa-cog'
                    },
                )
            },
            {
                'title': _('System admin'),
                'icon': 'fa-fw fa fa-cog',
                'menus': (
                    {
                        'title': _('Users'),
                        'url': '/xadmin/permission/',
                        'icon': 'fa fa-user-circle-o'
                    },
                    {
                        'title': _('Roles'),
                        'url': '/xadmin/roles/',
                        'icon': 'fa fa-id-badge'
                    },
                )
            },
            {
                'title': 'Reports',
                'icon': 'fas fa-file-medical-alt',
                'menus': (
                    {
                        'title': 'Performance reports',
                        'url': '/xadmin/performance-report/',
                        'icon': 'fas fa-file-alt'
                    },
                    {
                        'title': 'Members reports',
                        'url': '/xadmin/members-report/',
                        'icon': 'fas fa-users'
                    },
                )
            },
            {
                'title': 'Messaging',
                'icon': 'far fa-envelope',
                'menus': (
                    {
                        'title': _('Messages'),
                        'url': '/xadmin/operation/notification/',
                        'icon': 'far fa-envelope'
                    },
                    {
                        'title': _('Campaign'),
                        'url': '/xadmin/operation/campaign/',
                        'icon': 'fas fa-bullhorn'
                    }
                )
            },
        ]
                    
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


    list_display = ('username','email','is_admin', 'block', 'get_approved_tag', 'login_count', 'bet_count', 'deposit_count', 'withdraw_count', 'bet_count',  'user_action_link', 'user_deposit_channel', 'user_withdraw_channel','time_of_registration', 'ftd_time', 'verfication_time', 'modified_time', 'last_login_time', 'last_login_ip')
    list_filter = ('is_admin', 'user_tag', 'useraction__created_time',)

    # fieldsets = (
    #     (None, {'fields': ('username','email','password', 'first_name', 'last_name', 'phone', 'country', 'date_of_birth', 'street_address_1', 'street_address_2', 'city', 'state', 'zipcode', 'block', 'referral_id', 'referred_by', 'reward_points', 'balance', 'active', 'activation_code')}),
    #     ('Permissions', {'fields': ('is_admin', 'is_staff')})
    # )

    search_fields = ('username','email', 'user_tag__name')
    ordering = ('username','email',)
    # list_editable = 'username'
    # readonly_fields = ('username',)

    filter_horizontal = ()
    model_icon = 'fa fa-user fa-fw'
    inlines = (UserWithTagInline,)
    list_per_page = 20
    # refresh_times = [3,5] 

    form_layout = (
        Main(
            TabHolder(
                Tab('User Info',
                    Fieldset('General Info',
                            'username', 'member_status', 'user_attribute',
                            Row('email', 'phone'),
                            description="User Detail",
                    ),
                    Fieldset('Balance',
                            'main_wallet', 'other_game_wallet',
                    ),
                    Inline(UserWithTag),
                    
                ),
                Tab('User Detail',
                    Fieldset('Last',
                            'first_name', 'last_name',
                    ),
                ),
            )
            
        ),
    )

    
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

    def last_login_ip(self, obj):
        qs = UserAction.objects.filter(user=obj, event_type=0).order_by('-created_time')
        if qs.count() == 0:
            return None
        return qs[0].ip_addr

    def save_models(self):
        obj = self.new_obj
        super().save_models()
    
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

    list_display = ('user','event_type', 'ip_addr', 'created_time', 'user_action_link')
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



# from .views import UserDetailView, UserListView
xadmin.site.register_view(r'userdetail/(?P<pk>\d+)/$', UserDetailView, name='user_detail')
xadmin.site.register_view(r'userdetail/$', UserDetailView, name='user_detail')
xadmin.site.register_view(r'users/', UserListView, name='user_list')
xadmin.site.register_view(r'profile/', UserProfileView, name='user_profile')

from xadmin.views import CommAdminView
# xadmin.site.register(CommAdminView, GlobalSettings)


xadmin.site.register(views.CommAdminView, GlobalSettings)
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.unregister(CustomUser)
xadmin.site.unregister(Group)
xadmin.site.unregister(Permission)
# xadmin.site.register(CustomUser, MyUserAdmin)
# xadmin.site.register(UserTag,TagAdmin)
# xadmin.site.register(UserWithTag,UserWithTagAdmin)
# xadmin.site.register(UserAction, UserActionAdmin)
xadmin.site.login_form = AdminAuthenticationForm

# AGENT
xadmin.site.register_view(r'agentview/$', AgentView, name='agentview')
xadmin.site.register_view(r'agentdetail/$', AgentDetailView, name='agent_detail')
xadmin.site.register_view(r'agentdetail/(?P<pk>\d+)/$', AgentDetailView, name='agent_detail')

# VIP
xadmin.site.register_view(r'vip/$', VIPView, name='vipview')