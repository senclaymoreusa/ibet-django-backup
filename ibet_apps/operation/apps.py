from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OperationConfig(AppConfig):
    name = 'operation'

    verbose_name = _('Operation System')