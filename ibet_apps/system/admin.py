from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(UserGroup)
admin.site.register(PermissionGroup)
admin.site.register(UserToUserGroup)
admin.site.register(UserPermission)