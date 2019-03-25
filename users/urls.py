from django.urls import path
from . import views
from users.forms import AuthenticationFormWithChekUsersStatus
from django.urls import include
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
]

urlpatterns += [
    path('', views.index, name='index'),
    path('game/<int:pk>', views.GameDetailView.as_view(), name='game-detail'),
    path('games/', views.GameListView.as_view(), name='games'),
    path('all_search_list_view/', views.AllSearchListView.as_view(), name='all_search_list_view'),
    path('profile', views.profile, name='profile'),
]

urlpatterns += [
    path('api/games/', views.GameAPIListView.as_view(), name='api_games'),
    path('api/games-detail/', views.GameDetailAPIListView.as_view(), name='games_detail'),
    path('api/user/', views.UserDetailsView.as_view(), name='rest_user_details'),
    path('api/signup/', views.RegisterView.as_view(), name='rest_register'),
    path('api/login/', views.LoginView.as_view(), name='api_login'),
    path('api/sendemail/', views.SendEmail.as_view(), name='sendemail'),
    path('api/reset-password/verify-token/', views.CustomPasswordTokenVerificationView.as_view(), name='password_reset_verify_token'),
    path('api/reset-password/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('api/language/', views.LanguageView.as_view(), name='language'),
    path('api/notice-message', views.NoticeMessageView.as_view(), name='notice_message'),
    path('api/referral/', views.ReferralAward.as_view(), name='referral'),
    path('api/checkreferral/', views.CheckReferral.as_view(), name='checkreferral'),
    path('api/referraltree/', views.ReferralTree.as_view(), name='referraltree'),
    path('api/config/', views.Global.as_view(), name='config'),
    path('api/addbalance/', csrf_exempt(views.AddBalance.as_view()), name='add_balance')
]
