from xadmin import views
import xadmin

from .models import NoticeMessage, Notification, AWSTopic
from .views import NotificationView, NotificationDetailView, AWSTopicView
from django.utils.translation import ugettext_lazy as _


class NoticeAdmin(object):
    model_icon = 'fa fa-tasks'


class NotificationAdmin(object):
    model_icon = 'fa fa-bell'


class AWSTopicAdmin(object):
    model_icon = 'fa fa-cloud'


# import urls
xadmin.site.register_view(r'notification-detail/(?P<pk>\d+)/$', NotificationDetailView, name='notification_detail')
xadmin.site.register_view(r'notification-detail/$', NotificationDetailView, name='notification_detail')

xadmin.site.register_view(r'notification/', NotificationView, name='notification')
# xadmin.site.register_view(r'userdetail/(?P<pk>\d+)/$', UserDetailView, name='user_detail')

xadmin.site.register_view(r'group/', AWSTopicView, name='notification_group')

xadmin.site.register(NoticeMessage, NoticeAdmin)
xadmin.site.register(Notification, NotificationAdmin)
xadmin.site.register(AWSTopic, AWSTopicAdmin)