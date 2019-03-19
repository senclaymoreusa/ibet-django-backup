from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm

from .models import CustomUser
from .models import Language, Category, Status, Game, Config

from .forms import UserCreationForm

class UserAdmin(BaseUserAdmin):
	add_form = UserCreationForm

	list_display = ('username','email','is_admin', 'first_name', 'last_name', 'block')
	list_filter = ('is_admin',)

	fieldsets = (
			(None, {'fields': ('username','email','password', 'first_name', 'last_name', 'phone', 'country', 'date_of_birth', 'street_address_1', 'street_address_2', 'city', 'state', 'zipcode', 'block', 'referral_id', 'referred_by', 'reward_points', 'referred_who')}),
			('Permissions', {'fields': ('is_admin',)})
		)
	search_fields = ('username','email')
	ordering = ('username','email')

	filter_horizontal = ()


admin.site.register(CustomUser, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Language)
admin.site.register(Category)
admin.site.register(Status)
admin.site.register(Game)
admin.site.register(Config)

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username',]

#admin.site.register(CustomUser, CustomUserAdmin)
