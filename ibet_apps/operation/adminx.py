from xadmin import views
import xadmin

from .models import NoticeMessage, Notification
from django.utils.translation import ugettext_lazy as _


class NoticeAdmin(object):
    model_icon = 'fa fa-tasks'


class NotificationAdmin(object):
    model_icon = 'fa fa-bell'


# import urls
from .views import NotificationView
# xadmin.site.register_view(r'noti', NotificationView, name="notification_list")

xadmin.site.register(NoticeMessage, NoticeAdmin)
xadmin.site.register(Notification, NotificationAdmin)