from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, UserWithTag
from django.forms import ModelForm

from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email']
    
    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return self.cleaned_data

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
	query = forms.CharField(label='Username / Email')
	password = forms.CharField(label='Password', widget=forms.PasswordInput)

	def clean(self, *args, **kwargs):
		query = self.cleaned_data.get('query')
		password = self.cleaned_data.get('password')
		user_qs_final = User.objects.filter(
				Q(username__iexact=query) |
				Q(email__iexact=query)
			).distinct()
		if not user_qs_final.exists() and user_qs_final.count != 1:
			raise forms.ValidationError("Invalid credentials - user does note exist")
		user_obj = user_qs_final.first()
		if not user_obj.check_password(password):
			raise forms.ValidationError("credentials are not correct")
		self.cleaned_data["user_obj"] = user_obj
		return super(UserLoginForm, self).clean(*args, **kwargs)

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'user_tag')


from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime #for checking renewal date range.

class RenewBookForm(forms.Form):
    """
    Form for a librarian to renew books.
    """
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        #Check date is not in past.
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))
        #Check date is in range librarian allowed to change (+4 weeks)
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data





# from django.contrib.auth.forms import AuthenticationForm

# class AuthenticationFormWithChekUsersStatus(AuthenticationForm):
#     def confirm_login_allowed(self, user):
#         if not user.status == 'enabled':
#             raise forms.ValidationError(
#                 ("Your account has disabled."),
#                 code='inactive',
#             )


class userWithTagCreationForm(ModelForm):

    class Meta:
        model = UserWithTag
        fields = ('user', 'tag')


class userWithTagEditForm(forms.ModelForm):
    class Meta:
        model = UserWithTag
        fields = ('tag', 'user', 'status', )

    def __init__(self, *args, **kwargs):
        super(userWithTagEditForm, self).__init__(*args, **kwargs)
        self.fields['tag'].disabled = True
        self.fields['user'].disabled = True
        # self.fields['status'].disabled = True
    
    def has_add_permission(self):
        return False