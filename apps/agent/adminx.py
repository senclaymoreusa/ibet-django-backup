import xadmin

from users.models import CustomUser
from .models import Agent

class AgentAdmin(object):
    list_display = ('username','active_user')

    #find all downline

class CommisionAdmin(object):
    


xadmin.site.register(Agent, AgentAdmin)