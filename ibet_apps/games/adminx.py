from xadmin import views
import xadmin

from .models import Game, Category
from django.utils.translation import ugettext_lazy as _


class GameAdmin(object):
    model_icon = 'fa fa-gamepad'


xadmin.site.register(Game, GameAdmin)