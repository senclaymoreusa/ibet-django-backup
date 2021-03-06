from xadmin import views
import xadmin

from .models import Notification, AWSTopic
from .views import NotificationView, NotificationDetailView, MessageUserGroupView, AWSTopicView, AuditNotificationView, CampaignView
from system.models import UserGroup
from django.utils.translation import ugettext_lazy as _

class NoticeAdmin(object):
    model_icon = 'fa fa-tasks'


class NotificationAdmin(object):
    model_icon = 'fa fa-bell'


class MessageGroupAdmin(object):
    model_icon = "fas fa-badge-percent"


class GroupAdmin(object):
    model_icon = 'fab fa-aws'


class AuditAdmin(object):
    model_icon = 'fas fa-tasks'


# import urls
xadmin.site.register_view(r'audit/', AuditNotificationView, name='audit')
xadmin.site.register_view(r'notification-detail/(?P<pk>\d+)/$', NotificationDetailView, name='notification_detail')
xadmin.site.register_view(r'notification-detail/$', NotificationDetailView, name='notification_detail')

xadmin.site.register_view(r'notification/', NotificationView, name='notification')
# xadmin.site.register_view(r'userdetail/(?P<pk>\d+)/$', UserDetailView, name='user_detail')
xadmin.site.register_view(r'awstopic/(?P<pk>\d+)/$', AWSTopicView, name='awstopic')
xadmin.site.register_view(r'awstopic/', AWSTopicView, name='awstopic')
xadmin.site.register_view(r'messagegroups/', MessageUserGroupView, name='messagegroups')
xadmin.site.register_view(r'campaign/', CampaignView, name='campaign')

# xadmin.site.register(Notification, NotificationAdmin)
# xadmin.site.register(UserGroup, MessageGroupAdmin)
# xadmin.site.register(AWSTopic, GroupAdmin)
# xadmin.site.register(Notification, AuditAdmin)