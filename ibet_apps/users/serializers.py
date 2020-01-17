from rest_framework import serializers
from users.models import CustomUser, NoticeMessage
from accounting.models import DepositAccessManagement, DepositChannel
from allauth.account import app_settings as allauth_settings
from allauth.utils import (email_address_exists, get_username_max_length)
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.base import AuthProcess
from rest_framework import serializers, exceptions
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers, exceptions
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.functional import Promise
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder
import datetime
from django.contrib.postgres.fields import JSONField

class ChoicesSerializerField(serializers.SerializerMethodField):
    """
    A read-only field that return the representation of a model field with choices.
    """
    def to_representation(self, value):
        # sample: 'get_XXXX_display'
        method_name = 'get_{field_name}_display'.format(field_name=self.field_name)
        # retrieve instance method
        method = getattr(value, method_name)
        # finally use instance method to return result of get_XXXX_display()
        return method()

class UserDetailsSerializer(serializers.ModelSerializer):
    security_question = ChoicesSerializerField()
    currency = ChoicesSerializerField()
    # favorite_deposit_method = serializers.SerializerMethodField('favoriteDeposit')

    # def favoriteDeposit(self, user):
    #     deposit_method = DepositAccessManagement.objects.filter(user_id=user, deposit_favorite_method=True)
    #     if len(deposit_method) > 0:
    #         return str(DepositChannel.objects.get(thirdParty_id=deposit_method[0].deposit_channel_id))
    #     return ""
    class Meta:
        model = CustomUser
        fields = ('pk', 'username', 'email', 'first_name', 'last_name', 'phone', 'country', 'date_of_birth', 'street_address_1', 'street_address_2', 'city', 'state', 'zipcode', 'block', 'referred_by', 'reward_points', 'main_wallet', 'active', 'gender', 'over_eighteen', 'currency', 'time_of_registration', 'last_login_time', 'security_question', 'security_answer', 'withdraw_password', 'favorite_payment_method', 'email_verified', 'phone_verified', 'id_verified')
        read_only_fields = ('pk', )


class RegisterSerializer(serializers.Serializer):
    username         = serializers.CharField(required=True)
    email            = serializers.EmailField(required=False)
    password         = serializers.CharField(write_only=True)
    first_name       = serializers.CharField(required=False)
    last_name        = serializers.CharField(required=False)
    date_of_birth    = serializers.CharField(required=False)
    phone            = serializers.CharField(required=True)
    street_address_1 = serializers.CharField(required=False)
    city             = serializers.CharField(required=False)
    country          = serializers.CharField(required=True)
    zipcode          = serializers.CharField(required=False)
    over_eighteen    = serializers.BooleanField(required=False)
    language         = serializers.CharField(required=False)
    referral_code    = serializers.CharField(required=False)



    def validate_username(self, username):

        #username = get_adapter().clean_username(username)
        #return username

        user_model = get_user_model() # your way of getting the User
        try:
           user_model.objects.get(username__iexact=username)
        except user_model.DoesNotExist:
            return username
        raise serializers.ValidationError(
                    _("A user is already registered with this username."))

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."))
        return email

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        
        # print(data['first_name'])
        if 'first_name' in data and (len(data['first_name']) > 20 or not data['first_name'].isalpha()):
            raise serializers.ValidationError(_("First name not valid"))
        if 'last_name' in data and (len(data['last_name']) > 20 or not data['last_name'].isalpha()):
            raise serializers.ValidationError(_("Last name not valid"))
        if 'date_of_birth' in data and (len(data['date_of_birth']) != 10 or any(char.isalpha() for char in data['date_of_birth'])) :
            raise serializers.ValidationError(_("Date of birth not valid"))
        elif 'date_of_birth' in data:
            date = data['date_of_birth']
            date = date.split('/')
            if len(date) != 3:
                raise serializers.ValidationError(_("Date of birth not valid"))
            if not (1 <= int(date[0]) <= 12) or not ( 1 <= int(date[1]) <= 31) or not (1900 <= int(date[2]) <= int(str(datetime.datetime.now())[0:4])):
                raise serializers.ValidationError(_("Date of birth not valid"))
        if 'city' in data and (any(char.isdigit() for char in data['city']) or len(data['city'])) > 25:
            raise serializers.ValidationError(_("City not valid"))
        if 'country' in data and (any(char.isdigit() for char in data['country']) or len(data['country']) > 25):
            raise serializers.ValidationError(_("Country not valid"))
        if 'zipcode' in data and (not len(data['zipcode']) < 20 or not data['zipcode'].isdigit()) :
            raise serializers.ValidationError(_("Zipcode not valid"))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'username':         self.validated_data.get('username', ''),
            'password1':         self.validated_data.get('password', ''),
            'email':            self.validated_data.get('email', ''),
            'first_name':       self.validated_data.get('first_name', ''),
            'last_name':        self.validated_data.get('last_name', ''),
            'phone':            self.validated_data.get('phone', ''),
            'date_of_birth':    self.validated_data.get('date_of_birth', ''),
            'street_address_1': self.validated_data.get('street_address_1', ''),
            'city':             self.validated_data.get('city', ''),
            'country':          self.validated_data.get('country', ''),
            'zipcode':          self.validated_data.get('zipcode', ''),
            'over_eighteen':    self.validated_data.get('over_eighteen', ''),
            'language':         self.validated_data.get('language', ''),
            'referral_code':    self.validated_data.get('referral_code', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        
        user.phone            = self.cleaned_data.get('phone')
        user.date_of_birth    = self.cleaned_data.get('date_of_birth')
        user.street_address_1 = self.cleaned_data.get('street_address_1')
        user.city             = self.cleaned_data.get('city')
        user.country          = self.cleaned_data.get('country')
        user.zipcode          = self.cleaned_data.get('zipcode')
        user.gender           = self.cleaned_data.get('gender')
        user.over_eighteen    = self.cleaned_data.get('over_eighteen')
        user.language         = self.cleaned_data.get('language')

        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})
    iovationData = serializers.JSONField(required=False)


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
    
    def custom_check_username_email_phone_password(self, item, password):
        try:
            user = CustomUser.objects.get(username=item)
            if user:
                if user.check_password(password):
                    return user
        except:
            user = ''
        
        try:
            user = CustomUser.objects.get(email=item)
            if user:
                if user.check_password(password):
                    return user
        except: 
            user = ''

        try:
            user = CustomUser.objects.get(phone=item)
            if user:
                if user.check_password(password):
                    return user
        except:
            user = ''

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        iovationData = attrs.get('iovationData')
        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            user = self.custom_check_username_email_phone_password(username, password)

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


class FacebookRegisterSerializer(serializers.Serializer):
    
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    
    def validate_username(self, username):

        user_model = get_user_model() # your way of getting the User
        try:
           user_model.objects.get(username__iexact=username)
        except user_model.DoesNotExist:
            return username
        raise serializers.ValidationError(
                    _("A user is already registered with this username."))

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."))
        return email


    def validate(self, data):
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'email': self.validated_data.get('email', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])

        user.save()
        return user


class FacebookLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

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

    def custom_check_username_email(self, username, email):
        try:
            temp = CustomUser.objects.filter(username=username)
            temp.update(active=True)
            user = CustomUser.objects.get(username=username)
            if user:
                if user.email == email:
                    return user
        except: 
            user = ''

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            user = self.custom_check_username_email(username, email)

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


class CustomTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class LanguageCodeSerializer(serializers.Serializer):
    languageCode = serializers.CharField()

class NoticeMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeMessage
        fields = ('pk', 'start_time', 'end_time', 'message', 'message_zh', 'message_fr')

class BalanceSerializer(serializers.Serializer):
    type = serializers.CharField()
    balance = serializers.FloatField()
    username = serializers.CharField()

class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)