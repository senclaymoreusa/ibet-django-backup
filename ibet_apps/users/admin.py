from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm

from .models import CustomUser
from .models import Language, Category, Status, Game, Config, NoticeMessage, Bonus, BonusRequirement, UserBonus, GBSportWalletBet, BetKenoList, BetKenoBalls, GBSportWalletSettle, SettleKenoList, SettleKenoBalls, AGGamemodels
from .forms import UserCreationForm

class UserAdmin(BaseUserAdmin):
	add_form = UserCreationForm

	list_display = ('username','email','is_admin', 'first_name', 'last_name', 'block')
	list_filter = ('is_admin',)

	fieldsets = (
			(None, {'fields': ('username','email','password', 'first_name', 'last_name', 'phone', 'country', 'date_of_birth', 'street_address_1', 'street_address_2', 'city', 'state', 'zipcode', 'language', 'block', 'referral_id', 'referred_by', 'reward_points', 'main_wallet', 'active', 'activation_code', 'gender', 'title', 'over_eighteen', 'odds_display', 'preferred_team', 'contact_option', 'deposit_limit', 'promo_code', 'currency', 'reset_password_code')}),
			('Permissions', {'fields': ('is_admin', 'is_staff')})
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
admin.site.register(NoticeMessage)
admin.site.register(Bonus)
admin.site.register(BonusRequirement)
admin.site.register(UserBonus)
admin.site.register(GBSportWalletBet)
admin.site.register(BetKenoList)
admin.site.register(BetKenoBalls)
admin.site.register(GBSportWalletSettle)
admin.site.register(SettleKenoList)
admin.site.register(SettleKenoBalls)
admin.site.register(AGGamemodels)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username',]

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django import forms
from django.forms.widgets import PasswordInput, TextInput
from django.utils.translation import gettext as _, gettext_lazy


class CustomizedAuthenticationForm(AuthenticationForm):

    username = forms.CharField(label=_("username") ,widget=TextInput())
    password = forms.CharField(label=_("password") ,widget=PasswordInput())
    remember_me = forms.BooleanField(required=False, initial=False)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        remember = self.cleaned_data.get('remember_me')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

admin.site.login_form = CustomizedAuthenticationForm

