from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm

from .models import CustomUser
from .models import Language, Category, Status, Game, Config, NoticeMessage
from .forms import UserCreationForm

class UserAdmin(BaseUserAdmin):
	add_form = UserCreationForm

	list_display = ('username','email','is_admin', 'first_name', 'last_name', 'block')
	list_filter = ('is_admin',)

	fieldsets = (
			(None, {'fields': ('username','email','password', 'first_name', 'last_name', 'phone', 'country', 'date_of_birth', 'street_address_1', 'street_address_2', 'city', 'state', 'zipcode', 'block', 'referral_id', 'referred_by', 'reward_points', 'balance', 'active', 'activation_code')}),
			('Permissions', {'fields': ('is_admin', 'is_staff')})
		)
	search_fields = ('username','email')
	ordering = ('username','email')

	filter_horizontal = ()

from django.contrib.admin import AdminSite
from django.views.decorators.cache import never_cache
from django.utils.translation import gettext as _, gettext_lazy
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse


# class CustomizedAdminSite(AdminSite):
#     @never_cache
#     def login(self, request, extra_context=None):
#         """
#         Display the login form for the given HttpRequest.
#         """
#         if request.method == 'GET' and self.has_permission(request):
#             # Already logged-in, redirect to admin index
#             index_path = reverse('admin:index', current_app=self.name)
#             return HttpResponseRedirect(index_path)

#         # Since this module gets imported in the application's root package,
#         # it cannot import models from other applications at the module level,
#         # and django.contrib.admin.forms eventually imports User.
#         # from django.contrib.admin.forms import AdminAuthenticationForm
#         context = {
#             **self.each_context(request),
#             'title': _('Log in'),
#             'app_path': request.get_full_path(),
#             'username': request.user.get_username(),
#         }
#         if (REDIRECT_FIELD_NAME not in request.GET and
#                 REDIRECT_FIELD_NAME not in request.POST):
#             context[REDIRECT_FIELD_NAME] = reverse('admin:index', current_app=self.name)
#         # context.update(extra_context)

#         defaults = {
#             'extra_context': context,
#             'authentication_form': CustomizedAuthenticationForm,
#             'template_name': self.login_template or 'admin/login.html',
#         }
#         request.current_app = self.name
#         return CustomizedLoginView.as_view(**defaults)(request)

# adminSite = CustomizedAdminSite()
admin.site.register(CustomUser, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Language)
admin.site.register(Category)
admin.site.register(Status)
admin.site.register(Game)
admin.site.register(Config)
admin.site.register(NoticeMessage)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username',]

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django import forms
from django.forms.widgets import PasswordInput, TextInput    

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


