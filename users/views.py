from django.shortcuts import render

# Added by Stephen
import logging
logger = logging.getLogger(__name__)
##################

# Create your views here.

from .models import Book, Author, BookInstance, Genre, Game, CustomUser
from django.urls import reverse_lazy
from django.views import generic

from .forms import CustomUserCreationForm

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

from django.views import generic



class GameListView(generic.ListView):
    """
    Generic class-based view for a list of games.
    """
    model = Game
    paginate_by = 10

class GameDetailView(generic.DetailView):
    """
    Generic class-based detail view for a game.
    """
    model = Game


class BookListView(generic.ListView):
    """
    Generic class-based view for a list of books.
    """
    model = Book
    paginate_by = 10
    
class BookDetailView(generic.DetailView):
    """
    Generic class-based detail view for a book.
    """
    model = Book

class AuthorListView(generic.ListView):
    """
    Generic class-based list view for a list of authors.
    """
    model = Author
    paginate_by = 10 


class AuthorDetailView(generic.DetailView):
    """
    Generic class-based detail view for an author.
    """
    model = Author

class PlayerDetailView(generic.DetailView):

    
    model = CustomUser


from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user. 
    """
    model = BookInstance
    template_name ='users/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


# Added as part of challenge!
from django.contrib.auth.mixins import PermissionRequiredMixin

class LoanedBooksAllListView(PermissionRequiredMixin,generic.ListView):
    """
    Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission.
    """
    model = BookInstance
    permission_required = 'users.can_mark_returned'
    template_name ='users/bookinstance_list_borrowed_all.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')  


from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import permission_required

from .forms import RenewBookForm

@permission_required('users.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'users/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})
    
    
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}
    permission_required = 'users.can_mark_returned'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']
    permission_required = 'users.can_mark_returned'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'users.can_mark_returned'
    

#Classes created for the forms challenge
class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'users.can_mark_returned'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'users.can_mark_returned'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'users.can_mark_returned'



class AllSearchListView(generic.ListView):
    model = Game
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query == None:
            return Game.objects.none()
        return Game.objects.filter(name__contains=self.request.GET.get('q'))



#  Added by Stephen
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView
)

from .serializers import GameSerializer, BookSerializer, AuthorSerializer, CategorySerializer, BookInstanceSerializer, UserDetailsSerializer, RegisterSerializer
from .models import Category

class GameAPIListView(ListAPIView):
    serializer_class = GameSerializer
    def get_queryset(self):
        term = self.request.GET['term']
        data = Game.objects.filter(category_id__parent_id__name__icontains=term)
        if not data:
            data = Game.objects.filter(category_id__name__icontains=term)
            if not data:
                data = Game.objects.filter(name__icontains=term)
                if not data:
                    logger.error('Search term is not valid')
                return data
            return data
        return data

class BookAPIListView(ListAPIView):
    serializer_class = BookSerializer
    queryset = Book.objects.all()

class AuthorAPIListView(ListAPIView):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()

class CategoryAPIListView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

class BookInstanceAPIListView(ListAPIView):
    serializer_class = BookInstanceSerializer
    queryset = BookInstance.objects.all()

from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

class UserDetailsView(RetrieveUpdateAPIView):

    serializer_class = UserDetailsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return get_user_model().objects.none()


from rest_auth.models import TokenModel
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters('password1', 'password2'))
from rest_auth.app_settings import (TokenSerializer, JWTSerializer, create_token)
from django.conf import settings
from allauth.account.utils import complete_signup
from allauth.account import app_settings as allauth_settings
from rest_framework.response import Response
from rest_framework import status

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


from django.contrib.auth.forms import AuthenticationForm
from .serializers import LoginSerializer
from django.conf import settings
from django.contrib.auth import (
    login as django_login,
    logout as django_logout
)
from django.http import HttpResponse
from rest_framework.exceptions import APIException
from django.utils.translation import ugettext_lazy as _



class BlockedUserException(APIException):
    status_code = 403
    default_detail = _('Current user is blocked!')
    default_code = 'block'

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
        self.user = self.serializer.validated_data['user']
        if self.user.block is True:
            # print("user block")
            raise BlockedUserException
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
        
import sendgrid
import os
from sendgrid.helpers.mail import *
from django.conf import settings
from django.views import View
from django.http import HttpResponse

class SendEmail(View):
    def get(self, request, *args, **kwargs):
        from_email_address = self.request.GET['from_email_address']
        to_email_address = self.request.GET['to_email_address']
        email_subject = self.request.GET['email_subject']
        email_content = self.request.GET['email_content']

        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        from_email = Email(from_email_address)
        to_email = Email(to_email_address)
        subject = email_subject
        content = Content("text/plain", email_content)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)

        return HttpResponse('Email has been sent!')


from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.response import Response
from .serializers import CustomTokenSerializer
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.views import get_password_reset_token_expiry_time
from django.utils import timezone
from datetime import timedelta


class CustomPasswordResetView:
    @receiver(reset_password_token_created)
    def password_reset_token_created(sender, reset_password_token, *args, **kwargs):
        
        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        from_email = Email('claymore@claymoreusa.com')
        to_email = Email(reset_password_token.user.email)
        subject = 'Hi ' + reset_password_token.user.username + ', You have requested to reset your password'
        content = Content("text/plain", 'Click the link to reset your email password: ' + "{}reset_password/{}".format('http://localhost:3000/', reset_password_token.key))
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

        # print(request.session.keys())
        print('post: ' + languageCode)

        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        if session_key is None:
            request.session.create()
            print('saved session key ' + request.session._session_key)
            # response.set_cookie(key=settings.SESSION_COOKIE_NAME, value=request.session._session_key, domain='.app.localhost')
            response.set_cookie(key=settings.SESSION_COOKIE_NAME, value=request.session._session_key)
            pass
        else:
            print('existed session key ' + session_key)
            pass
        # print('session key: ' + session_key)

        # Check that the test cookie worked (we set it below):
        if request.session.test_cookie_worked():

            # The test cookie worked, so delete it.
            request.session.delete_test_cookie()

            # In practice, we'd need some logic to check username/password
            # here, but since this is an example...
            print("You're logged in.")
        request.session.set_test_cookie()
        
        return response

    def get(self, request, *args, **kwargs):
        languageCode = 'en'
        if LANGUAGE_SESSION_KEY in request.session:
            languageCode = request.session[LANGUAGE_SESSION_KEY]
        
        # print(request.session.keys())
        print('get: ' + languageCode)

        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, 'nothing')
        print('session key: ' + session_key)

        return Response({'languageCode': languageCode}, status = status.HTTP_200_OK)

        