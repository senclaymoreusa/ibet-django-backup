from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as django_login, logout as django_logout
from django.contrib import messages
from django.contrib.auth import get_user_model

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy

from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.decorators.debug import sensitive_post_parameters
from django.views import generic
from django.views import View

from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import timedelta
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth, TruncDate, Coalesce
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from django.utils.crypto import get_random_string

from django_rest_passwordreset.signals import reset_password_token_created
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.views import get_password_reset_token_expiry_time

from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth, Coalesce
from django.template.defaulttags import register

from rest_auth.models import TokenModel
from rest_auth.app_settings import TokenSerializer, JWTSerializer, create_token

from allauth.account.utils import complete_signup
from allauth.account import app_settings as allauth_settings

from dateutil.relativedelta import relativedelta
from users.serializers import GameSerializer, CategorySerializer, UserDetailsSerializer, RegisterSerializer, LoginSerializer, CustomTokenSerializer, NoticeMessageSerializer, FacebookRegisterSerializer, FacebookLoginSerializer, BalanceSerializer
from users.serializers import LazyEncoder
from users.forms import RenewBookForm, CustomUserCreationForm
from users.models import Game, CustomUser, Category, Config, NoticeMessage, UserAction, UserActivity, Limitation, GameRequestsModel
from games.models import Game as NewGame
from accounting.models import Transaction
from threading import Timer
from xadmin.views import CommAdminView
from users.views.helper import *
from django.contrib.auth.hashers import make_password, check_password

from operation.views import send_sms

import datetime
import logging
import os
import base64
import uuid
import csv
import random
import simplejson as json
import decimal
from utils.constants import *
import requests

import xmltodict

from django.db import transaction

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
        data = NewGame.objects.filter(pk=id)
        return data


class CategoryAPIListView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class UserDetailsView(RetrieveUpdateAPIView):
    serializer_class = UserDetailsSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user = self.get_object()
            serializer = UserDetailsSerializer(user)
            if checkUserBlock(self.request.user):
                errorMessage = _('The current user is blocked!')
                data = {
                    "errorCode": ERROR_CODE_BLOCK,
                    "errorMsg": {
                        "detail": [errorMessage]
                    }
                }
                return Response(data)
            return Response(serializer.data)
        except Exception as e:
            logger.error("Error getting user details", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            user = self.get_object()
            if checkUserBlock(self.request.user):
                errorMessage = _('The current user is blocked!')
                data = {
                    "errorCode": ERROR_CODE_BLOCK,
                    "errorMsg": {
                        "detail": [errorMessage]
                    }
                }
                return Response(data)

            serializer = UserDetailsSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            logger.info("User details format is not correct", e)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Error updating user details", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

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
            created_time=timezone.now()
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


# class BlockedUserException(APIException):
#     status_code = 404
#     default_detail = _('Current user is blocked!')
#     default_code = '100'

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
        if checkUserBlock(self.user):
            errorMessage = _('The current user is blocked!')
            data = {
                "errorCode": ERROR_CODE_BLOCK,
                "errorMsg": {
                    "detail": [errorMessage]
                }
            }
            return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")
        if self.user.active == False:
            # raise InactiveUserException
            errorMessage = _('Please activate your account!')
            data = {
                "errorCode": ERROR_CODE_INACTIVE,
                "errorMsg": {
                    "detail": [errorMessage]
                }
            }
            return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")

        if getattr(settings, 'REST_USE_JWT', False):
            
            self.token = jwt_encode(self.user)
        else:
            self.token = create_token(self.token_model, self.user, self.serializer)

        customUser = CustomUser.objects.filter(username=self.user)
        action = UserAction(
            user= customUser.first(),
            ip_addr=self.request.META['REMOTE_ADDR'],
            event_type=0,
            created_time=timezone.now()
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
        try:
            self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})

            if self.serializer.is_valid(raise_exception=True):
                return self.login()
        except Exception as e:
            errorMessage = _('Invalid username/ passowrd')
            data = {}
            data["errorCode"] = ERROR_CODE_INVALID_INFO
            data["errorMsg"] = {
                "detail": [errorMessage]
            }
            # TODO: ADD LOG
            return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")
        


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
            created_time=timezone.now()
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


class SendEmail(APIView):

    permission_classes = (AllowAny,)

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
            email_content = _('Please use the referral link to register your new account: ') + settings.HOST_URL +  'home/' + self.request.GET['referralid']

        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        from_email = Email(from_email_address)
        to_email = Email(to_email_address)
        subject = email_subject
        content = Content("text/plain", email_content)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        return Response(status=status.HTTP_200_OK)


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
from ..serializers import LanguageCodeSerializer
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

        try:
            languageCode = 'en'
            if LANGUAGE_SESSION_KEY in request.session:
                languageCode = request.session[LANGUAGE_SESSION_KEY]
    
            # print('get: ' + languageCode)
            logger.info("Getting the language code: {}".format(languageCode))
            return Response({'languageCode': languageCode}, status = status.HTTP_200_OK)  
        
        except:
            logger.error("Error getting language code")
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

class NoticeMessageView(ListAPIView):
    serializer_class = NoticeMessageSerializer
    queryset = NoticeMessage.objects.all()

class ReferralAward(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        referral_id = request.GET.get('referral_id')
        current_referred = request.GET.get('referred')
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
        
        return Response('Update successful')


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

            # create = Transaction.objects.create(
            #     user_id=CustomUser.objects.filter(username=username).first(), 
            #     amount=balance, 
            #     transaction_type=1,
            #     currency=0,
            # )

            # action = UserAction(
            #     user= CustomUser.objects.filter(username=username).first(),
            #     ip_addr=self.request.META['REMOTE_ADDR'],
            #     event_type=4,
            #     dollar_amount=balance
            # )
            # action.save()
            return HttpResponse('Withdraw Success')

class Activation(APIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        
        email = request.data['email']

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
        return Response('Email has been sent!')

class ActivationVerify(APIView):

    permission_classes = (AllowAny,)
    
    def post(self, request):

        token = request.data['token']

        user = get_user_model().objects.filter(activation_code=token)
        if len(user) != 0:
            user.update(active=True)
            user.update(activation_code='', modified_time=timezone.now())
            return Response('Success')
        return Response('The link has expired')


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
            raise BlockedUserException
        if self.user.active == False:
            # print('User not active')
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

    def post(self, request, *args, **kwargs):

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

        return Response({'username': username, 'password': password}, status=status.HTTP_200_OK)


class UpdateEmail(APIView):

    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):

        old_email = request.data['old_email']
        new_email = request.data['new_email']

        check_duplicate = get_user_model().objects.filter(email__iexact=new_email)
        if check_duplicate:
            return Response('Duplicate')
            
        user = CustomUser.objects.filter(email=old_email)
        user.update(email=new_email, modified_time=timezone.now())
        return Response('Success')


class CheckEmailExixted(APIView):

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        
        email = request.GET.get('email')
        check_exist = get_user_model().objects.filter(email__iexact=email)
        if check_exist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)
        
        
class GetUsernameByReferid(APIView):

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        refer_id = request.GET.get('referid')
        user = get_user_model().objects.filter(referral_code=refer_id)
        if user:
            return Response(user[0].username)
        return Response('Failed')

class GenerateForgetPasswordCode(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):

        email = request.data['email']
        user = get_user_model().objects.filter(email__iexact=email)
        if user:
            code = ''.join([str(random.randint(0, 9)) for i in range(4)])
            user.update(reset_password_code=code)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SendResetPasswordCode(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):

        email = request.data['email']
        user = get_user_model().objects.filter(email__iexact=email)
        reset_password_code = user[0].reset_password_code
        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        from_email = Email('ibet@ibet.com')
        to_email = Email(email)
        subject =  str(_('Reset Password'))
        content_text = str(_('Use this code to reset your password '))
        content = Content("text/plain", content_text + "\n {} \n \n {} ".format(reset_password_code, 'ibet'))
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body = mail.get())
        return Response(status=status.HTTP_200_OK)


class VerifyResetPasswordCode(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):

        email = request.data['email']
        code = request.data['code']
        password = request.data['password']
        user = get_user_model().objects.filter(email__iexact=email)
        verify = user[0].reset_password_code
        if code == verify:
            user.update(reset_password_code='')
            user = get_user_model().objects.get(email__iexact=email)
            user.set_password(password)
            user.save()
            return Response('Success')
        else:
            return Response('Failed')


class ChangeAndResetPassword(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):

        email = request.data['email']

        password = request.data['password']

        user = get_user_model().objects.get(email__iexact=email)
        user.set_password(password)
        user.save()
        return Response('Success')

     
from xadmin.views import CommAdminView
from django.core import serializers
from django.http import HttpResponse
from django.db.models import Sum
from datetime import timedelta
from django.db.models import Q
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from django.conf import settings   
            

class ChangePassword(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            username = request.data['username']
            password = request.data['password']
            user = get_user_model().objects.get(username=username)
            if checkUserBlock(user):
                data = {}
                errorMessage = _('The current user is blocked!')
                data["errorCode"] = ERROR_CODE_BLOCK
                data["errorMsg"] = {
                    "detail": [errorMessage]
                }
            return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")

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
            return HttpResponse(status=400)
        return HttpResponse(status=200)

'''
class GenerateActivationCode(APIView):

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        user = get_user_model().objects.filter(username=username)
        random_num = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        user.update(activation_code=random_num)

        send_sms(str(random_num), user[0].pk)
    
        return Response(status=status.HTTP_200_OK)
'''


class GenerateActivationCode(APIView):

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        username = data['username']
        postType = data['type']
        try:
            user = get_user_model().objects.filter(username=username)
            if postType == "change_member_phone_num":
                phone = data['phone']
                time = timezone.now() - datetime.timedelta(days=1)
                event_filter = Q(user=user[0])&Q(event_type=EVENT_CHOICES_SMS_CODE)&Q(created_time__gt=time)
                count = UserAction.objects.filter(event_filter).count()
                if count <= 300:
                    random_num = ''.join([str(random.randint(0, 9)) for _ in range(4)])

                    # DB transaction atomic as a context manager:
                    with transaction.atomic():
                        user.update(activation_code=random_num)

                        send_sms(str(random_num), user[0].pk)

                        action = UserAction(
                            user=user[0],
                            event_type=EVENT_CHOICES_SMS_CODE,
                            created_time=timezone.now()
                        )
                        action.save()

                        return Response(status=status.HTTP_201_CREATED)

                return Response(ERROR_CODE_MAX_EXCEED)
            elif postType == "change_member_email":
                email = data['email']
                random_num = ''.join([str(random.randint(0, 9)) for _ in range(4)])

                # DB transaction atomic as a context manager:
                with transaction.atomic():
                    user.update(activation_code=random_num)

                    from_email_address = 'claymore@claymoreusa.com'
                    # to_email_address = user[0].email
                    to_email_address = email
                    email_subject = str(_('Activation Code')) + ' '
                    email_content = str(_('Your activation code is ')) + str(random_num)

                    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
                    from_email = Email(from_email_address)
                    to_email = Email(to_email_address)
                    subject = email_subject
                    content = Content("text/plain", email_content)
                    mail = Mail(from_email, subject, to_email, content)
                    response = sg.client.mail.send.post(request_body=mail.get())

                    action = UserAction(
                        user=user[0],
                        event_type=EVENT_CHOICES_SMS_CODE,
                        created_time=timezone.now()
                    )
                    action.save()

                    return Response(status=status.HTTP_201_CREATED)
            else:
                # leave this for active code, currently no SMS system available
                random_num = ''.join([str(random.randint(0, 9)) for _ in range(4)])
                user.update(activation_code=random_num)
                send_sms(str(random_num), user[0].pk)
        except Exception as e:
            logger.error("Error Generating Activation Code: ", e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


class VerifyActivationCode(APIView):

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        code = request.data['code']
        user = get_user_model().objects.filter(username=username)
        
        # last_verify_action = UserAction.objects.filter(Q(user=user[0])&Q(event_type=EVENT_CHOICES_SMS_CODE)).order_by('-created_time')

        # delta = timezone.now() - timedelta(seconds=180)
        # if verification_time < last_verify_action[0].created_time:
        if user[0].activation_code == code:
            user.update(active=True)
            user.update(activation_code='')
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     return Response(ERROR_CODE_TIME_EXCEED)


class UserSearchAutocomplete(View):
    def get(self, request, *args, **kwargs):

        #search keyword in username/phone/first name/last name/email
        try:
            search = request.GET['search']
            # block = request.GET['block'] == 'true'
            
            logger.info('Search user, key: ' + search)
            # search_id = CustomUser.objects.filter(Q(pk__contains=search)&Q(block=block))
            # search_username = CustomUser.objects.filter(Q(username__contains=search)&Q(block=block))
            # search_email = CustomUser.objects.filter(Q(email__contains=search)&Q(block=block))
            # search_phone = CustomUser.objects.filter(Q(phone__contains=search)&Q(block=block))
            # search_first_name = CustomUser.objects.filter(Q(first_name__contains=search)&Q(block=block))
            # search_last_name = CustomUser.objects.filter(Q(last_name__contains=search)&Q(block=block))

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

        except Exception as e:
            logger.error("Error from searching user: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


class ValidateAndResetPassowrd(APIView):

    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        
        current = request.data['current_password']
        new = request.data['new_password']
        user = self.request.user

        if not user.check_password(current):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new)
        user.save()
        return Response(status=status.HTTP_200_OK)


class CancelRegistration(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):

        username = request.data['username']
        user = CustomUser.objects.get(username=username)
        user.delete()
        return Response(status=status.HTTP_200_OK)

from users.views.helper import set_loss_limitation, set_deposit_limitation, set_temporary_timeout, set_permanent_timeout, get_old_limitations

class SetLimitation(View):

    def post(self, request, *args, **kwargs):

        try:
            data = json.loads(request.body)
            userId = data['user_id']
            limit = data['limit']
            interval = data['interval']
            limit_type = data['type']
            user = CustomUser.objects.get(pk=userId)

            if checkUserBlock(user):
                data = {}
                errorMessage = _('The current user is blocked!')
                data["errorCode"] = ERROR_CODE_BLOCK
                data["errorMsg"] = {
                    "detail": [errorMessage]
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")
            
            # print(limit, interval, user_id, limit_type)
            oldLimitMap = get_old_limitations(userId)
            # print(oldLimitMap)

            if limit_type == 'loss':
                otherLimits = oldLimitMap[LIMIT_TYPE_LOSS]
                set_loss_limitation(userId, limit, interval, oldLimitMap, user)
            elif limit_type == 'deposit':
                set_deposit_limitation(userId, limit, interval, oldLimitMap, user)

            return HttpResponse(('Successfully set the {} limitation'.format(limit_type)), status = 200)

        except Exception as e:
            logger.error("Error from setting user's limitation: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)      

class DeleteLimitation(View):

    def post(self, request, *args, **kwargs):
        
        try:
            data = json.loads(request.body)
            userId = data['user_id']
            user = CustomUser.objects.get(pk=userId)

            if checkUserBlock(user):
                data = {}
                errorMessage = _('The current user is blocked!')
                data["errorCode"] = ERROR_CODE_BLOCK
                data["errorMsg"] = {
                    "detail": [errorMessage]
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")
            
            # limit = data['limit']
            interval = data['interval']
            limit_type = data['type']
            limit_id = data['id']
            
            if limit_type == 'deposit':
                limit_type = LIMIT_TYPE_DEPOSIT
            elif limit_type == 'loss':
                limit_type = LIMIT_TYPE_LOSS

            limit = Limitation.objects.get(user=user, limit_type=limit_type, interval=interval)
            time = timezone.now() + datetime.timedelta(days=1)
            limit.expiration_time = time
            limit.temporary_amount = limit.amount
            limit.amount = None
            limit.save()
            # return HttpResponse(('Successfully delete the {} limitation'.format(limit_type)), status = 200)
            message = 'Successfully delete the {} limitation and interval is {}'.format(limit_type, interval)
            current_tz = timezone.get_current_timezone()
            time = time.astimezone(current_tz)
            expiration_timeStr = str(time.astimezone(current_tz))

            response = {
                "expire_time": expiration_timeStr,
                "message": message
            }
            
            return HttpResponse(json.dumps(response, cls=LazyEncoder), content_type="application/json")
        
        except Exception as e:
            logger.error("Error from delete user's limitation: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)



class CancelDeleteLimitation(View):

    def post(self, request, *args, **kwargs):
        
        try:
            data = json.loads(request.body)
            userId = data['user_id']
            user = CustomUser.objects.get(pk=userId)

            if checkUserBlock(user):
                data = {}
                errorMessage = _('The current user is blocked!')
                data["errorCode"] = ERROR_CODE_BLOCK
                data["errorMsg"] = {
                    "detail": [errorMessage]
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")

            # limit = data['limit']
            interval = data['interval']
            limit_type = data['type']
            limit_id = data['id']

            if limit_type == 'deposit':
                limit_type = LIMIT_TYPE_DEPOSIT
            elif limit_type == 'loss':
                limit_type = LIMIT_TYPE_LOSS

            limit = Limitation.objects.get(user=user, limit_type=limit_type, interval=interval)
            limit.expiration_time = None
            limit.amount = limit.temporary_amount
            limit.temporary_amount = None
            limit.save()

            return HttpResponse(('Successfully cancel the {} limitation action'.format(limit_type)), status=200)

        except Exception as e:
            logger.error("Error from delete user's limitation: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

class GetLimitation(View):

    def get(self, request, *args, **kwargs):

        try:
            userId = request.GET.get('id')
            # limit_type = request.GET.get('type')
            # limit_type = limit_type.capitalize()
            # limitDict = dict(LIMIT_TYPE)
            # for key, value in limitDict.items():
            #     if value == limit_type:
            #         limit_type = key

            user = CustomUser.objects.get(pk=userId)

            if checkUserBlock(user):
                errorMessage = _('The current user is blocked!')
                data = {}
                data["errorCode"] = ERROR_CODE_BLOCK
                data["errorMsg"] = {
                    "detail": [errorMessage]
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")

            userJson = serializers.serialize('json', [user])
            userJson = json.loads(userJson)
            # print(userJson)

            # print(user)
            userLimitation = Limitation.objects.filter(user=user)

            intervalMap = {}
            for t in Limitation._meta.get_field('interval').choices:
                intervalMap[t[0]] = t[1]

            limitationDict = {
                'bet': [],
                'loss': [],
                'deposit': [],
                'withdraw': [],
                'tempBlock': {},
                'permBlock': {}
            }
            for limitation in userLimitation:
                temporary_amount = decimal.Decimal(0) if limitation.temporary_amount is None else  decimal.Decimal(limitation.temporary_amount)
                amount = None if limitation.amount is None else decimal.Decimal(limitation.amount)
                expiration_timeStr = ''
                expiration_time = ""
                if limitation.expiration_time:
                    current_tz = timezone.get_current_timezone()
                    expiration_time = limitation.expiration_time.astimezone(current_tz)
                    expiration_timeStr = str(limitation.expiration_time.astimezone(current_tz))

                if not limitation.amount and not expiration_time:
                    continue
                else:
                    if expiration_time and expiration_time <= timezone.now():
                        continue
                
                if limitation.limit_type == LIMIT_TYPE_LOSS:
                    lossMap = {
                        'amount': amount,
                        'intervalValue': limitation.interval,
                        'interval': intervalMap[limitation.interval],
                        'limitId': limitation.pk,
                        'temporary_amount': temporary_amount,
                        'expiration_time': expiration_timeStr
                    }
                    limitationDict['loss'].append(lossMap)
                elif limitation.limit_type == LIMIT_TYPE_DEPOSIT:
                    
                    depositMap = {
                        'amount': amount,
                        'intervalValue': limitation.interval,
                        'interval': intervalMap[limitation.interval],
                        'limitId': limitation.pk,
                        'temporary_amount': temporary_amount,
                        'expiration_time': expiration_timeStr
                    }
                    limitationDict['deposit'].append(depositMap)
        
            if user.temporary_block_interval:
                # print(user.temporary_block_timespan)
                # print(userJson[0]['fields']['temporary_block_timespan'])
                # timeList = userJson[0]['fields']['temporary_block_timespan'].split(' ')
                # time = timeList[0]
                # time = int(time)
                tempMap = {
                    'temporary_block': user.temporary_block_interval
                }
                limitationDict['tempBlock'] = tempMap

            if user.permanent_block_interval:
                permanentMap = {
                    'permanent_block': user.permanent_block_interval
                }
                limitationDict['permBlock'] = permanentMap
                # print(limitationDict)

            return HttpResponse(json.dumps(limitationDict, cls=DjangoJSONEncoder), content_type="application/json", status=200)
        
        except Exception as e:
            logger.error("Error from getting user's limitations: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

class SetBlockTime(View):

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            lock_timespan = data['timespan']
            userId = data['userId']

            user = CustomUser.objects.get(pk=userId)

            if checkUserBlock(user):
                data = {}
                errorMessage = _('The current user is blocked!')
                data["errorCode"] = ERROR_CODE_BLOCK
                data["errorMsg"] = {
                    "detail": [errorMessage]
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")

            # lock_type = data['type']
            tempIntervals = list(map(lambda x: x[0], TEMPORARY_INTERVAL))
            # print(userId, lock_type, lock_timespan)
            if lock_timespan not in tempIntervals:
                set_permanent_timeout(user, lock_timespan)
                set_temporary_timeout(user, -1)
            else:
                set_temporary_timeout(user, lock_timespan)
                set_permanent_timeout(user, -1)
            
            return HttpResponse(('Successfully block the userId: {0} for lock timespan option {1}'.format(userId, lock_timespan)), status=200)
        
        except Exception as e:
            logger.error("Error from setting user's blocking time : ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        
 
class MarketingSettings(View):

    def get(self, request, *args, **kwargs):

        try:
            userId = request.GET['userId']
            user = CustomUser.objects.get(pk=userId)

            if checkUserBlock(user):
                data = {}
                errorMessage = _('The current user is blocked!')
                data["errorCode"] = ERROR_CODE_BLOCK
                data["errorMsg"] = {
                    "detail": [errorMessage]
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")

            contact_methods = user.contact_methods

            response = {
                "email": False,
                "phone": False,
                "sms": False,
                "postal": False
            }
            
            if contact_methods:
                contact_methods_list = contact_methods.split(',')
                for i in contact_methods_list:
                    response[i] = True

            response.update(socialMedia=user.social_media)

            # print(response)
            logger.info("Sending marketing settings response: {}".format(json.dumps(response)))
            return HttpResponse(json.dumps(response), content_type='application/json', status=200)
        
        except Exception as e:
            logger.error("Error getting marketing for a user", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):

        try:
            data = json.loads(request.body)
            # print(data)
            email = data['email']
            phone = data['phone']
            sms = data['sms']
            postal_mail = data['postalMail']
            social_media = data['socialMedia']
            userId = data['userId']

            user = CustomUser.objects.get(pk=userId)

            if checkUserBlock(user):
                errorMessage = _('The current user is blocked!')
                data = {}
                data["errorCode"] = ERROR_CODE_BLOCK
                data["errorMsg"] = {
                    "detail": [errorMessage]
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")

            contact_methods = []
            # print(email, phone, sms, postal_mail, social_media, userId)
            if email:
                contact_methods.append("email")
            if phone:
                contact_methods.append("phone")
            if sms:
                contact_methods.append("sms")
            if postal_mail:
                contact_methods.append("postal")
            
            contact_methods_str = ''
            contact_methods_str = ','.join(str(i) for i in contact_methods)

            # print(contact_methods_str)
            # print(social_media)
            user.social_media = social_media
            user.contact_methods = contact_methods_str
            user.save()

            logger.info("Marketing settings for user: {}".format(str(user.username)))
            logger.info("Email: {}, Phone: {}, SMS: {}, Mail: {}, Social Media: {}".format(email, phone, sms, postal_mail, social_media))

            return HttpResponse(('Successfully set the marketing setting'), status=200)

        except Exception as e:
            logger.error("Error setting marketing for a user", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)



class PrivacySettings(View):

    def get(self, request, *args, **kwargs):

        try:
            userId = request.GET['userId']
            user = CustomUser.objects.get(pk=userId)

            if checkUserBlock(user):
                errorMessage = _('The current user is blocked!')
                data = {}
                data["errorCode"] = ERROR_CODE_BLOCK
                data["errorMsg"] = {
                    "detail": [errorMessage]
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")
            
            
            response = {
                "bonus": user.bonusesProgram,
                "vip": user.vipProgram
            }

            logger.info("Sending privacy settings response: {}".format(json.dumps(response)))
            return HttpResponse(json.dumps(response), content_type='application/json', status=200)

        except Exception as e:
            logger.error("Error getting privacy setting for a user", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


    def post(self, request, *args, **kwargs):

        try:
            data = json.loads(request.body)

            bonuses = data['bonuses']
            vip = data['vip']
            userId = data['userId']

            user = CustomUser.objects.get(pk=userId)

            if checkUserBlock(user):
                errorMessage = _('The current user is blocked!')
                data = {}
                data["errorCode"] = ERROR_CODE_BLOCK
                data["errorMsg"] = {
                    "detail": [errorMessage]
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")
            
            user.bonusesProgram = bonuses
            user.vipProgram = vip
            user.save()

            logger.info("Privacy setting for user: {}".format(str(user.username)))
            logger.info("Bonuses: {}, VIP: {}".format(bonuses, vip))

            return HttpResponse(('Successfully set the privacy setting'), status=200)

        except Exception as e:
            logger.error("Error getting privacy setting for a user", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


class GetBetHistory(View):

    def get(self, request, *args, **kwargs):
        try:
            user_name = request.GET['username']
            user = CustomUser.objects.get(username=user_name)
            if checkUserBlock(user):
                errorMessage = _('The current user is blocked!')
                data = {}
                data["errorCode"] = ERROR_CODE_BLOCK
                data["errorMsg"] = {
                    "detail": [errorMessage]
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")

            bet = GameRequestsModel.objects.filter(MemberID=user_name)
            #print(bet)
            response = {
                "bet": list(bet.values())
            }
            
            return HttpResponse(json.dumps(response), content_type='application/json',status=200)

        except Exception as e:
            logger.error("Error getting bet history for a user", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

class ActivityCheckSetting(View):


    def get(self, request, *args, **kwargs):

        try:
            userId= request.GET['userId']
            user = CustomUser.objects.get(pk=userId)
            if checkUserBlock(user):
                errorMessage = _('The current user is blocked!')
                data = {}
                data["errorCode"] = ERROR_CODE_BLOCK
                data["errorMsg"] = {
                    "detail": [errorMessage]
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")

            response = {
                "activityOpt": user.activity_check
            }

            return HttpResponse(json.dumps(response), content_type='application/json', status=200)
        
        except Exception as e:
            logger.error("Error getting privacy setting for a user", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):

        try:
            data = json.loads(request.body)
            userId = data['userId']
            activityOpt = data['activityOpt']

            user = CustomUser.objects.get(pk=userId)
            if checkUserBlock(user):
                data = {}
                errorMessage = _('The current user is blocked!')
                data["errorCode"] = ERROR_CODE_BLOCK
                data["errorMsg"] = {
                    "detail": [errorMessage]
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")

            user.activity_check = activityOpt
            user.save()
            logger.info("Activity check setting for user: {}, and time option is: {}".format(str(user.username), activityOpt))

            return HttpResponse(('Successfully set the activity check setting'), status=200)
        
        except Exception as e:
            logger.error("Error from setting privacy", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)



class CheckUserStatusAPI(View):

    def get(self, request, *args, **kwargs):

        try:
            userId = request.GET['userId']
            data = {
                "errorCode": CODE_SUCCESS,
                "errorMsg": _("Success")
            }
            user = CustomUser.objects.get(pk=userId)
            if checkUserBlock(user):
                errorMessage = _('The current user is blocked!')
                data["errorCode"] = ERROR_CODE_BLOCK
                data["errorMsg"] = {
                    "detail": [errorMessage]
                }
            return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type="application/json")
        
        except Exception as e:
            logger.error("Error from setting privacy", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


class AllSecurityQuestion(View):

    def get(self, request, *args, **kwargs):

        try:
            data = []
            for question in SECURITY_QUESTION:
                data.append({"value": question[0], "question": question[1]})

            logger.info("Sending all security question options response......... ")
            return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type='application/json')

        except:
            logger.error("Error getting all security question options: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    

class UserSecurityQuestion(View):

    def get(self, request, *args, **kwargs):
        
        try:
            userId = request.GET.get('userId')
            user = CustomUser.objects.get(pk=userId)

            if checkUserBlock(user):
                errorMessage = _('The current user is blocked!')
                data = {
                    "errorCode": ERROR_CODE_BLOCK,
                    "errorMsg": {
                        "detail": [errorMessage]
                    }
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type='application/json')
            
            if user.security_question:
                data = {
                    "value": user.security_question,
                    "question": str(dict(SECURITY_QUESTION).get(user.security_question))
                }
            else: 
                data = {
                    "errorCode": ERROR_CODE_EMPTY_RESULT,
                    "errorMessage": "You should set the security question"
                }

            return HttpResponse(json.dumps(data), content_type='application/json')

        except Exception as e:
            logger.error("Error getting security question for a user: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        

    def post(self, request, *args, **kwargs):

        try:
            data = json.loads(request.body)
            userId = data['userId']
            question = data['question']
            answer = data['answer']
            user = CustomUser.objects.get(pk=userId)

            if checkUserBlock(user):
                errorMessage = _('The current user is blocked!')
                data = {
                    "errorCode": ERROR_CODE_BLOCK,
                    "errorMsg": {
                        "detail": [errorMessage]
                    }
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type='application/json')

            user.security_question = question
            user.security_answer = answer
            user.save()

            response = {
                "code": CODE_SUCCESS,
                "message": "Successfully set the security Question"
            }
            return HttpResponse(json.dumps(response), content_type='application/json')

        except Exception as e:
            logger.error("Error setting security questions: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

class SetWithdrawPassword(View):

    def post(self, request, *args, **kwargs):
        
        try:
            data = json.loads(request.body)
            userId = data['userId'] 
            withdrawPassword = data['withdrawPassword']
            customUser = CustomUser.objects.get(pk=userId)
            print(customUser)
            if checkUserBlock(customUser):
                errorMessage = _('The current user is blocked!')
                data = {
                    "errorCode": ERROR_CODE_BLOCK,
                    "errorMsg": {
                        "detail": [errorMessage]
                    }
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type='application/json')

            if customUser.withdraw_password:
                response = {
                    "code": ERROR_CODE_INVALID_INFO,
                    "message": "You already setting the withdraw password"
                }
                logger.info("Already setting the withdraw password: {}".format(customUser.username))
                return HttpResponse(json.dumps(response), content_type='application/json', status = 200)

            customUser.withdraw_password = make_password(withdrawPassword)
            customUser.save()

            response = {
                "code": CODE_SUCCESS,
                "message": "Successfully set the withdraw password"
            }

            logger.info("Finished set the {} withdraw password.........".format(customUser.username))
            return HttpResponse(json.dumps(response), content_type='application/json', status = 200)

        except Exception as e:
            logger.error("Error setting withdraw password: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)



class ResetWithdrawPassword(View):

    def post(self, request, *args, **kwargs):

        response = {
            "code": 0,
            "message": ""
        }
        
        try:
            data = json.loads(request.body)
            userId = data['userId']
            oldWithdrawPassword = data['oldWithdrawPassword']
            newWithdrawPassword = data['newWithdrawPassword']
            customUser = CustomUser.objects.get(pk=userId)

            if checkUserBlock(customUser):
                errorMessage = _('The current user is blocked!')
                data = {
                    "errorCode": ERROR_CODE_BLOCK,
                    "errorMsg": {
                        "detail": [errorMessage]
                    }
                }
                return HttpResponse(json.dumps(data, cls=LazyEncoder), content_type='application/json')

            if customUser.withdraw_password and check_password(oldWithdrawPassword, customUser.withdraw_password):
                hashPassword = make_password(newWithdrawPassword)
                customUser.withdraw_password = hashPassword
                customUser.save()
            elif not check_password(oldWithdrawPassword, customUser.withdraw_password):
                response['code'] = ERROR_CODE_INVALID_INFO
                response['message'] = "The password you have entered does not match your current one."
                logger.info("The password you have entered does not match your current one: {}".format(customUser.username))
                return HttpResponse(json.dumps(response), content_type='application/json', status=200)
            else:
                response['code'] = ERROR_CODE_EMPTY_RESULT
                response['message'] = "You should set the password first"
                logger.info("You should set the withdraw password first: {}".format(customUser.username))
                return HttpResponse(json.dumps(response), content_type='application/json', status=200)
            
            response['code'] = CODE_SUCCESS
            response['message'] = "Successfully set the withdraw password"

            logger.info("Finished set the {} withdraw password.........".format(customUser.username))
            return HttpResponse(json.dumps(response), content_type='application/json', status=200)

        except Exception as e:
            logger.error("Error resetting withdraw password: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)