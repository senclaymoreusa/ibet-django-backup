from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Category)
admin.site.register(Game)
admin.site.register(GameAttribute)
admin.site.register(FGSession)