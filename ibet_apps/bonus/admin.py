from django.contrib import admin
from bonus.models import *

# Register your models here.
admin.site.register(Bonus)
admin.site.register(Requirement)
admin.site.register(UserBonusEvent)
