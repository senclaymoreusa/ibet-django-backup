from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers

import accounting.views.qaicashviews as qaicash
import accounting.views.paypalviews as paypal
import accounting.views.linepayviews as linepay
import accounting.views.astropayviews as astropay
import accounting.views.asiapayviews as asiapay
import accounting.views.help2payviews as help2pay
import accounting.views.circlepayviews as circlepay

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
    path('api/linepay/reserve_payment', csrf_exempt(linepay.reserve_payment), name = "LINEpay_reserve_payment"),
    path('api/linepay/confirm_payment', csrf_exempt(linepay.confirm_payment), name = "LINEpay_confirm_payment"),
    path('api/astropay/new_invoice', astropay.astroNewInvoice, name = 'AstroPay_new_invoice'),
    path('api/astropay/payment_status', astropay.astroPaymentStatus, name = 'AstroPay_Payment_Status'),
    path('api/astropay/sendCardToMobile_mobile', astropay.sendCardToMobile, name = 'AstroPay_Send_Card_To_Mobile'),
    path('api/astropay/checkUser', astropay.checkUser, name = 'AstroPay_Check_User'),
    path('api/astropay/sendCardToMobile_appid', astropay.sendCardToMobileWithAppId, name = 'AstroPay_Send_Card_To_Mobile_Appid'),
    path('api/astropay/verif_transtatus', astropay.verif_transtatus, name = 'AstroPay_verif_transtatus'),
    path('api/astropay/cancel_card', csrf_exempt(astropay.cancel_cashout_card), name = 'AstroPay_Cancel_Card'),
    path('api/astropay/capture_transaction', csrf_exempt(astropay.capture_transaction), name = "AstroPay_Capture_Transaction"),
    path('api/asiapay/deposit', asiapay.submitDeposit.as_view(), name = 'AsiaPay_deposit'),
    path('api/asiapay/cashout', asiapay.submitCashout.as_view(), name = 'AsiaPay_cashout'),
    path('api/asiapay/depositFinish', asiapay.depositfinish.as_view(), name = 'AsiaPay_deposit_finish'),
    path('api/asiapay/orderStatus', asiapay.orderStatus.as_view(), name = 'AsiaPay_Order_Status'),
    path('api/asiapay/exchangeRate', asiapay.exchangeRate.as_view(), name = 'AsiaPay_Exchange_Rate'),
    path('api/asiapay/depositArrive', asiapay.depositArrive.as_view(), name = 'AsiaPay_deposit_Arrive'),
    path('api/help2pay/deposit', help2pay.submitDeposit.as_view(), name = 'Help2pay_Deposit'),
    path('api/help2pay/deposit_result', help2pay.depositResult.as_view(), name = 'Help2pay_deposit_result'),
    path('api/circlepay/deposit', csrf_exempt(circlepay.create_deposit), name = "CirclePay_create_deposit"),
    path('api/circlepay/check_transaction', csrf_exempt(circlepay.check_transaction), name = "CirclePay_check_transaction")
]
