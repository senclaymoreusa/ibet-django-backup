from django.urls import path, include
from rest_framework import routers
import games.views.eagameviews as eagameviews
import games.views.inplaygameviews as inplayviews
import games.views.betsoftviews as betsoftviews
import games.views.kygameviews as kygameviews
import games.views.playngogameviews as playngogameviews
import games.views.allbetgameviews as allbetgameviews
import games.views.fggameviews as fggameviews
import games.views.mggameviews as mggameviews
from django.views.decorators.csrf import csrf_exempt
from games.views.views import *
import games.views.gdcasinoviews as gdcasino
import games.views.betsviews as bets
from games.live_casino import *
import games.views.onebookviews as onebookviews
import games.views.sagameviews as sagameviews
import games.views.gbsportsviews as gbsports
import games.views.qtgameviews as qtgameviews

urlpatterns = [
    path('api/games/', GamesSearchView.as_view(), name = 'games_search'),
    path('api/games-detail/', GameDetailAPIListView.as_view(), name='games_detail'),
    # path('api/live-casino/', getLiveCasinoGames, name = 'live_casino_games'),
    path('api/providers/', ProvidersSearchView.as_view(), name = 'provider_search'),
    path('api/filter/', FilterAPI.as_view(), name='get_filter'),
    path('api/login-ea/', csrf_exempt(eagameviews.EALiveCasinoClientLoginView.as_view()), name="ea_login"),
    path('api/single-login-ea/', csrf_exempt(eagameviews.EASingleLoginValidation.as_view()), name="ea_single_login"),
    # path('api/testview/', csrf_exempt(eagameviews.TestView.as_view()), name="test_View"),
    path('api/auto-cashier-login/', csrf_exempt(eagameviews.AutoCashierLoginEA.as_view()), name="auto_cashier_login"),

    path('api/bets/getall', csrf_exempt(bets.getBetHistory), name="get_bet_history"),

    # Inplay Matrix
    path('api/inplay/login', csrf_exempt(inplayviews.InplayLoginAPI.as_view()), name="inplay_login"),
    path('api/inplay/GetBalance/', inplayviews.InplayGetBalanceAPI.as_view(), name="inplay_get_balance"),
    path('api/inplay/GetApproval/', inplayviews.InplayGetApprovalAPI.as_view(), name="inplay_get_approval"),
    path('api/inplay/DeductBalance/', inplayviews.InplayDeductBalanceAPI.as_view(), name="inplay-deduct-balance"),
    path('api/inplay/test-decryption/', inplayviews.TestDecryption.as_view(), name="inplay_test_decryption"),

    #ea live casino
    path('api/ea/login/', csrf_exempt(eagameviews.EALiveCasinoClientLoginView.as_view()), name="ea_login"),
    path('api/ea/single-login/', csrf_exempt(eagameviews.EASingleLoginValidation.as_view()), name="ea_single_login"),
    path('api/ea/deposit/', csrf_exempt(eagameviews.DepositEAView.as_view()), name="ea_deposit"),
    path('api/ea/withdraw/', csrf_exempt(eagameviews.WithdrawEAView.as_view()), name="ea_withdraw"),
    path('api/ea/get-balance/', csrf_exempt(eagameviews.GetEABalance.as_view()),name="ea_get_balance"),
    path('api/ea/auto-cashier-login/', csrf_exempt(eagameviews.AutoCashierLoginEA.as_view()), name="ea_auto_cashier_login"),
    
    #gd casino
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

    # Play n Go
    path('api/playngo/login/', csrf_exempt(playngogameviews.AuthenticateView.as_view()), name="png_auth"),
    path('api/playngo/balance/', csrf_exempt(playngogameviews.BalanceView.as_view()), name="png_bal"),
    path('api/playngo/reserve/', csrf_exempt(playngogameviews.ReserveView.as_view()), name="png_res"),

    # AllBet
    path('api/allbet/encryption', csrf_exempt(allbetgameviews.EncryptionView.as_view()), name='allbet_encrypt'),
    path('api/allbet/get_balance/<str:player_account_name>', csrf_exempt(allbetgameviews.BalanceView.as_view()), name='allbet_balance'),

    # fg
    path('api/get_all_game', fggameviews.GetAllGame.as_view(), name = 'get_all_game'),
    path('api/fg/login', fggameviews.FGLogin.as_view(), name = 'fg_login'),
    path('api/fg/getSessionKey', fggameviews.GetSessionKey.as_view(), name = 'fg_get_sessionkey' ),
    path('api/fg/gamelaunch', fggameviews.GameLaunch.as_view(), name = 'game_launch'),
    path('omegassw/getAccountDetails', fggameviews.GetAccountDetail.as_view(), name ='account_detail'),
    path('omegassw/getBalance', fggameviews.GetBalance.as_view(), name = 'get_balance'),
    path('omegassw/processTransaction', fggameviews.ProcessTransaction.as_view(), name = 'process_transaction'),
    

    #mg game
    path('api/mg/', mggameviews.MGgame.as_view(), name = 'mg_game'),
    path('api/mg/token_save', mggameviews.MGtoken.as_view(), name = 'mg_token'),


    # kaiyuan gaming
    path('api/ky/games/', csrf_exempt(kygameviews.KaiyuanAPI.as_view()), name="ky_games"),
    path('api/ky/test/', csrf_exempt(kygameviews.TestTransferAPI.as_view()), name="ky_test"),
    path('api/ky/record/', csrf_exempt(kygameviews.TestGetRecord.as_view()), name="ky_record"),

    #onebook
    path('api/onebook/create_member', onebookviews.CreateMember.as_view(), name="create_member"),
    path('api/onebook/fund_transfer', onebookviews.FundTransfer.as_view(), name="fund_transfer"),
    path('api/onebook/login', onebookviews.Login.as_view(), name="Login"),
    path('api/onebook/check_member_online', csrf_exempt(onebookviews.CheckMemberOnline), name="Check_Member_Online"),
    path('api/onebook/get_bet_detail', onebookviews.GetBetDetail, name="Get_Bet_Detail"),
    # path('api/onebook/test', onebookviews.test.as_view(), name="onebook_test"),
    

    #betsoft
    path('api/betsoft/authenticate', betsoftviews.BetSoftAuthenticate.as_view(), name="betsoft_authenticate"),
    path('api/betsoft/result', betsoftviews.BetSoftBetResult.as_view(), name="betsoft_bet_result"),
    path('api/betsoft/refundBet', betsoftviews.BetSoftBetRefund.as_view(), name="betsoft_refund"),
    path('api/betsoft/account', betsoftviews.BetSoftGetInfo.as_view(), name="betsoft_get_info"),
    path('api/betsoft/lunch', betsoftviews.BetsoftGameLaunch.as_view(), name="betsoft_lunch"),
    # path('api/betsoft/bonusRelease', betsoftviews.BonusRelease.as_view(), name="betsoft_bonus_release"),
    # path('api/betsoft/bonusWin', betsoftviews.BonusWin.as_view(), name="betsoft_bonus_win"),

    #sa
    path('api/sa/reg_user_info', sagameviews.RegUserInfo.as_view(), name="sa_register_user"),
    path('api/sa/login_request', sagameviews.LoginRequest.as_view(), name="sa_login_request"),

    #gb
    path('api/gb/walletgeneral/', gbsports.WalletGeneralAPI.as_view(), name='wallet_general'),
    path('api/gb/walletbet/', gbsports.WalletBetAPIURL.as_view(), name='wallet_bet'),
    path('api/gb/walletsettle/', gbsports.WalletSettleAPIURL.as_view(), name='wallet_settle'),
    path('api/gb/generategameurl/', gbsports.GenerateGameURL.as_view(), name='generate_game_url'),
    path('api/gb/generatefakeusergameurl/', gbsports.GenerateFakeUserGameURL.as_view(), name='generate_fake_user_game_url'),

    # path('api/onebook/test/<username>', onebookviews.test01,name="test"),
    # QT
    path('accounts/<str:playerId>/session', qtgameviews.VerifySession.as_view(), name="verify_session"),
    path('accounts/<str:playerId>/balance', qtgameviews.GetBalance.as_view(), name="get_balance"),
    path('api/qt/game_launch', qtgameviews.GameLaunch.as_view(), name="qt_game_launch"),

]

#onebookviews.getBetDetail(repeat=300,repeat_until=None)
