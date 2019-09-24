from django.contrib import admin
from .models import Notification, CampaignToGroup

# Register your models here.
admin.site.register(Notification)
admin.site.register(CampaignToGroup)