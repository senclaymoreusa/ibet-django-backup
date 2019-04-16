from xadmin import views
import xadmin

from .models import Game, Category
from django.utils.translation import ugettext_lazy as _


# class NoticeAdmin(object):
#     model_icon = 'fa fa-tasks'


xadmin.site.register(Game)
