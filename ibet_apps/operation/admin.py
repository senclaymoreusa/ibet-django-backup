from django.contrib import admin
from .models import Notification, Campaign, CampaignToGroup

# Register your models here.
admin.site.register(Notification)
admin.site.register(Campaign)
admin.site.register(CampaignToGroup)
