from django.urls import path
from . import views

import users.views.agintegrationviews as agintegrationviews
import users.views.yggdrasilintegrationviews as yggdrasilintegrationviews
import users.views.saintegrationviews as saintegrationviews
import users.views.iovation as iovationviews


# from users.forms import AuthenticationFormWithChekUsersStatus
from django.urls import include
from django.views.decorators.csrf import csrf_exempt
import users.views.transferview as transferview
import users.views.paymentsetting as paymentsettingview
import users.views.vipview as vipview
from users.views.adminview import *


urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
]

urlpatterns += [
    path('', views.index, name='index'),
    path('game/<int:pk>', views.GameDetailView.as_view(), name='game-detail'),
    path('games/', views.GameListView.as_view(), name='games'),
    path('all_search_list_view/', views.AllSearchListView.as_view(), name='all_search_list_view'),
    path('profile', views.profile, name='profile'),
    path('export_vip', vipview.exportVIP, name='export_vip'),
]

urlpatterns += [
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
    path('api/addorwithdrawbalance/', views.AddOrWithdrawBalance.as_view(), name='add_withdraw_balance'),
    path('api/activate/', views.Activation.as_view(), name='activate'),
    path('api/activate-verify/', views.ActivationVerify.as_view(), name='activate_verify'),
    path('api/facebooksignup/', views.FacebookRegister.as_view(), name='facebook_signup'),
    path('api/facebooklogin/', csrf_exempt(views.FacebookLoginView.as_view()), name='facebook_login'),
    path('api/oneclicksignup/', views.OneclickRegister.as_view(), name='one_click'),
    path('api/updateemail/', views.UpdateEmail.as_view(), name='update_email'),
    path('api/checkemailexist/', views.CheckEmailExixted.as_view(), name='email_exist'),
    path('api/generatepasswordcode/', views.GenerateForgetPasswordCode.as_view(), name='generate_code'),
    path('api/retrievepasswordmethod/', views.CheckRetrievePasswordMethod.as_view(), name='retrieve_password_method'),
    path('api/sendresetpasswordcode/', views.SendResetPasswordCode.as_view(), name='send_code'),
    path('api/verifyresetpasswordcode/', views.VerifyResetPasswordCode.as_view(), name='verify_resetpassword_code'),
    path('api/changeandresetpassword/', views.ChangeAndResetPassword.as_view(),name='change_reset_password'),
    path('api/changepassword/', views.ChangePassword.as_view(), name='change_password'),
    path('api/checkusernameexist/', views.CheckUsernameExist.as_view(), name='check_username_exist'),
    path('api/userSearch/', views.UserSearchAutocomplete.as_view(), name='user_autocomplete_search'),
    path('api/generateactivationcode/', views.GenerateActivationCode.as_view(), name='generate_activation_code'),
    path('api/verifyactivationcode/', views.VerifyActivationCode.as_view(), name='verify_activation_code'),
    path('api/validateandresetpassword/', views.ValidateAndResetPassowrd.as_view(), name='validate_and_reset_password'),
    path('api/cancelregistration/', views.CancelRegistration.as_view(), name='cancel_registration'),
    path('api/getusernamebyreferid/', views.GetUsernameByReferid.as_view(), name = 'get_user'),
    path('api/posttransferforag/', agintegrationviews.PostTransferforAG.as_view(), name='post_transfer_for_ag'),
    path('api/Yggdrasil/',yggdrasilintegrationviews.YggdrasilAPI.as_view(), name='Yggdrasil_api'),
    path('api/sagetbalance/', saintegrationviews.SAGetUserBalance.as_view(), name='sa_get_balance'),
    path('api/saplacebet/', saintegrationviews.SAPlaceBet.as_view(), name='sa_place_bet'),
    path('api/saplayerwin/', saintegrationviews.SAPlayerWin.as_view(), name='sa_player_win'),
    path('api/saplayerlost/', saintegrationviews.SAPlayerLost.as_view(), name='sa_player_lost'),
    path('api/saplayerbetcancel/', saintegrationviews.SAPlaceBetCancel.as_view(), name='sa_player_bet_cancel'),
    path('api/set-limitations/',csrf_exempt(views.SetLimitation.as_view()), name='set_limitation'),
    path('api/delete-limitation/', csrf_exempt(views.DeleteLimitation.as_view()), name='delete_limitation'),
    path('api/get-limitations/', csrf_exempt(views.GetLimitation.as_view()), name='get_limitation'),
    path('api/set-block-time/', csrf_exempt(views.SetBlockTime.as_view()), name='set_block_time'),
    path('api/cancel-delete-limitation/', csrf_exempt(views.CancelDeleteLimitation.as_view()), name='cancel-delete-limitation'),
    path('api/marketing-settings/', csrf_exempt(views.MarketingSettings.as_view()), name="market_settings"),
    path('api/privacy-settings/', csrf_exempt(views.PrivacySettings.as_view()), name="privacy_settings"),
    path('api/bet-history/',views.GetBetHistory.as_view(), name="get_bet_history"),
    path('api/activity-check/', csrf_exempt(views.ActivityCheckSetting.as_view()), name="activity_check"),
    path('api/check-user-status/', views.CheckUserStatusAPI.as_view(), name="check_user_status"),
    path('api/security-question/', views.AllSecurityQuestion.as_view(), name="security_question"),
    path('api/user-security-question/', csrf_exempt(views.UserSecurityQuestion.as_view()), name="user_security_question"),
    path('api/setting-withdraw-password/', csrf_exempt(views.SetWithdrawPassword.as_view()), name="withdraw_password"),
    path('api/reset-withdraw-password/', csrf_exempt(views.ResetWithdrawPassword.as_view()), name="reset_withdraw_password"),
    path('api/check-withdraw-password/', csrf_exempt(views.checkWithdrawPassword), name="check_withdraw_password"),
    path('api/transfer/', csrf_exempt(transferview.Transfer.as_view()), name="transfer_view"),
    path('api/favorite-payment-setting/', csrf_exempt(paymentsettingview.PaymentSetting.as_view()), name="favorite_deposit_setting"),

    path('api/login-device-info', iovationviews.LoginDeviceInfo.as_view(), name="login_device_info"),

    path('api/get-each-wallet-amount/', transferview.EachWalletAmount.as_view(), name="get_each_wallet_amount"),
    path('api/get-product-contribution/', ProductContribution.as_view(), name="product_contribution"),

    # admin API
    path('api/admin/get-user-info', GetUserInfo.as_view(), name='get_user_info'),
    path('api/admin/get-user-transctions', GetUserTransaction.as_view(), name="get_user_transactions"),
    path('api/admin/get-bet-history-detail', GetBetHistoryDetail.as_view(), name="get_bet_history_info"),
    path('api/admin/user-adjustment', UserAdjustment.as_view(), name="user_adjustment"),
    path('api/admin/user-transfer', UserTransfer.as_view(), name="user_transfer"),
    path('api/admin/blacklist-user', BlackListUser.as_view(), name="blacklist_user"),
    path('api/admin/send-sms', SendSMS.as_view(), name="admin_send_sms"),
    path('api/admin/export-user', ExportUserList.as_view(), name="export_user")
]
