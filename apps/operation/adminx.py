from xadmin import views
import xadmin

from .models import NoticeMessage
from django.utils.translation import ugettext_lazy as _
from extra_app.xadmin.forms import AdminAuthenticationForm

xadmin.site.register(NoticeMessage)
