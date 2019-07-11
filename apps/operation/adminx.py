from xadmin import views
import xadmin

from .models import NoticeMessage, Notification, AWSTopic
from .views import NotificationView
from django.utils.translation import ugettext_lazy as _


class NoticeAdmin(object):
    model_icon = 'fa fa-tasks'


class NotificationAdmin(object):
    model_icon = 'fa fa-bell'


class AWSTopicAdmin(object):
    model_icon = 'fa fa-cloud'


# import urls
from .views import NotificationView
xadmin.site.register_view(r'notification/', NotificationView, name='notification')
# xadmin.site.register_view('notidication/')
# xadmin.site.register_view(r'agent_view/$', AgentView, name='agent_view')

xadmin.site.register(NoticeMessage, NoticeAdmin)
xadmin.site.register(Notification, NotificationAdmin)
xadmin.site.register(AWSTopic, AWSTopicAdmin)