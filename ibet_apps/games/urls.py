from django.urls import path, include
from rest_framework import routers
import games.views.eagameviews as eagameviews
from django.views.decorators.csrf import csrf_exempt
from games.views.views import *
import games.views.gdcasinoviews as gdcasino

urlpatterns = [
    path('api/games/', GamesSearchView.as_view(), name = 'games_search'),
    path('api/providers/', ProvidersSearchView.as_view(), name = 'provider_search'),
    path('api/filter/', FilterAPI.as_view(), name='get_filter'),
    path('api/login-ea/', csrf_exempt(eagameviews.EALiveCasinoClientLoginView.as_view()), name="ea_login"),
    path('api/single-login-ea/', csrf_exempt(eagameviews.EASingleLoginValidation.as_view()), name="ea_single_login"),
    path('api/testview/', csrf_exempt(eagameviews.TestView.as_view()), name="test_View"),
    path('api/auto-cashier-login/', csrf_exempt(eagameviews.AutoCashierLoginEA.as_view()), name="auto_cashier_login"),
    path('api/gd/', gdcasino.my_soap_application, name = 'my_soap_application'),
    path('api/gd/login', gdcasino.LoginView.as_view(), name = 'GDCasino_Login'),
    path('api/gd/create_member', gdcasino.CreateMember.as_view(), name = 'GDCasino_Create_Member'),
    path('api/gd/logout_player', gdcasino.LogoutPlayer.as_view(), name = 'GDCasino_Logout_Player'),
    path('api/gd/withdraw', gdcasino.Withdrawal.as_view(), name = 'GDCasino_Withdrawal'),
    path('api/gd/deposit', gdcasino.Deposit.as_view(), name = 'GDCasino_Deposit'),
    path('api/gd/check_client', gdcasino.CheckClient.as_view(), name = 'GDCasino_Check_Client'),
    path('api/gd/get_bet_history', gdcasino.GetBetHistory.as_view(), name = 'GDCasino_Get_Bet_History'),
    path('api/gd/get_member_balance', gdcasino.GetMemberBalance.as_view(), name = 'GDCasino_Get_Member_Balance'),
    path('api/gd/check_transaction_status', gdcasino.checkTransactionStatus.as_view(), name = 'GDCasino_check_Transaction_Status'),
    
    
    
]
