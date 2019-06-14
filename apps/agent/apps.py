from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AgentConfig(AppConfig):
    name = 'agent'
    verbose_name = _('Agent System')

