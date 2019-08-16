
from . import views
from django.urls import path

urlpatterns = [
    # path('api/games/', views.GameAPIListView.as_view(), name='api_games'),
    # path('api/games-detail/', views.GameDetailAPIListView.as_view(), name='games_detail'),
    # path('api/user/', views.UserDetailsView.as_view(), name='rest_user_details'),
    # path('api/signup/', views.RegisterView.as_view(), name='api_register'),
    # path('api/login/', views.LoginView.as_view(), name='api_login'),
    # path('api/sendemail/', views.SendEmail.as_view(), name='sendemail'),
    # path('api/reset-password/verify-token/', views.CustomPasswordTokenVerificationView.as_view(), name='password_reset_verify_token'),
    # path('api/reset-password/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    # path('api/language/', views.LanguageView.as_view(), name='language'),
    path('api/notification', views.NotificationAPIView.as_view(), name='notification'),
    path('api/notification-log', views.NotificationLogView.as_view(), name='notification-log'),
    path('api/notification-users', views.NotificationToUsersView.as_view(), name='notification-users'),
    path('api/create-topic', views.AWSTopicView.as_view(), name='create-topic'),
    path('api/create-message', views.CreateNotificationAPIView.as_view(), name='create-message'),
    # path('api/referral/', views.ReferralAward.as_view(), name='referral'),
    # path('api/checkreferral/', views.CheckReferral.as_view(), name='checkreferral'),
    # path('api/referraltree/', views.ReferralTree.as_view(), name='referraltree'),
    # path('api/config/', views.Global.as_view(), name='config'),
    # path('api/addbalance/', csrf_exempt(views.AddBalance.as_view()), name='add_balance'),
    # path('api/activate/', csrf_exempt(views.Activation.as_view()), name='activate'),
    # path('api/activate-verify/', csrf_exempt(views.ActivationVerify.as_view()), name='activate_verify')
]