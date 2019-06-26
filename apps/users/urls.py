from django.urls import path
from . import views
# from users.forms import AuthenticationFormWithChekUsersStatus
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
    path('api/signup/', views.RegisterView.as_view(), name='api_register'),
    path('api/login/', views.LoginView.as_view(), name='api_login'),
    path('api/logout/', views.LogoutView.as_view(), name='api_logout'),
    path('api/sendemail/', views.SendEmail.as_view(), name='sendemail'),
    path('api/reset-password/verify-token/', views.CustomPasswordTokenVerificationView.as_view(), name='password_reset_verify_token'),
    path('api/reset-password/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('api/language/', views.LanguageView.as_view(), name='language'),
    path('api/notice-message', views.NoticeMessageView.as_view(), name='notice_message'),
    path('api/referral/', views.ReferralAward.as_view(), name='referral'),
    path('api/checkreferral/', views.CheckReferral.as_view(), name='checkreferral'),
    path('api/referraltree/', views.ReferralTree.as_view(), name='referraltree'),
    path('api/config/', views.Global.as_view(), name='config'),
    path('api/addorwithdrawbalance/', csrf_exempt(views.AddOrWithdrawBalance.as_view()), name='add_withdraw_balance'),
    path('api/activate/', csrf_exempt(views.Activation.as_view()), name='activate'),
    path('api/activate-verify/', csrf_exempt(views.ActivationVerify.as_view()), name='activate_verify'),
    path('api/facebooksignup/', views.FacebookRegister.as_view(), name='facebook_signup'),
    path('api/facebooklogin/', csrf_exempt(views.FacebookLoginView.as_view()), name='facebook_login'),
    path('api/oneclicksignup/', views.OneclickRegister.as_view(), name='one_click'),
    path('api/updateemail/', csrf_exempt(views.UpdateEmail.as_view()), name='update_email'),
    path('api/checkemailexist/', views.CheckEmailExixted.as_view(), name='email_exist'),
    path('api/generatepasswordcode/', csrf_exempt(views.GenerateForgetPasswordCode.as_view()), name='generate_code'),
    path('api/sendresetpasswordcode/', csrf_exempt(views.SendResetPasswordCode.as_view()), name='send_code'),
    path('api/verifyresetpasswordcode/', csrf_exempt(views.VerifyResetPasswordCode.as_view()), name='verify_resetpassword_code'),
    path('api/changeandresetpassword/', csrf_exempt(views.ChangeAndResetPassword.as_view()),name='change_reset_password'),
    path('api/changepassword/', views.ChangePassword.as_view(), name='change_password'),
    path('api/checkusernameexist/', views.CheckUsernameExist.as_view(), name='check_username_exist'),
    path('api/userSearch/', views.UserSearchAutocomplete.as_view(), name='user_autocomplete_search'),
    path('api/generateactivationcode/', views.GenerateActivationCode.as_view(), name='generate_activation_code'),
    path('api/verifyactivationcode/', views.VerifyActivationCode.as_view(), name='verify_activation_code'),
    path('api/validateandresetpassword/', views.ValidateAndResetPassowrd.as_view(), name='validate_and_reset_password')
]
