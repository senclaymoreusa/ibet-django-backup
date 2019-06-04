from django.urls import path, include
from . import views

urlpatterns = [
    path('api/deposit_method', views.getDepositMethod.as_view(), name = 'deposit_method'),
    path('api/get_BankList', views.getBankList.as_view(), name = 'get_BankList'),
    path('api/get_banklimits', views.getBankLimits.as_view(), name = 'get_BankLimits'),
    path('api/submit_deposit', views.submitDeposit.as_view(), name = 'submit_Deposit'),
    path('api/submit_payout', views.submitPayout.as_view(), name = 'submit_Payout'),
    path('api/payout_transaction', views.getPayoutTransaction.as_view(), name = 'payout_Transaction'),
    path('api/approve_payout', views.approvePayout.as_view(), name = 'approve_Payout'),
    path('api/reject_payout', views.rejectPayout.as_view(), name = 'reject_Payout'),
    path('api/deposit_transaction', views.getDepositTransaction.as_view(), name = 'deposit_Transaction'),
    path('api/transaction_status', views.transactionStatusUpdate.as_view(), name = 'transaction_status_update'),
    path('api/payout_method', views.payoutMethod.as_view(), name = 'payout_Method'),
    path('api/payout_banklist', views.getPayoutBankList.as_view(), name = 'payout_Banklist'),
    path('api/payout_banklimits', views.getPayoutBankLimits.as_view(), name = 'payout_Banklimits'),
    path('api/paypal_create_payment', views.paypalCreatePayment.as_view(), name = 'paypal_Create_Payment'),
    path('api/paypal_get_order', views.paypalGetOrder.as_view(), name = 'paypal_Get_Order'),
]