from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import permission_required
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as django_login, logout as django_logout
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.views import View
from django.utils.timezone import timedelta
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth, Coalesce
from django.contrib import messages
from dateutil.relativedelta import relativedelta

from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import GameSerializer, CategorySerializer, UserDetailsSerializer, RegisterSerializer, LoginSerializer, CustomTokenSerializer, NoticeMessageSerializer, FacebookRegisterSerializer, FacebookLoginSerializer, BalanceSerializer
from .forms import RenewBookForm, CustomUserCreationForm
from .models import Game, CustomUser, Category, Config, NoticeMessage, UserAction, UserActivity, Limitation

from accounting.models import Transaction

from rest_auth.models import TokenModel
from rest_auth.app_settings import TokenSerializer, JWTSerializer, create_token

from allauth.account.utils import complete_signup
from allauth.account import app_settings as allauth_settings

from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.views import get_password_reset_token_expiry_time
from django.template.defaulttags import register

import datetime
import logging
import os

from django.contrib.auth import get_user_model

import base64
import uuid
import csv

from threading import Timer

from django.utils.crypto import get_random_string
from xadmin.views import CommAdminView
import random

import simplejson as json
import decimal

from utils.constants import *
import requests

logger = logging.getLogger('django')

sensitive_post_parameters_m = method_decorator(sensitive_post_parameters('password1', 'password2'))


class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

def profile(request):
        if request.method == "POST":
            return render(request, "users/profile.html")
        else:
            return render(request, "users/profile.html")

def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    # Available copies of books
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1
    
    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        'index.html',
        context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors,
            'num_visits':num_visits},
    )


class GameListView(generic.ListView):
    model = Game
    paginate_by = 10


class GameDetailView(generic.DetailView):
    model = Game


class PlayerDetailView(generic.DetailView):
    model = CustomUser


class AllSearchListView(generic.ListView):
    model = Game
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query == None:
            return Game.objects.none()
        return Game.objects.filter(name__contains=self.request.GET.get('q'))


class GameAPIListView(ListAPIView):
    serializer_class = GameSerializer
    def get_queryset(self):
        term = self.request.GET['term']
        # print("term:" + term)
        data = Game.objects.filter(category_id__parent_id__name__icontains=term)

        if not data:
            data = Game.objects.filter(category_id__name__icontains=term)

        if not data:
            data = Game.objects.filter(name__icontains=term)

        if not data:
            logger.error('Search term did not match any categories or token')
        return data

class GameDetailAPIListView(ListAPIView):
    
    serializer_class = GameSerializer
    def get_queryset(self):
        id = self.request.GET['id']
        data = Game.objects.filter(pk=id)
        return data


class CategoryAPIListView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class UserDetailsView(RetrieveUpdateAPIView):
    serializer_class = UserDetailsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return get_user_model().objects.none()

class RegisterView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny, ]
    token_model = TokenModel

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(RegisterView, self).dispatch(*args, **kwargs)

    def get_response_data(self, user):
        if allauth_settings.EMAIL_VERIFICATION == allauth_settings.EmailVerificationMethod.MANDATORY:
            return {"detail": ("Verification e-mail sent.")}

        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': user,
                'token': self.token
            }
            return JWTSerializer(data).data
        else:
            return TokenSerializer(user.auth_token).data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        customUser = CustomUser.objects.filter(username=user).first()

        # if customUser.
        customUser.time_of_registration = timezone.now()
        customUser.save()

        
        action = UserAction(
            user= customUser,
            ip_addr=self.request.META['REMOTE_ADDR'],
            event_type=2,
        )
        action.save()

        return Response(self.get_response_data(user),
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        if getattr(settings, 'REST_USE_JWT', False):
            self.token = jwt_encode(user)
        else:
            create_token(self.token_model, user, serializer)

        complete_signup(self.request._request, user,
                        allauth_settings.EMAIL_VERIFICATION,
                        None)
        return user


class BlockedUserException(APIException):
    status_code = 403
    default_detail = _('Current user is blocked!')
    default_code = 'block'

class InactiveUserException(APIException):
    status_code = 403
    default_detail = _('Please activate your account!') 


class LoginView(GenericAPIView):
    """
    Check the credentials and return the REST Token
    if the credentials are valid and authenticated.
    Calls Django Auth login method to register User ID
    in Django session framework
    Accept the following POST parameters: username, password
    Return the REST Framework Token Object's key.
    """
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    token_model = TokenModel

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def process_login(self):
        django_login(self.request, self.user)

    def get_response_serializer(self):
        if getattr(settings, 'REST_USE_JWT', False):
            response_serializer = JWTSerializer
        else:
            response_serializer = TokenSerializer
        return response_serializer

    def login(self):

        languageCode = 'en'
        if LANGUAGE_SESSION_KEY in self.request.session:
            languageCode = self.request.session[LANGUAGE_SESSION_KEY]
        # print('login language code: ' + languageCode)

        self.user = self.serializer.validated_data['user']
        if self.user.block is True:
            print("user block")
            raise BlockedUserException
        if self.user.active == False:
            print('User not active')
            raise InactiveUserException

        if getattr(settings, 'REST_USE_JWT', False):
            
            self.token = jwt_encode(self.user)
        else:
            self.token = create_token(self.token_model, self.user, self.serializer)

        customUser = CustomUser.objects.filter(username=self.user)
        action = UserAction(
            user= customUser.first(),
            ip_addr=self.request.META['REMOTE_ADDR'],
            event_type=0,
        )
        action.save()
        customUser.update(last_login_time=timezone.now(), modified_time=timezone.now())
        loginUser = CustomUser.objects.filter(username=self.user)
        loginTimes = CustomUser.objects.filter(username=self.user).first().login_times
        loginUser.update(login_times=loginTimes+1)

        if getattr(settings, 'REST_SESSION_LOGIN', True):
            self.process_login()
        return self.get_response()

    def get_response(self):
        serializer_class = self.get_response_serializer()

        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': self.user,
                'token': self.token
            }
            serializer = serializer_class(instance=data,
                                          context={'request': self.request})
        else:
            serializer = serializer_class(instance=self.token,
                                          context={'request': self.request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):        
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)

        return self.login()


from django.core.exceptions import ObjectDoesNotExist

class LogoutView(APIView):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.
    Accepts/Returns nothing.
    """
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        if getattr(settings, 'ACCOUNT_LOGOUT_ON_GET', False):
            response = self.logout(request)
        else:
            response = self.http_method_not_allowed(request, *args, **kwargs)

        return self.finalize_response(request, response, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.logout(request)

    def logout(self, request):
        self.user = request.user
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        action = UserAction(
            user= CustomUser.objects.filter(username=self.user).first(),
            ip_addr=self.request.META['REMOTE_ADDR'],
            event_type=1,
        )
        action.save()

        if getattr(settings, 'REST_SESSION_LOGIN', True):
            django_logout(request)
        
        response = Response({"detail": _("Successfully logged out.")},
                            status=status.HTTP_200_OK)

        if getattr(settings, 'REST_USE_JWT', False):
            from rest_framework_jwt.settings import api_settings as jwt_settings
            if jwt_settings.JWT_AUTH_COOKIE:
                response.delete_cookie(jwt_settings.JWT_AUTH_COOKIE)
        return response


import sendgrid
from sendgrid.helpers.mail import *


class SendEmail(View):
    def get(self, request, *args, **kwargs):
        case = self.request.GET['case']
        from_email_address = 'claymore@claymoreusa.com'
        if case == 'signup':
            to_email_address = self.request.GET['to_email_address']
            email_subject = str(_('You have registered an account at ibet.com, ')) + ' '
            email_content = str(_('You username is ')) + self.request.GET['username'] + str(_(', and your email address is ')) + self.request.GET['email']
        elif case == 'change_email':
            to_email_address = self.request.GET['to_email_address']
            email_subject = _('Request of changing email address') + ' '
            email_content = _('Your new Email Address is: ') + self.request.GET['email']
        elif case == 'referral':
            to_email_address = self.request.GET['to_email_address']
            email_subject = self.request.GET['username'] + str(_(' referred you to sign up an account with Claymore')) 
            email_content = _('Please use the referral link to register your new account: ') + 'http://localhost:3000/signup/' + self.request.GET['referralid']

        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        from_email = Email(from_email_address)
        to_email = Email(to_email_address)
        subject = email_subject
        content = Content("text/plain", email_content)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        return HttpResponse('Email has been sent!')


class CustomPasswordResetView:
    @receiver(reset_password_token_created)
    def password_reset_token_created(sender, reset_password_token, *args, **kwargs):
        
        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        from_email = Email('claymore@claymoreusa.com')
        to_email = Email(reset_password_token.user.email)
        subject =  _('Hi %(username)s, You have requested to reset your password') % {'username': reset_password_token.user.username}
        # subject = _('Hi ' + reset_password_token.user.username + ', You have requested to reset your password')
        content_text = _('Click the link to reset your email password: ')
        content = Content("text/plain", content_text + "{}reset_password/{}".format('http://localhost:3000/', reset_password_token.key))
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())


class CustomPasswordTokenVerificationView(APIView):
    """
      An Api View which provides a method to verifiy that a given pw-reset token is valid before actually confirming the
      reset.
    """
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = CustomTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        # get token validation time
        password_reset_token_validation_time = get_password_reset_token_expiry_time()

        # find token
        reset_password_token = ResetPasswordToken.objects.filter(key=token).first()

        if reset_password_token is None:
            return Response({'status': 'invalid'}, status=status.HTTP_404_NOT_FOUND)

        # check expiry date
        expiry_date = reset_password_token.created_at + timedelta(hours=password_reset_token_validation_time)

        if timezone.now() > expiry_date:
            # delete expired token
            reset_password_token.delete()
            return Response({'status': 'expired'}, status=status.HTTP_404_NOT_FOUND)

        # check if user has password to change
        if not reset_password_token.user.has_usable_password():
            return Response({'status': 'irrelevant'})

        return Response({'status': 'OK'})


from django.utils import timezone
from django.utils.translation import ngettext
from .serializers import LanguageCodeSerializer
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils import translation
from django.contrib.sessions.backends.db import SessionStore


class LanguageView(APIView):

    # throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = LanguageCodeSerializer
    
    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        languageCode = serializer.validated_data['languageCode']
        request.session[LANGUAGE_SESSION_KEY] = languageCode
        request.session.modified = True
        # Make current response also shows translated result
        translation.activate(languageCode)

        response = Response({'languageCode': languageCode}, status = status.HTTP_200_OK)

        # print('post: ' + languageCode)

        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        if session_key is None:
            request.session.create()
            response.set_cookie(key=settings.SESSION_COOKIE_NAME, value=request.session._session_key)
        # Check that the test cookie worked (we set it below):
        # if request.session.test_cookie_worked():

        #     # The test cookie worked, so delete it.
        #     request.session.delete_test_cookie()

        #     # In practice, we'd need some logic to check username/password
        #     # here, but since this is an example...
        # request.session.set_test_cookie()
        
        return response

    def get(self, request, *args, **kwargs):
        languageCode = 'en'
        if LANGUAGE_SESSION_KEY in request.session:
            languageCode = request.session[LANGUAGE_SESSION_KEY]
        
        
        # print('get: ' + languageCode)
        return Response({'languageCode': languageCode}, status = status.HTTP_200_OK)  


class NoticeMessageView(ListAPIView):
    serializer_class = NoticeMessageSerializer
    queryset = NoticeMessage.objects.all()

class ReferralAward(View):
    def get(self, request, *args, **kwargs):
        referral_id = self.request.GET['referral_id']
        current_referred = self.request.GET['referred']
        user          = get_user_model().objects.filter(referral_id=referral_id)
        referred_user = get_user_model().objects.filter(username=current_referred)
        
        data = Config.objects.all()[0]
        to_add = data.referral_award_points
        to_add_accept = data.referral_accept_points

        for item in user:
            points = item.reward_points
        points_sum = points + to_add
        user.update(reward_points=points_sum, modified_time=timezone.now())

        for item in referred_user:
            points_referred = item.reward_points
        points_sum_referred = to_add_accept + points_referred
        referred_user.update(reward_points = points_sum_referred, modified_time=timezone.now())
   
        referred_user.update(referred_by=user[0], modified_time=timezone.now())
        
        return HttpResponse('Update successful')


class CheckReferral(View):
    def get(self, request, *args, **kwargs):
        
        referral_id = self.request.GET['referral_id']
        email = self.request.GET['email']
        check_duplicate = get_user_model().objects.filter(email__iexact=email)
        if check_duplicate:
            return HttpResponse('Duplicate')
        user = get_user_model().objects.filter(referral_id=referral_id)
        data = Config.objects.all()[0]
        maximum = data.referral_limit
        current_referral = len(user[0].referees.all())
        if not current_referral:
            return HttpResponse('Valid')
        if current_referral >= maximum:
            return HttpResponse('Invalid')
        return HttpResponse('Valid')


class ReferralTree(View):
    def get(self, request, *args, **kwargs):
        username = self.request.GET['username']
        user = get_user_model().objects.filter(username=username)
        result = []
        data = Config.objects.all()[0]
        level = data.level
        temp = user[0].referees.all()
        result.append(len(temp))
        for i in range(level - 1):
            dummy = []
            for item in temp:
                for person in item.referees.all():
                    dummy.append(person)
            result.append(len(dummy))
            temp = dummy
        return HttpResponse(result)

class Global(View):
    def get(self, request, *args, **kwargs):
        data = Config.objects.all()[0]
        return HttpResponse(data.level)

        
class AddOrWithdrawBalance(APIView):

    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = BalanceSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        balance = serializer.validated_data['balance']
        type_balance = serializer.validated_data['type']

        user = get_user_model().objects.filter(username=username)
        currrent_balance = user[0].main_wallet
        # if balance.isdigit() == False:
        #     return HttpResponse('Failed')

        if type_balance == 'add':
            if user[0].ftd_time is None:
                user.update(ftd_time=timezone.now(), modified_time=timezone.now())

            new_balance = currrent_balance + decimal.Decimal(balance)
            user.update(main_wallet=new_balance, modified_time=timezone.now())
            referrer = user[0].referred_by

            if referrer:
                referr_object = get_user_model().objects.filter(username=referrer.username)
                data = Config.objects.all()[0]
                reward_points = referr_object[0].reward_points
                current_points = reward_points + data.Referee_add_balance_reward
                referr_object.update(reward_points=current_points, modified_time=timezone.now())

            # create = Transaction.objects.create(
            #     user_id=CustomUser.objects.filter(username=username).first(), 
            #     amount=balance, 
            #     transaction_type=0
            # )

            # action = UserAction(
            #     user= CustomUser.objects.filter(username=username).first(),
            #     ip_addr=self.request.META['REMOTE_ADDR'],
            #     event_type=3,
            #     dollar_amount=balance
            # )
            # action.save()
            return HttpResponse('Deposit Success')

        else:
            if decimal.Decimal(balance) > currrent_balance:
                return HttpResponse('The balance is not enough', status=200)

            new_balance = currrent_balance - decimal.Decimal(balance)
            user.update(main_wallet=new_balance, modified_time=timezone.now())

            create = Transaction.objects.create(
                user_id=CustomUser.objects.filter(username=username).first(), 
                amount=balance, 
                transaction_type=1
            )

            # action = UserAction(
            #     user= CustomUser.objects.filter(username=username).first(),
            #     ip_addr=self.request.META['REMOTE_ADDR'],
            #     event_type=4,
            #     dollar_amount=balance
            # )
            # action.save()
            return HttpResponse('Withdraw Success')

class Activation(View):
    def post(self, request, *args, **kwargs):
        
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        email = body['email']

        user = get_user_model().objects.filter(email=email)
        user.update(verfication_time=timezone.now(), modified_time=timezone.now())
        activation_code = str(base64.urlsafe_b64encode(uuid.uuid1().bytes.rstrip())[:25])[2:-1]
        user.update(activation_code=activation_code, modified_time=timezone.now())
        def timeout():
            if user[0].activation_code:
                user.delete()
        thread = Timer(1800.0, timeout)
        thread.start()

        from_email_address = 'claymore@claymoreusa.com'
        to_email_address = email
        email_subject = str(_('Please activate you ibet account ')) + ' '
        email_content = settings.HOST_URL + 'activate/' + activation_code

        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        from_email = Email(from_email_address)
        to_email = Email(to_email_address)
        subject = email_subject
        content = Content("text/plain", email_content)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        #print(response.status_code)
        return HttpResponse('Email has been sent!')

class ActivationVerify(View):
    def post(self, request, *args, **kwargs):

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        token = body['token']

        user = get_user_model().objects.filter(activation_code=token)
        if len(user) != 0:
            user.update(active=True)
            user.update(activation_code='', modified_time=timezone.now())
            return HttpResponse('Success')
        return HttpResponse('The link has expired')


class FacebookRegister(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = FacebookRegisterSerializer
    permission_classes = [AllowAny, ]
    token_model = TokenModel

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(FacebookRegister, self).dispatch(*args, **kwargs)

    def get_response_data(self, user):
        if allauth_settings.EMAIL_VERIFICATION == allauth_settings.EmailVerificationMethod.MANDATORY:
            return {"detail": ("Verification e-mail sent.")}

        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': user,
                'token': self.token
            }
            return JWTSerializer(data).data
        else:
            return TokenSerializer(user.auth_token).data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(self.get_response_data(user),
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        if getattr(settings, 'REST_USE_JWT', False):
            self.token = jwt_encode(user)
        else:
            create_token(self.token_model, user, serializer)

        complete_signup(self.request._request, user,
                        allauth_settings.EMAIL_VERIFICATION,
                        None)
        return user


class FacebookLoginView(GenericAPIView):
    """
    Check the credentials and return the REST Token
    if the credentials are valid and authenticated.
    Calls Django Auth login method to register User ID
    in Django session framework
    Accept the following POST parameters: username, password
    Return the REST Framework Token Object's key.
    """
    permission_classes = (AllowAny,)
    serializer_class = FacebookLoginSerializer
    token_model = TokenModel

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(FacebookLoginView, self).dispatch(*args, **kwargs)

    def process_login(self):
        django_login(self.request, self.user)

    def get_response_serializer(self):
        if getattr(settings, 'REST_USE_JWT', False):
            response_serializer = JWTSerializer
        else:
            response_serializer = TokenSerializer
        return response_serializer

    def login(self):

        languageCode = 'en'
        if LANGUAGE_SESSION_KEY in self.request.session:
            languageCode = self.request.session[LANGUAGE_SESSION_KEY]
        # print('login language code: ' + languageCode)

        self.user = self.serializer.validated_data['user']
        if self.user.block is True:
            print("user block")
            raise BlockedUserException
        if self.user.active == False:
            print('User not active')
            raise InactiveUserException

        if getattr(settings, 'REST_USE_JWT', False):
            
            self.token = jwt_encode(self.user)
        else:
            self.token = create_token(self.token_model, self.user,
                                      self.serializer)

        if getattr(settings, 'REST_SESSION_LOGIN', True):
            self.process_login()
        return self.get_response()

    def get_response(self):
        serializer_class = self.get_response_serializer()

        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': self.user,
                'token': self.token
            }
            serializer = serializer_class(instance=data,
                                          context={'request': self.request})
        else:
            serializer = serializer_class(instance=self.token,
                                          context={'request': self.request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):        
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)

        return self.login()

def generate_username():
    name_list = [ 'Stephen', 'Mike', 'Tom', 'Luke', 'James', 'Kevin', 'Stephan', 'Wilson', 'Alice', 'Sunny', 'Cloris', 'Jack', 
        'Leo', 'Shaw', 'Peter', 'Ben', 'Ross', 'Rachel', 'Michael', 'Jordan', 'Oliver', 'Harry', 'John', 'William', 'David', 'Richard', 'Joseph',
        'Charles', 'Thomas', 'Joe', 'George', 'Oscar', 'Amelia', 'Margaret', 'Megan', 'Jennifer', 'Bethany', 'Isla', 'Lauren', 'Samantha', 'Emma',
        'Joanne', 'Ava', 'Tracy', 'Elizabeth', 'Sophie', 'Lily', 'Jacob', 'Robert']

    username_1 = name_list[random.randint(1, len(name_list) - 1)]
    username_2 = ''.join([str(random.randint(0, 9)) for i in range(5)])
    return username_1 + username_2


class OneclickRegister(APIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        username = generate_username()
        check_duplicate = CustomUser.objects.filter(username=username)
        while check_duplicate:
            username = generate_username
            check_duplicate = CustomUser.objects.filter(username=username)

        email = get_random_string(length=8)
        check_duplicate = CustomUser.objects.filter(email=email)
        while check_duplicate:
            email = get_random_string(length=8)
            check_duplicate = CustomUser.objects.filter(email=email)

        phone = ''.join([str(random.randint(0,10)) for i in range(10)])
        check_duplicate = CustomUser.objects.filter(phone=phone)
        while check_duplicate:
            phone = ''.join([str(random.randint(0,10)) for i in range(10)])
            check_duplicate = CustomUser.objects.filter(phone=phone)

        password = get_random_string(length=10)
        email = email + '@gmail.com'

        CustomUser.objects.create_user(username, email, phone, password)
        user = CustomUser.objects.filter(username=username)
        user.update(active=True, modified_time=timezone.now())

        return Response({'username': username, 'password': password})


class UpdateEmail(View):
    def post(self, request, *args, **kwargs):

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        old_email = body['old_email']

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        new_email = body['new_email']

        check_duplicate = get_user_model().objects.filter(email__iexact=new_email)
        if check_duplicate:
            return HttpResponse('Duplicate')
            
        user = CustomUser.objects.filter(email=old_email)
        user.update(email=new_email, modified_time=timezone.now())
        return HttpResponse('Success')


class CheckEmailExixted(View):
    def get(self, request, *args, **kwargs):
        
        email = self.request.GET['email']
        check_exist = get_user_model().objects.filter(email__iexact=email)
        if check_exist:
            return HttpResponse('Exist')
        return HttpResponse('Invalid')


class GenerateForgetPasswordCode(View):
    def post(self, request, *args, **kwargs):

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        email = body['email']
        user = get_user_model().objects.filter(email__iexact=email)
        if user:
            code = ''.join([str(random.randint(0, 9)) for i in range(4)])
            user.update(reset_password_code=code)
            return HttpResponse('Success')
        return HttpResponse('Failed')


class SendResetPasswordCode(View):
    def post(self, request, *args, **kwargs):

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        email = body['email']
        user = get_user_model().objects.filter(email=email)
        reset_password_code = user[0].reset_password_code
        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        from_email = Email('ibet@ibet.com')
        to_email = Email(email)
        subject =  str(_('Reset Password'))
        content_text = str(_('Use this code to reset your password '))
        content = Content("text/plain", content_text + "\n {} \n \n {} ".format(reset_password_code, 'ibet'))
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        return HttpResponse('Success')


class VerifyResetPasswordCode(View):
    def post(self, request, *args, **kwargs):

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        email = body['email']

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        code = body['code']

        user = get_user_model().objects.filter(email=email)
        verify = user[0].reset_password_code
        if code == verify:
            user.update(reset_password_code='')
            return HttpResponse('Success')
        else:
            return HttpResponse('Failed')


class ChangeAndResetPassword(View):
    def post(self, request, *args, **kwargs):

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        email = body['email']

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        password = body['password']

        user = get_user_model().objects.get(email=email)
        user.set_password(password)
        user.save()
        return HttpResponse('Success')





class AgentView(CommAdminView):
    def get(self, request):
        context = super().get_context()
        users = get_user_model().objects.all()
        agents = get_user_model().objects.exclude(agent_level='Normal')
        agents_has_referred = agents.filter(referred_by_id__isnull=False)
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        today = datetime.date.today()
        last_month = datetime.date.today().replace(day=1) + relativedelta(months=-1)
        before_last_month = datetime.date.today().replace(day=1) + relativedelta(months=-2)
        this_month = datetime.date.today().replace(day=1)

        # get transaction type 
        tran_type = Transaction._meta.get_field('transaction_type').choices
        commission_number = None
        for key, value in tran_type:
            if value is 'Commission':
                commission_number = key

        if commission_number is None:
            raise ValueError('No Commission Type Here!!!')      
        tran_commission = Transaction.objects.filter(transaction_type=commission_number)
        tran_with_commission_this_month = tran_commission.filter(Q(request_time__gte=last_month) & Q(request_time__lte=this_month))
        tran_with_commission_month_before = tran_commission.filter(Q(request_time__gte=before_last_month) & Q(request_time__lte=last_month))


        title = "Agent Overview"
        context["breadcrumbs"].append({'url': '/agent_overview/', 'title': title})
        context["title"] = title
        context["agents"] = agents
        context["premium_number"] = users.filter(agent_level='Premium').count()
        context["invalid_number"] = users.filter(agent_level='Invalid').count()
        context["normal_number"] = users.filter(agent_level='Normal').count()
        context["negative_number"] = users.filter(agent_level='Negative').count()
        context["new_ftd"] = agents.filter(ftd_time__range=[yesterday, today]).count()
        context["most_new_player"] = agents_has_referred.values("referred_by_id").annotate(downline_number=Count("referred_by_id")).order_by("-referred_by_id")


        # active user
        @register.filter(name='lookup')
        def lookup(dict, index):
            if index in dict:
                return dict[index]
            return '0'

        active_user_dict = {}
        for user, agent in agents.values_list('id', 'referred_by'):
            if agent is None:
                continue
            elif (Transaction.objects.all().filter(Q(user_id=user) & Q(request_time__gte=last_month)).exists()):
                active_user_dict.update({agent: active_user_dict.get(agent, 0) + 1})
        context["active_user_dict"] = active_user_dict

        # downline deposit
        downline_deposit = {}
        for user, agent, balance in agents.values_list('id', 'referred_by', 'main_wallet'):
            if agent is not None:
                downline_deposit.update({agent: downline_deposit.get(agent, 0) + balance})                
        context["downline_deposit"] = downline_deposit

        # commission system
        commision_transaction = tran_commission.annotate(month=TruncMonth('request_time')).values('month').annotate(total_commission=Sum('amount')).order_by('-month')
        
        commission = []

        for tran in commision_transaction:
            commission_dict = {}
            commission_dict['month'] = tran['month']
            commission_dict['total_commission'] = tran['total_commission']
            commission_dict['agent_number'] = agents.exclude(user_to_agent=None).filter(user_to_agent__lte=tran['month']+relativedelta(months=1)).count()
            # add a condition referred_by_id is none
            commission_dict['active_downline'] = Transaction.objects.filter(Q(request_time__gte=tran['month']) & Q(request_time__lte=tran['month']+relativedelta(months=1))).values('user_id').distinct().count()
            commission.append(commission_dict)
        
        context["commision_transaction"] = commission
        
        
        commission_last_month = {}
        commission_month_before = {}
        for agent_name,agent_id in agents.values_list('username','id'):
            try:
                cur = tran_with_commission_this_month.get(user_id_id=agent_id)
                commission_last_month.update({agent_name: cur.amount})
            except:
                commission_last_month.update({agent_name: '0'})
            

        for agent_name,agent_id in agents.values_list('username','id'):
            try:
                last = tran_with_commission_month_before.get(user_id_id=agent_id)
                commission_month_before.update({agent_name: last.amount})
            except:
                commission_month_before.update({agent_name: '0'})
        
        context["commission_last_month"] = commission_last_month
        context["commission_month_before"] = commission_month_before

        # premium application
        users_with_application_to_premium = users.exclude(user_application_time=None).order_by('-user_application_time')
        context["users_with_application_to_premium"] = users_with_application_to_premium

        return render(request, 'users/agent_list.html', context) 
    
    # post for new affiliate
    # def post(self, request, *args, **kwargs):
    #     username = generate_username()
    #     check_duplicate = CustomUser.objects.filter(username=username)
    #     while check_duplicate:
    #         username = generate_username
    #         check_duplicate = CustomUser.objects.filter(username=username)

    #     email = get_random_string(length=8)
    #     check_duplicate = CustomUser.objects.filter(email=email)
    #     while check_duplicate:
    #         email = get_random_string(length=8)
    #         check_duplicate = CustomUser.objects.filter(email=email)

    #     phone = ''.join([str(random.randint(0,10)) for i in range(10)])
    #     check_duplicate = CustomUser.objects.filter(phone=phone)
    #     while check_duplicate:
    #         phone = ''.join([str(random.randint(0,10)) for i in range(10)])
    #         check_duplicate = CustomUser.objects.filter(phone=phone)

    #     password = get_random_string(length=10)
    #     email = email + '@gmail.com'

    #     CustomUser.objects.create_user(username, email, phone, password)
    #     user = CustomUser.objects.filter(username=username)
    #     user.update(active=True, modified_time=timezone.now())

    #     context = super().get_context()
    #     agent_name = request.POST.get('username')
    #     args = {'agent_name':username, 'agent_password':password, 'user':user}
        
    #     return render(request,"users/agent_list.html",args)

class AgentDetailView(CommAdminView):
    def get(self, request, *args, **kwargs):
        context = super().get_context()
        return render(request,"users/agent_detail.html", context)
     
from xadmin.views import CommAdminView
from django.core import serializers
from django.http import HttpResponse
from django.db.models import Sum
from datetime import timedelta
from django.db.models import Q
import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError
from django.conf import settings


class UserDetailView(CommAdminView):
    def get(self, request, *args, **kwargs):
        context = super().get_context()
        title = 'Member ' + self.kwargs.get('pk')
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context["title"] = title
        context['time'] = timezone.now()
        customUser = CustomUser.objects.get(pk=self.kwargs.get('pk'))
        context['customuser'] = customUser
        context['userPhotoId'] = self.download_user_photo_id(customUser.username)
        context['userLoginActions'] = UserAction.objects.filter(user=customUser, event_type=0)[:20]
        transaction = Transaction.objects.filter(user_id=customUser)

        riskLevelMap = {}
        for t in CustomUser._meta.get_field('risk_level').choices:
            riskLevelMap[t[0]] = t[1]

        context['riskLevel'] = riskLevelMap[int(customUser.risk_level)]

        statusMap = {}
        for t in Transaction._meta.get_field('status').choices:
            statusMap[t[0]] = t[1]

        transTypeMap = {}
        for t in Transaction._meta.get_field('transaction_type').choices:
            transTypeMap[t[0]] = t[1]
        
        productMap = {}
        for t in Transaction._meta.get_field('product').choices:
            productMap[t[0]] = t[1]

        currencyMap = {}
        for t in Transaction._meta.get_field('currency').choices:
            currencyMap[t[0]] = t[1]
        
        channelMap = {}
        for t in Transaction._meta.get_field('channel').choices:
            channelMap[t[0]] = t[1]


        if Transaction.objects.filter(user_id=customUser).count() == 0:
            context['userTransactions'] = ''
        else:
            transactions = Transaction.objects.filter(user_id=customUser).order_by("-request_time")[:20]
            transactions = serializers.serialize('json', transactions)
            transactions = json.loads(transactions)

            trans = []
            for tran in transactions:
                try:
                    time = datetime.datetime.strptime(tran['fields']['request_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    time = datetime.datetime.strptime(tran['fields']['request_time'], "%Y-%m-%dT%H:%M:%SZ")
                time = time.strftime("%B %d, %Y, %I:%M %p")
                transDict = {
                    'transactionId': str(tran['pk']),
                    'category': str(transTypeMap[tran['fields']['transaction_type']]),
                    'transType': transTypeMap[tran['fields']['transaction_type']],
                    'transTypeCode': tran['fields']['transaction_type'],
                    'product': productMap[tran['fields']['product']],
                    'toWhichWallet': str(tran['fields']['transfer_to']),
                    'currency': currencyMap[tran['fields']['currency']],
                    'time': time,
                    'amount': tran['fields']['amount'],
                    'balance': tran['fields']['amount'],
                    'status': statusMap[tran['fields']['status']],
                    'bank': str(tran['fields']['bank']),
                    'channel': channelMap[tran['fields']['channel']],
                    'method': tran['fields']['method'],
                }
                # transDict = serializers.serialize('json')
                trans.append(transDict)
            context['userTransactions'] = trans
            

        userLastLogin = UserAction.objects.filter(user=customUser, event_type=0).order_by('-created_time').first()   
        context['userLastIpAddr'] = userLastLogin
        context['loginCount'] = UserAction.objects.filter(user=customUser, event_type=0).count()

        transaction = Transaction.objects.filter(user_id=customUser)
        if transaction.count() <= 20:
            context['isLastPage'] = True
        else:
            context['isLastPage'] = False

        depositAmount = Transaction.objects.filter(user_id=customUser, transaction_type=0).aggregate(Sum('amount'))
        withdrawAmount = Transaction.objects.filter(user_id=customUser, transaction_type=1).aggregate(Sum('amount'))
        depositCount = Transaction.objects.filter(user_id=customUser, transaction_type=0).count()
        withdrawCount = Transaction.objects.filter(user_id=customUser, transaction_type=1).count()
        bonusAmount = Transaction.objects.filter(user_id=customUser, transaction_type=6).aggregate(Sum('amount'))

        if bonusAmount['amount__sum'] is None:
            bonusAmount['amount__sum'] = 0
        if withdrawAmount['amount__sum'] is None:
            withdrawAmount['amount__sum'] = 0
        if depositAmount['amount__sum'] is None:
            depositAmount['amount__sum'] = 0

        if depositAmount['amount__sum'] == 0:
            withdrawRate = 0
            bonusRate = 0
        else:
            withdrawRate = withdrawAmount['amount__sum']/depositAmount['amount__sum']
            bonusRate = bonusAmount['amount__sum']/depositAmount['amount__sum']
        
        context['withdrawDepositRate'] = "%.2f" % withdrawRate
        context['bonusDepositRate'] = "%.2f" % bonusRate
        context['depositCount'] = depositCount
        context['withdrawCount'] = withdrawCount
        context['depositAmount'] = depositAmount['amount__sum']
        context['withdrawAmount'] = withdrawAmount['amount__sum']
        
        if userLastLogin is None:
            context['relativeAccount'] = ''
        else:
            context['relativeAccount'] = self.account_by_ip(userLastLogin.ip_addr, userLastLogin.user)
        # print(str(context['relativeAccount']))

        deposits = Transaction.objects.filter(user_id=customUser, transaction_type=0).order_by('-request_time').first()
        if deposits:
            deposits = serializers.serialize('json', [deposits])
            deposits = json.loads(deposits)
            lastDeposit = []
            for deposit in deposits:
                try:
                    time = datetime.datetime.strptime(deposit['fields']['request_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    time = datetime.datetime.strptime(deposit['fields']['request_time'], "%Y-%m-%dT%H:%M:%SZ")
                time = time.strftime("%B %d, %Y, %I:%M %p")
                depositDict = {
                    'transactionId': str(deposit['pk']),
                    'category': str(transTypeMap[deposit['fields']['transaction_type']]),
                    'transType': transTypeMap[deposit['fields']['transaction_type']],
                    'transTypeCode': deposit['fields']['transaction_type'],
                    'product': productMap[deposit['fields']['product']],
                    'toWhichWallet': str(deposit['fields']['transfer_to']),
                    'currency': currencyMap[deposit['fields']['currency']],
                    'time': time,
                    'amount': deposit['fields']['amount'],
                    'status': statusMap[deposit['fields']['status']],
                    'bank': str(deposit['fields']['bank']),
                    'channel': channelMap[deposit['fields']['channel']],
                    'method': deposit['fields']['method'],
                }
                lastDeposit.append(depositDict)
            context['lastDeposits'] = lastDeposit[:1]
        else:
            context['lastDeposits'] = {}

        withdraws = Transaction.objects.filter(user_id=customUser, transaction_type=1).order_by('-request_time').first() 
        if withdraws:
            withdraws = serializers.serialize('json', [withdraws])
            withdraws = json.loads(withdraws)
            lastWithdraw = []
            for withdraw in withdraws:
                try:
                    time = datetime.datetime.strptime(withdraw['fields']['request_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    time = datetime.datetime.strptime(withdraw['fields']['request_time'], "%Y-%m-%dT%H:%M:%SZ")
                time = time.strftime("%B %d, %Y, %I:%M %p")
                withdrawDict = {
                    'transactionId': str(withdraw['pk']),
                    'category': withdraw['fields']['transaction_type'],
                    'transType': transTypeMap[withdraw['fields']['transaction_type']],
                    'transTypeCode': withdraw['fields']['transaction_type'],
                    'product': productMap[withdraw['fields']['product']],
                    'toWhichWallet': str(withdraw['fields']['transfer_to']),
                    'currency': currencyMap[withdraw['fields']['currency']],
                    'time': time,
                    'amount': withdraw['fields']['amount'],
                    'status': statusMap[withdraw['fields']['status']],
                    'bank': str(withdraw['fields']['bank']),
                    'channel': channelMap[withdraw['fields']['channel']],
                    'method': withdraw['fields']['method'],
                }
                lastWithdraw.append(withdrawDict)
            context['lastWithdraws'] = lastWithdraw[0]
        else:
            context['lastWithdraws'] = {}


        activity = UserActivity.objects.filter(user=customUser).order_by("-created_time")
        if activity:
            context['activity'] = activity
        else:
            context['activity'] = ''

        limitations = Limitation.objects.filter(user=customUser)

        productMap = {}
        for t in Limitation._meta.get_field('product').choices:
            productMap[t[0]] = t[1]

        intervalMap = {}
        for t in Limitation._meta.get_field('interval').choices:
            intervalMap[t[0]] = t[1]

        limitationDict = {
            'bet': [],
            'loss': [],
            'deposit': [],
            'withdraw': [],
        }
        productAccessArr = []
        for limitation in limitations:
            if limitation.limit_type == 0:
                betLimit = {
                    'amount': limitation.amount,
                    'productValue': limitation.product,
                    'product':  productMap[limitation.product]
                }
                limitationDict['bet'].append(betLimit)
            elif limitation.limit_type == LIMIT_TYPE_LOSS:
                lossMap = {
                    'amount': limitation.amount,
                    'intervalValue': limitation.interval,
                    'interval': intervalMap[limitation.interval]
                }
                limitationDict['loss'].append(lossMap)
                # limitationDict['loss'] = lossMap
            elif limitation.limit_type == LIMIT_TYPE_DEPOSIT:
                depositMap = {
                    'amount': limitation.amount,
                    'intervalValue': limitation.interval,
                    'interval': intervalMap[limitation.interval]
                }
                limitationDict['deposit'].append(depositMap)
                # limitationDict['deposit'] = depositMap
            elif limitation.limit_type == LIMIT_TYPE_WITHDRAW:
                withdrawMap = {
                    'amount': limitation.amount,
                    'intervalValue': limitation.interval,
                    'interval': intervalMap[limitation.interval]
                }
                limitationDict['withdraw'].append(withdrawMap)
                # limitationDict['withdraw'] = withdrawMap
            elif limitation.limit_type == LIMIT_TYPE_ACCESS_DENY:
                value = limitation.product
                productAccessMap = {
                    'productValue': value,
                    'product':  productMap[value]
                }
                productAccessArr.append(productAccessMap)


        # print(limitationDict)
        context['limitation'] = limitationDict
        context['productAccess'] = json.dumps(productAccessArr)
        context['accessDenyObj'] = productAccessArr
        
        return render(request, 'user_detail.html', context)


    def post(self, request):
        post_type = request.POST.get('type')
        user_id = request.POST.get('user_id')

        if post_type == 'edit_user_detail':
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            birthday = request.POST.get('birthday')
            address = request.POST.get('address')
            city = request.POST.get('city')
            zipcode = request.POST.get('zipcode')
            country = request.POST.get('country')
            user_id_img = request.POST.get('user_id_img')
            # upload image to S3
            self.upload_user_photo_id(username, user_id_img)

            CustomUser.objects.filter(pk=user_id).update(
                username=username, first_name=first_name, 
                last_name=last_name, email=email, 
                phone=phone, date_of_birth=birthday, 
                street_address_1=address, city=city,
                zipcode=zipcode, country=country)
            
            logger.info('Finished update user: ' + str(username) + 'info to DB')
            # print(CustomUser.objects.get(pk=user_id).id_image)

            return HttpResponseRedirect(reverse('xadmin:user_detail', args=[user_id]))
        
        elif post_type == 'update_message':
            admin_user = request.POST.get('admin_user')
            message = request.POST.get('message')

            UserActivity.objects.create(
                user = CustomUser.objects.filter(pk=user_id).first(),
                admin = CustomUser.objects.filter(username=admin_user).first(),
                message = message,
                activity_type = 3,
            )

            logger.info('Finished create activity to DB')
            return HttpResponseRedirect(reverse('xadmin:user_detail', args=[user_id]))

        elif post_type == 'activity_filter':
            activity_type = request.POST.get('activity_type')

            user = CustomUser.objects.get(pk=user_id)
            # print(str(activity_type))
            
            if activity_type == 'all':
                activitys = UserActivity.objects.filter(user=user).order_by('-created_time')
            else:
                activitys = UserActivity.objects.filter(user=user, activity_type=activity_type).order_by('-created_time')
            
            activitys = serializers.serialize('json', activitys)
            activitys = json.loads(activitys)
            response = []
            for act in activitys:
                actDict = {}
                try:
                    time = datetime.datetime.strptime(act['fields']['created_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    time = datetime.datetime.strptime(act['fields']['created_time'], "%Y-%m-%dT%H:%M:%SZ")
                time = time.strftime("%B %d, %Y, %I:%M %p")
                actDict['time'] = time
                adminUser = CustomUser.objects.get(pk=act['fields']['admin'])
                actDict['adminUser'] = str(adminUser.username)
                actDict['message'] = act['fields']['message']
                response.append(actDict)
            # print(str(response))

            return HttpResponse(json.dumps(response), content_type='application/json')

        elif post_type == 'get_user_transactions':
            time_from = request.POST.get('from')
            time_to = request.POST.get('to')
            pageSize = int(request.POST.get('pageSize'))
            fromItem = int(request.POST.get('fromItem'))
            endItem = fromItem + pageSize
            category = request.POST.get('transaction_category')
            user = CustomUser.objects.get(pk=user_id)

            if time_from == 'Invalid date':
                time_from = datetime.datetime(2000, 1, 1)
            if time_to == 'Invalid date':
                time_to = datetime.datetime(2400, 1, 1)

            logger.info('Transactions filter: username "' + str(user.username) + '" send transactions filter request which time form: ' + str(time_from) + ',to: ' + str(time_to) + ',category: ' + str(category))
            logger.info('Pagination: Maximum size of the page is ' + str(pageSize) + 'and from item #' + str(fromItem) + ' to item # ' + str(endItem))
            
            if category == 'all':
                transactions = Transaction.objects.filter(
                    Q(user_id=user) & Q(request_time__range=[time_from, time_to])
                ).order_by('-request_time')[fromItem:endItem]
                count = Transaction.objects.filter(Q(user_id=user) & Q(request_time__range=[time_from, time_to])).count()
            else:
                transactions = Transaction.objects.filter(
                    Q(user_id=user) & Q(transaction_type=category) & Q(request_time__range=[time_from, time_to])
                ).order_by('-request_time')[fromItem:endItem]
                count = Transaction.objects.filter(Q(user_id=user) & Q(transaction_type=category) & Q(request_time__range=[time_from, time_to])).count()

            response = {}
            if endItem >= count:
                response['isLastPage'] = True
            else:
                response['isLastPage'] = False

            if fromItem == 0:
                response['isFirstPage'] = True
            else:
                response['isFirstPage'] = False

            transactionsJson = serializers.serialize('json', transactions)
            transactionsList = json.loads(transactionsJson)
            statusMap = {}
            for t in Transaction._meta.get_field('status').choices:
                statusMap[t[0]] = t[1]

            for tran in transactionsList:
                tran['fields']['status'] = statusMap[tran['fields']['status']]
            
            # transactionsJson = json.dumps(transactionsList)
            response['transactions'] = transactionsList

            return HttpResponse(json.dumps(response), content_type='application/json')

        elif post_type == 'limitation_setting':
            
            # bet_limitation = request.POST.getlist('bet_limit[]')
            # bet_product = request.POST.getlist('game_type[]')
            # bet_product = list(map(lambda x : int(x), bet_product))
            print("passing data.....")
            print("user: " + str(user_id))
            loss_limitation = request.POST.getlist('loss_limit[]')
            loss_limitation = [item for item in loss_limitation if len(item) > 0]
            # print("loss_limitation type: " + str(type(loss_limitation)))
            print("origin loss_limitation: " + str(loss_limitation))
            loss_interval = request.POST.getlist('loss_limit_interval[]')
            # print("origin loss_interval: " + str(loss_interval))
            # loss_interval = list(map(lambda x : int(x) if x >= 0, loss_interval))
            loss_interval = [item for item in loss_interval if int(item) >= 0]
            deposit_limitation = request.POST.getlist('deposit_limit[]')
            # deposit_limitation = [float(item) for item in deposit_limitation if float(item) >= 0]
            deposit_interval = request.POST.getlist('deposit_limit_interval[]')
            # deposit_interval = list(map(lambda x : int(x), deposit_interval))
            deposit_interval = [int(item) for item in deposit_interval if int(item) >= 0]
            withdraw_limitation = request.POST.getlist('withdraw_limit[]')
            # deposit_limitation = [float(item) for item in withdraw_limitation if float(item) >= 0]
            withdraw_interval = request.POST.getlist('withdraw_limit_interval[]')
            withdraw_interval = [int(item) for item in withdraw_interval if int(item) >= 0]

            reason = request.POST.get('reasonTextarea')
            print(str(reason))

            # withdraw_interval = list(map(lambda x : int(x), withdraw_interval))

            # print("loss data.....")
            # print("loss_limitation: " + str(loss_limitation))
            # print("loss_interval: " + str(loss_interval))

            # print("deposit data.....")
            # print("deposit_limitation: " + str(deposit_limitation))
            # print("deposit_interval: " + str(deposit_interval))

            # print("withdraw data.....")
            # print("withdraw_limitation: " + str(withdraw_limitation))
            # print("withdraw_interval: " + str(withdraw_interval))

            access_deny_tags = request.POST.get('access_deny_tags')
            access_deny_tags = json.loads(access_deny_tags)
            # print(str(access_deny_tags))
            user = CustomUser.objects.get(pk=user_id)

            oldLimitMap = {
                LIMIT_TYPE_BET: {},
                LIMIT_TYPE_LOSS: {},
                LIMIT_TYPE_DEPOSIT: {},
                LIMIT_TYPE_WITHDRAW: {},
                LIMIT_TYPE_ACCESS_DENY: {}
            }

            limitations = Limitation.objects.filter(user=user)
            for limit in limitations:
                limitType = limit.limit_type
                if limitType == LIMIT_TYPE_ACCESS_DENY:
                    oldLimitMap[limitType][limit.product] = limit.amount
                else:
                    # oldLimitMap[limitType]['amount'] = limit.amount
                    oldLimitMap[limitType][limit.interval] = limit.amount


            print("oldLimitMap: " + str(oldLimitMap))
            # if bet_limitation:

            #     # delete
            #     for productType in oldLimitMap[LIMIT_TYPE_BET]:
            #         if productType not in bet_product:
            #             logger.info('Deleting bet limit for product type' + str(productType))
            #             Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_BET, product=productType).delete()

            #     # insert or update
            #     for i in range(len(bet_limitation)):
            #         if Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_BET, product=bet_product[i]).exists():
            #             logger.info('Update bet limit for product type for' + str(user))
            #             Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_BET, product=bet_product[i]).update(amount=bet_limitation[i])
            #         else:
            #             logger.info('Create new bet limit for product type for' + str(user))
            #             limitation = Limitation(
            #                 user= user,
            #                 limit_type=0,
            #                 amount=bet_limitation[i],
            #                 product=bet_product[i],
            #             )
            #             limitation.save()

            if access_deny_tags:
                for productType in oldLimitMap[LIMIT_TYPE_ACCESS_DENY]:
                    if productType not in access_deny_tags:
                        logger.info('Deleting access deny limit for product type ' + str(productType))
                        Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_ACCESS_DENY, product=productType).delete()

                for i in range(len(access_deny_tags)):
                    if Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_ACCESS_DENY, product=access_deny_tags[i]).exists():
                        pass
                    else:
                        logger.info('Create new access deny for product type for' + str(user))
                        limitation = Limitation(
                            user= user,
                            limit_type=LIMIT_TYPE_ACCESS_DENY,
                            amount=0,
                            product=access_deny_tags[i],
                        )
                        limitation.save()
            else:
                Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_ACCESS_DENY).delete()
                

            if loss_interval:
                # if Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_LOSS).exists():
                #     logger.info('Update loss limitation')
                #     Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_LOSS).update(amount=loss_limitation)
                # else:
                #     logger.info('Create a loss limitation')
                #     limitation = Limitation(
                #             user= user,
                #             limit_type=LIMIT_TYPE_LOSS,
                #             amount=loss_limitation,
                #         )
                #     limitation.save()

                # delete
                for intervalType in oldLimitMap[LIMIT_TYPE_LOSS]:
                    if intervalType not in loss_interval:
                        logger.info('Deleting loss limit for interval type: ' + str(intervalType))
                        Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_LOSS, interval=intervalType).delete()

                # insert or update
                for i in range(len(loss_limitation)):
                    if Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_LOSS, interval=loss_interval[i]).exists():
                        logger.info('Update loss limit for interval type: ' + str(user))
                        Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_LOSS, interval=loss_interval[i]).update(amount=loss_limitation[i])
                    else:
                        logger.info('Create new bet limit for product type for' + str(user))
                        limitation = Limitation(
                            user= user,
                            limit_type=LIMIT_TYPE_LOSS,
                            amount=loss_limitation[i],
                            interval=loss_interval[i],
                        )
                        limitation.save()
            else:
                Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_LOSS).delete()

            if deposit_interval:
                # logger.info('Update deposit limitation')
                # if Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_DEPOSIT).exists():
                #     Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_DEPOSIT).update(amount=deposit_limitation)
                # else:
                #     logger.info('Create deposit limitation')
                #     limitation = Limitation(
                #             user= user,
                #             limit_type=LIMIT_TYPE_DEPOSIT,
                #             amount=deposit_limitation,
                #         )
                #     limitation.save()

                # delete
                for intervalType in oldLimitMap[LIMIT_TYPE_DEPOSIT]:
                    if intervalType not in deposit_interval:
                        logger.info('Deleting loss limit for interval type: ' + str(intervalType))
                        Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_DEPOSIT, interval=intervalType).delete()

                # insert or update
                for i in range(len(deposit_limitation)):
                    # print("index: " + str(i))
                    if Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_DEPOSIT, interval=deposit_interval[i]).exists():
                        logger.info('Update loss limit for interval type: ' + str(user))
                        Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_DEPOSIT, interval=deposit_interval[i]).update(amount=deposit_limitation[i])
                    else:
                        logger.info('Create new bet limit for product type for' + str(user))
                        limitation = Limitation(
                            user= user,
                            limit_type=LIMIT_TYPE_DEPOSIT,
                            amount=deposit_limitation[i],
                            interval=deposit_interval[i],
                        )
                        limitation.save()
            else:
                Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_DEPOSIT).delete()

            if withdraw_interval:
                # if Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_WITHDRAW).exists():
                #     logger.info('Update withdraw limitation')
                #     Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_WITHDRAW).update(amount=withdraw_limitation)
                # else:
                #     logger.info('Create withdraw limitation')
                #     limitation = Limitation(
                #             user= user,
                #             limit_type=LIMIT_TYPE_WITHDRAW,
                #             amount=withdraw_limitation,
                #         )
                #     limitation.save()

                # delete
                for intervalType in oldLimitMap[LIMIT_TYPE_WITHDRAW]:
                    if intervalType not in withdraw_interval:
                        logger.info('Deleting loss limit for interval type: ' + str(intervalType))
                        Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_WITHDRAW, interval=intervalType).delete()

                # insert or update
                for i in range(len(withdraw_limitation)):
                    if Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_WITHDRAW, interval=withdraw_interval[i]).exists():
                        logger.info('Update loss limit for interval type: ' + str(user))
                        Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_WITHDRAW, interval=withdraw_interval[i]).update(amount=withdraw_limitation[i])
                    else:
                        logger.info('Create new bet limit for product type for' + str(user))
                        limitation = Limitation(
                            user= user,
                            limit_type=LIMIT_TYPE_WITHDRAW,
                            amount=withdraw_limitation[i],
                            interval=withdraw_interval[i],
                        )
                        limitation.save()
            else:
                Limitation.objects.filter(user=user, limit_type=LIMIT_TYPE_WITHDRAW).delete()

            return HttpResponseRedirect(reverse('xadmin:user_detail', args=[user_id]))

        elif post_type == 'block_user':
            action = request.POST.get('action')
            if action == 'block':
                user = CustomUser.objects.filter(pk=user_id).update(block=True, temporary_block_time=datetime.datetime.now())
            else:
                user = CustomUser.objects.filter(pk=user_id).update(block=False, temporary_block_time=None)

            return HttpResponseRedirect(reverse('xadmin:user_detail', args=[user_id]))
    
    def account_by_ip(self, userIp, username):
        relative_account = UserAction.objects.filter(ip_addr=userIp, event_type=0).exclude(user=username).values('user_id').distinct()
        # print(relative_account)

        accounts = []
        for item in relative_account:
            userDict = {}
            # user = CustomUser.objects.get(username=i.user)
            user = CustomUser.objects.get(pk=item['user_id'])
            userDict['id'] = user.pk
            userDict['username'] = user.username
            userDict['source'] = user.get_user_attribute_display
            userDict['channel'] = user.get_user_attribute_display
            depositSucc = Transaction.objects.filter(user_id=user, transaction_type=0, status=3).count()
            depositCount = Transaction.objects.filter(user_id=user, transaction_type=0).count()
            userDict['deposit'] = str(depositSucc) + '/' + str(depositCount)
            userDict['turnover'] = ''
            withdrawAmount = Transaction.objects.filter(user_id=user, transaction_type=1).aggregate(Sum('amount'))
            if withdrawAmount['amount__sum'] is None:
                withdrawAmount['amount__sum'] = 0
            userDict['withdrawal'] = withdrawAmount['amount__sum']
            userDict['contribution'] = ''
            userDict['riskLevel'] = 'A'
            accounts.append(userDict)
        return accounts




    def download_user_photo_id(self, username):
        aws_session = boto3.Session()
        s3_client = aws_session.client('s3')
        file_name = self.get_user_photo_file_name(username)

        success = False
        try:
            s3_response_object = s3_client.get_object(Bucket=settings.AWS_S3_ADMIN_BUCKET, Key=file_name)
            success = True
        except ClientError as e:
            # AllAccessDisabled error == bucket or object not found
            logger.error(e)
        except NoCredentialsError as e:
            logger.error(e)
        if not success:
            logger.info('Cannout find any image from this user: ' + username)
            return None

        object_content = s3_response_object['Body'].read()
        object_content = object_content.decode('utf-8')

        logger.info('Finished download username: ' + username + ' and file: ' + file_name + ' to S3!!!')
        return object_content


    def upload_user_photo_id(self, username, content):
        aws_session = boto3.Session()
        s3 = aws_session.resource('s3')
        file_name = self.get_user_photo_file_name(username)

        success = False
        try:
            obj = s3.Object(settings.AWS_S3_ADMIN_BUCKET, file_name)
            obj.put(Body=content)
            success = True
            logger.info('Finished upload username: ' + username + 'and file: ' + file_name + ' to S3!!!')
        except NoCredentialsError as e:
            logger.error(e)
        if not success:
            logger.info('Cannout upload image: ' + username)
            return None


    def get_user_photo_file_name(self, username):
        return username + '_photo_id'       


class UserListView(CommAdminView): 
    def get(self, request):

        # print(request.GET)
        search = request.GET.get('search')
        pageSize = request.GET.get('pageSize')
        offset = request.GET.get('offset')

        # print("search: " + str(search))

        if pageSize is None:
            pageSize = 20
        else: 
            pageSize = int(pageSize)

        if offset is None:
            offset = 0
        else:
            offset = int(offset)

        context = super().get_context()
        title = 'Member List'
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context['title'] = title
        context['time'] = timezone.now()
        if search:
            count = CustomUser.objects.filter(Q(pk__contains=search)|Q(username__contains=search)|Q(email__contains=search)|Q(phone__contains=search)|Q(first_name__contains=search)|Q(last_name__contains=search)).count()
            customUser = CustomUser.objects.filter(Q(pk__contains=search)|Q(username__contains=search)|Q(email__contains=search)|Q(phone__contains=search)|Q(first_name__contains=search)|Q(last_name__contains=search))[offset:offset+pageSize]

            if count == 0:
                count = CustomUser.objects.all().count()
                customUser = CustomUser.objects.all()[offset:offset+pageSize]
                context['searchError'] = _("No search data")

        else:
            count = CustomUser.objects.all().count()
            customUser = CustomUser.objects.all()[offset:offset+pageSize]

        if offset == 0:
            context['isFirstPage'] = True
        else:
            context['isFirstPage'] = False
        
        if count <= offset+pageSize:
            context['isLastPage'] = True
        else:
            context['isLastPage'] = False

        user_data = []
        for user in customUser:
            userDict = {}
            userDict['id'] = user.pk
            userDict['username'] = user.username
            userDict['source'] = str(user.get_user_attribute_display())
            userDict['risk_level'] = ''
            userDict['balance'] = user.main_wallet + user.other_game_wallet
            userDict['product_attribute'] = ''
            userDict['time_of_registration'] = user.time_of_registration
            userDict['ftd_time'] = user.ftd_time
            userDict['verfication_time'] = user.verfication_time
            userDict['id_location'] = user.id_location
            userDict['phone'] = user.phone
            userDict['address'] = str(user.street_address_1) + ', ' + str(user.street_address_2) + ', ' + str(user.city) + ', ' + str(user.state) + ', ' + str(user.country) 
            userDict['deposit_turnover'] = ''
            userDict['bonus_turnover'] = ''
            userDict['contribution'] = 0
            depositTimes = Transaction.objects.filter(user_id=user, transaction_type=0).count()
            withdrawTimes = Transaction.objects.filter(user_id=user, transaction_type=1).count()
            betTims = Transaction.objects.filter(user_id=user, transaction_type=2).count()
            activeDays = int(depositTimes) + int(withdrawTimes) + int(betTims)
            userDict['active_days'] = ''
            userDict['bet_platform'] = user.product_attribute


            userDict['last_login_time'] = user.last_login_time
            userDict['last_betting_time'] = user.last_betting_time
            userDict['login'] = UserAction.objects.filter(user=user, event_type=0).count()
            userDict['betting'] = Transaction.objects.filter(user_id=user, transaction_type=2).count()
            userDict['turnover'] = ''
            userDict['deposit'] = Transaction.objects.filter(user_id=user, transaction_type=0).count()
            userDict['deposit_amount'] = Transaction.objects.filter(user_id=user, transaction_type=0).aggregate(Sum('amount'))
            userDict['withdrawal'] = Transaction.objects.filter(user_id=user, transaction_type=1).count()
            userDict['withdrawal_amount'] = Transaction.objects.filter(user_id=user, transaction_type=1).aggregate(Sum('amount'))
            userDict['last_login_ip'] = UserAction.objects.filter(user=user, event_type=0).order_by('-created_time').first()
            # print("object: " + str(userDict))
            user_data.append(userDict)
        
        context['user_data'] = user_data


        return render(request, 'user_list.html', context)

    
    def post(self, request):
        post_type = request.POST.get('type')
        # user_id = request.POST.get('user_id')

        if post_type == 'user_list_time_range_filter':
            time_from = request.POST.get('from')
            time_to = request.POST.get('to')
            # print("from: " + str(time_from) + 'to: ' + str(time_to))
            Customuser = CustomUser.objects.all()
            # context['customuser'] = Customuser
            
            updated_data = []
            for user in Customuser:
                userDict = {}
                userDict['login_times'] = UserAction.objects.filter(user=user, event_type=0, created_time__range=[time_from, time_to]).count()
                userDict['betting_times'] = Transaction.objects.filter(user_id=user, transaction_type=2, request_time__range=[time_from, time_to]).count()
                userDict['deposit_times'] = Transaction.objects.filter(user_id=user, transaction_type=0, request_time__range=[time_from, time_to]).count()
                userDict['deposit_amount'] = Transaction.objects.filter(user_id=user, transaction_type=0, request_time__range=[time_from, time_to]).aggregate(Sum('amount'))
                userDict['withdrawal_times'] = Transaction.objects.filter(user_id=user, transaction_type=1, request_time__range=[time_from, time_to]).count()
                userDict['withdrawal_amount'] = Transaction.objects.filter(user_id=user, transaction_type=1, request_time__range=[time_from, time_to]).aggregate(Sum('amount'))
                # add GGR amount, turnover amount, contribution
                updated_data.append(userDict)
                # print(userDict)
            
            # print("sending data")
            return HttpResponse(json.dumps(updated_data), content_type="application/json")

        elif post_type == 'user_list_filter':
            time_from = request.POST.get('from')
            time_to = request.POST.get('to')
            pageSize = int(request.POST.get('pageSize'))
            fromItem = int(request.POST.get('fromItem'))
            endItem = fromItem + pageSize

            if time_from == 'Invalid date':
                time_from = datetime.datetime(2000, 1, 1)
            if time_to == 'Invalid date':
                time_to = datetime.datetime(2400, 1, 1)

            # print('fromItem: ' + str(fromItem))
            # print('endItem: ' + str(endItem))
            users = CustomUser.objects.all()[fromItem:endItem]
            count = CustomUser.objects.all().count()
            # print(str(count))
            # usersJson = serializers.serialize('json', users)

            # usersList = json.loads(usersJson)            
            response = {}
            if endItem >= count:
                response['isLastPage'] = True
            else:
                response['isLastPage'] = False

            if fromItem == 0:
                response['isFirstPage'] = True
            else:
                response['isFirstPage'] = False
            
            sourceMap = {}
            for t in CustomUser._meta.get_field('user_attribute').choices:
                sourceMap[t[0]] = t[1]

            usersList = []
            for user in users:
                userDict = {}
                userDict['id'] = user.pk
                userDict['username'] = user.username
                userDict['source'] = str(sourceMap[user.user_attribute])
                userDict['balance'] = user.main_wallet + user.other_game_wallet
                userDict['product_attribute'] = ''
                userDict['time_of_registration'] = str(user.time_of_registration)
                userDict['ftd_time'] = str(user.ftd_time)
                userDict['verfication_time'] = str(user.verfication_time)
                userDict['id_location'] = user.id_location
                userDict['phone'] = user.phone
                userDict['address'] = str(user.street_address_1) + ', ' + str(user.street_address_2) + ', ' + str(user.city) + ', ' + str(user.state) + ', ' + str(user.country) 
                userDict['deposit_turnover'] = ''
                userDict['bonus_turnover'] = ''
                userDict['contribution'] = 0
                depositTimes = Transaction.objects.filter(user_id=user, transaction_type=0).count()
                # print(type(depositTimes))
                withdrawTimes = Transaction.objects.filter(user_id=user, transaction_type=1).count()
                betTimes = Transaction.objects.filter(user_id=user, transaction_type=2).count()
                activeDays = int(depositTimes) + int(withdrawTimes) + int(betTimes)
                userDict['active_days'] = ''
                userDict['bet_platform'] = user.product_attribute

                # print("object: " + str(userDict))
                usersList.append(userDict)
            response['usersList'] = usersList
            # response = json.loads(response)
            return HttpResponse(json.dumps(response), content_type="application/json")    
            

class ChangePassword(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            username = request.data['username']
            password = request.data['password']
            user = get_user_model().objects.get(username=username)
            user.set_password(password)
            user.save()
            return Response('Success')
        except:
            return Response('Failed')

class CheckUsernameExist(View):
    def get(self, request, *args, **kwargs):
        username = self.request.GET['username']
        user = get_user_model().objects.filter(username=username)
        if user:
            return HttpResponse('Exist')
        return HttpResponse('Valid')

class GenerateActivationCode(APIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data['username']
        user = get_user_model().objects.filter(username=username)
        random_num = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        user.update(activation_code=random_num)
    
        DOMAIN = settings.DOMAIN
        r = requests.post(DOMAIN + 'operation/api/notification', {
            'content':               random_num, 
            'notification_choice':   'U',
            'notification_method':   'S',
            'notifiers':             user[0].pk
        })
        
        return Response(status=status.HTTP_200_OK)

class VerifyActivationCode(APIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data['username']
        code = request.data['code']
        user = get_user_model().objects.filter(username=username)
        if user[0].activation_code == code:
            user.update(active=True)
            user.update(activation_code='')
            return Response({'status': 'Success'})
        return Response({'status': 'Failed'})




class UserSearchAutocomplete(View):
    def get(self, request, *args, **kwargs):
        search = request.GET['search']

        logger.info('Search user, key: ' + search)
        search_id = CustomUser.objects.filter(pk__contains=search)
        search_username = CustomUser.objects.filter(username__contains=search)
        search_email = CustomUser.objects.filter(email__contains=search)
        search_phone = CustomUser.objects.filter(phone__contains=search)
        search_first_name = CustomUser.objects.filter(first_name__contains=search)
        search_last_name = CustomUser.objects.filter(last_name__contains=search)

        search_id = serializers.serialize('json', search_id)
        search_username = serializers.serialize('json', search_username)
        search_email = serializers.serialize('json', search_email)
        search_phone = serializers.serialize('json', search_phone)
        search_first_name = serializers.serialize('json', search_first_name)
        search_last_name = serializers.serialize('json', search_last_name)

        search_id = json.loads(search_id)
        search_username = json.loads(search_username)
        search_email = json.loads(search_email)
        search_phone = json.loads(search_phone)
        search_first_name = json.loads(search_first_name)
        search_last_name = json.loads(search_last_name)
        response = {}

        id_data = []
        for user in search_id:
            userMap = {}
            userMap['id'] = user['pk']
            id_data.append(userMap)
        response['id'] = id_data

        username_data = []
        for user in search_username:
            userMap = {}
            userMap['id'] = user['pk']
            userMap['username'] = user['fields']['username']
            username_data.append(userMap)
        response['username'] = username_data

        email_data = []
        for user in search_email:
            userMap = {}
            userMap['id'] = user['pk']
            userMap['email'] = user['fields']['email']
            email_data.append(userMap)
        response['email'] = email_data

        phone_data = []
        for user in search_phone:
            userMap = {}
            userMap['id'] = user['pk']
            userMap['phone'] = user['fields']['phone']
            phone_data.append(userMap)
        response['phone'] = phone_data

        first_name_data = []
        for user in search_first_name:
            userMap = {}
            userMap['id'] = user['pk']
            userMap['firstName'] = user['fields']['first_name']
            first_name_data.append(userMap)
        response['firstName'] = first_name_data

        last_name_data = []
        for user in search_last_name:
            userMap = {}
            userMap['id'] = user['pk']
            userMap['lastName'] = user['fields']['last_name']
            last_name_data.append(userMap)
        response['lastName'] = last_name_data
        # print(str(response))
        logger.info('Search response: ' + json.dumps(response))
        return HttpResponse(json.dumps(response), content_type='application/json')


class ValidateAndResetPassowrd(APIView):

    permission_classes = (IsAuthenticated, )

    def post(self, request):
        username = request.data['username']
        current = request.data['current_password']
        new = request.data['new_password']

        user = CustomUser.objects.get(username=username)
        if not user.check_password(current):
            return Response({'status': 'Failed'})
        user.set_password(new)
        user.save()
        return Response({'status': 'Success'})

class CancelRegistration(APIView):

    permission_classes = (AllowAny, )

    def post(self, request):
        username = request.data['username']
        user = CustomUser.objects.get(username=username)
        user.delete()
        return Response(status=status.HTTP_200_OK)



