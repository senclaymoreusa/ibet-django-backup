from django.urls import path, include
from rest_framework import routers
from . import views



urlpatterns = [
    path('api/qaicash/deposit_method', views.getDepositMethod.as_view(), name = 'deposit_method'),
    path('api/qaicash/get_bank_list', views.getBankList.as_view(), name = 'get_bank_list'),
    path('api/qaicash/get_bank_limits', views.getBankLimits.as_view(), name = 'get_bank_limits'),
    path('api/qaicash/submit_deposit', views.submitDeposit.as_view(), name = 'submit_Deposit'),
    path('api/qaicash/submit_payout', views.submitPayout.as_view(), name = 'submit_Payout'),
    path('api/qaicash/payout_transaction', views.getPayoutTransaction.as_view(), name = 'payout_Transaction'),
    path('api/qaicash/approve_payout', views.approvePayout.as_view(), name = 'approve_Payout'),
    path('api/qaicash/reject_payout', views.rejectPayout.as_view(), name = 'reject_Payout'),
    path('api/qaicash/deposit_transaction', views.getDepositTransaction.as_view(), name = 'deposit_Transaction'),
    path('api/qaicash/transaction_status', views.transactionStatusUpdate.as_view(), name = 'transaction_status_update'),
    path('api/qaicash/payout_method', views.payoutMethod.as_view(), name = 'payout_Method'),
    path('api/qaicash/payout_bank_list', views.getPayoutBankList.as_view(), name = 'payout_Banklist'),
    path('api/qaicash/payout_bank_limits', views.getPayoutBankLimits.as_view(), name = 'payout_Banklimits'),
    path('api/paypal/create_payment', views.paypalCreatePayment.as_view(), name = 'paypal_Create_Payment'),
    path('api/paypal/get_order', views.paypalGetOrder.as_view(), name = 'paypal_Get_Order'),
    path('api/paypal/execute_payment', views.paypalExecutePayment.as_view(), name = 'paypal_Execute_Payment'),
    path('api/linepay/reserve_payment', views.reservePayment, name = "LINEpay_reserve_payment"),
    path('api/astro_new_invoice', views.astroNewInvoice, name = 'AstroPay_new_invoice'),
    path('api/astro_payment_status', views.astroPaymentStatus, name = 'AstroPay_Payment_Status'),
]