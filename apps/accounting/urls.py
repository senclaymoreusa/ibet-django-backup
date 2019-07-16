from django.urls import path, include
from django.conf.urls import url
from rest_framework import routers

import accounting.views.qaicashviews as qaicash
import accounting.views.paypalviews as paypal
import accounting.views.linepayviews as linepay
import accounting.views.astropayviews as astropay
import accounting.views.asiapayviews as asiapay
import accounting.views.deposit_views as deposit

urlpatterns = [
    path('api/qaicash/deposit_method', qaicash.getDepositMethod.as_view(), name = 'deposit_method'),
    path('api/qaicash/get_bank_list', qaicash.getBankList.as_view(), name = 'get_bank_list'),
    path('api/qaicash/get_bank_limits', qaicash.getBankLimits.as_view(), name = 'get_bank_limits'),
    path('api/qaicash/submit_deposit', qaicash.submitDeposit.as_view(), name = 'submit_Deposit'),
    path('api/qaicash/submit_payout', qaicash.submitPayout.as_view(), name = 'submit_Payout'),
    path('api/qaicash/payout_transaction', qaicash.getPayoutTransaction.as_view(), name = 'payout_Transaction'),
    path('api/qaicash/approve_payout', qaicash.approvePayout.as_view(), name = 'approve_Payout'),
    path('api/qaicash/reject_payout', qaicash.rejectPayout.as_view(), name = 'reject_Payout'),
    path('api/qaicash/deposit_transaction', qaicash.getDepositTransaction.as_view(), name = 'deposit_Transaction'),
    path('api/qaicash/transaction_status', qaicash.transactionStatusUpdate.as_view(), name = 'transaction_status_update'),
    path('api/qaicash/payout_method', qaicash.payoutMethod.as_view(), name = 'payout_Method'),
    path('api/qaicash/payout_bank_list', qaicash.getPayoutBankList.as_view(), name = 'payout_Banklist'),
    path('api/qaicash/payout_bank_limits', qaicash.getPayoutBankLimits.as_view(), name = 'payout_Banklimits'),
    path('api/paypal/create_payment', paypal.paypalCreatePayment.as_view(), name = 'paypal_Create_Payment'),
    path('api/paypal/get_order', paypal.paypalGetOrder.as_view(), name = 'paypal_Get_Order'),
    path('api/paypal/execute_payment', paypal.paypalExecutePayment.as_view(), name = 'paypal_Execute_Payment'),
    path('api/linepay/reserve_payment', linepay.reservePayment, name = "LINEpay_reserve_payment"),
    path('api/astropay/new_invoice', astropay.astroNewInvoice, name = 'AstroPay_new_invoice'),
    path('api/astropay/payment_status', astropay.astroPaymentStatus, name = 'AstroPay_Payment_Status'),
    path('api/asiapay/deposit', asiapay.submitDeposit.as_view(), name = 'AsiaPay_deposit'),
]


