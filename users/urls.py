from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
]


urlpatterns += [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),

    path('game/<int:pk>', views.GameDetailView.as_view(), name='game-detail'),

    path('games/', views.GameListView.as_view(), name='games'),
    path('all_search_list_view/', views.AllSearchListView.as_view(), name='all_search_list_view'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('profile', views.profile, name='profile'),
]


urlpatterns += [
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    #path('myprofile/', views.ProfileByUserListView.as_view(), name='my-profile'),
    path(r'borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'), #Added for challenge
]

# Add URLConf for librarian to renew a book.
urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]


# Add URLConf to create, update, and delete authors
urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author_create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author_update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author_delete'),
]

# Add URLConf to create, update, and delete books
urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book_create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book_update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book_delete'),
]


# Added by Stephen

from users.forms import AuthenticationFormWithChekUsersStatus
from django.urls import include

urlpatterns += [
    path('api/games/', views.GameAPIListView.as_view(), name='api_games'),
    path('api/books/', views.BookAPIListView.as_view(), name='api_books'),
    path('api/authors/', views.AuthorAPIListView.as_view(), name='api_authors'),
    path('api/bookinstance/', views.BookInstanceAPIListView.as_view(), name='api_bookinstance'),
    path('api/user/', views.UserDetailsView.as_view(), name='rest_user_details'),
    path('api/signup/', views.RegisterView.as_view(), name='rest_register'),
    path('api/login/', views.LoginView.as_view(), name='api_login'),
    path('api/sendemail/', views.SendEmail.as_view(), name='sendemail'),
    path('api/reset-password/verify-token/', views.CustomPasswordTokenVerificationView.as_view(), name='password_reset_verify_token'),
    path('api/reset-password/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('api/language/', views.LanguageView.as_view(), name='language'),
]
