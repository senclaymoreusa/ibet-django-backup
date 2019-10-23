from django.urls import path, include
from rest_framework import routers
import games.views.eagameviews as eagameviews
import games.views.fggameviews as fggameviews
from django.views.decorators.csrf import csrf_exempt
from games.views.views import *

urlpatterns = [
    path('api/games/', GamesSearchView.as_view(), name = 'games_search'),
    path('api/providers/', ProvidersSearchView.as_view(), name = 'provider_search'),
    path('api/filter/', FilterAPI.as_view(), name='get_filter'),
    path('api/login-ea/', csrf_exempt(eagameviews.EALiveCasinoClientLoginView.as_view()), name="ea_login"),
    path('api/single-login-ea/', csrf_exempt(eagameviews.EASingleLoginValidation.as_view()), name="ea_single_login"),
    path('api/testview/', csrf_exempt(eagameviews.TestView.as_view()), name="test_View"),
    path('api/auto-cashier-login/', csrf_exempt(eagameviews.AutoCashierLoginEA.as_view()), name="auto_cashier_login"),

    path('api/fg/login', fggameviews.FGLogin.as_view(), name = 'fg_login'),
    path('api/fg/sessionCheck', fggameviews.SessionCheck.as_view(), name = 'fg_session_check'),
    path('api/fg/gamelaunch', fggameviews.GameLaunch.as_view(), name = 'game_launch'),
    path('omegassw/getAccountDetails', fggameviews.GetAccountDetail.as_view(), name ='account_detail'),
    path('omegassw/getBalance', fggameviews.GetBalance.as_view(), name = 'get_balance'),
    path('omegassw/processTransaction', fggameviews.ProcessTransaction.as_view(), name = 'process_transaction')


]
