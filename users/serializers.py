from rest_framework import serializers
from users.models import Game, Book, Author, Category, BookInstance, CustomUser

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'notes', 'category_id', 'parent_id')

class CategorySerializer(serializers.ModelSerializer):
    parent_id = SubCategorySerializer(read_only=True)
    class Meta:
        model = Category
        fields = ('parent_id', 'name', 'notes', 'category_id')
        
class GameSerializer(serializers.ModelSerializer):
    category_id = CategorySerializer(read_only=True)
    class Meta:
        model = Game
        fields = ('category_id', 'name', 'description', 'start_time', 'end_time', 'opponent1', 'opponent2', 'status_id')

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('first_name', 'last_name', 'date_of_birth', 'date_of_death')

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = Book
        fields = ('title', 'author', 'summary')

class BookInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookInstance
        fields = '__all__'

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('pk', 'username', 'email', 'first_name', 'last_name', 'phone', 'country', 'date_of_birth', 'street_address_1', 'street_address_2', 'city', 'state', 'zipcode', 'block')
        read_only_fields = ('username', )

from allauth.account import app_settings as allauth_settings
from allauth.utils import (email_address_exists, get_username_max_length)
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.base import AuthProcess
from rest_framework import serializers, exceptions


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    date_of_birth = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    street_address_1 = serializers.CharField(required=False)
    street_address_2 = serializers.CharField(required=False)
    city = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    zipcode = serializers.CharField(required=True)
    
    
    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."))
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),

            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'phone': self.validated_data.get('phone', ''),
            'date_of_birth': self.validated_data.get('date_of_birth', ''),
            'street_address_1': self.validated_data.get('street_address_1', ''),
            'street_address_2': self.validated_data.get('street_address_2', ''),
            'city': self.validated_data.get('city', ''),
            'country': self.validated_data.get('country', ''),
            'state': self.validated_data.get('state', ''),
            'zipcode': self.validated_data.get('zipcode', ''),
            
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])

        user.phone= self.cleaned_data.get('phone')
        user.date_of_birth = self.cleaned_data.get('date_of_birth')
        user.street_address_1 = self.cleaned_data.get('street_address_1')
        user.street_address_2 = self.cleaned_data.get('street_address_2')
        user.city = self.cleaned_data.get('city')
        user.country = self.cleaned_data.get('country')
        user.state = self.cleaned_data.get('state')
        user.zipcode = self.cleaned_data.get('zipcode')

        user.save()
        return user




from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers, exceptions
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email(self, username, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include either "username" or "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

            # Authentication through username
            elif app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email(username, email, password)

        else:
            # Authentication without using allauth
            if email:
                try:
                    username = UserModel.objects.get(email__iexact=email).get_username()
                except UserModel.DoesNotExist:
                    pass

            if username:
                user = self._validate_username_email(username, '', password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError({'detail': msg})

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs
