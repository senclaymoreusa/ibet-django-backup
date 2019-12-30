from django.urls import path, include
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers

import accounting.views.qaicashviews as qaicash
import accounting.views.paypalviews as paypal
import accounting.views.linepayviews as linepay
import accounting.views.astropayviews as astropay
import accounting.views.asiapayviews as asiapay
import accounting.views.help2payviews as help2pay
import accounting.views.circlepayviews as circlepay
import accounting.views.payzodviews as payzod
import accounting.views.fgateviews as fgate
import accounting.views.paymentiqviews as paymentiq
import accounting.views.scratchcardviews as scratchcard
import accounting.transactions

urlpatterns = [
    path('api/qaicash/deposit_method', qaicash.getDepositMethod.as_view(), name='Qaicash_deposit_method'),
    path('api/qaicash/get_bank_list', qaicash.getBankList.as_view(), name='Qaicash_get_bank_list'),
    path('api/qaicash/get_bank_limits', qaicash.getBankLimits.as_view(), name='Qaicash_get_bank_limits'),
    path('api/qaicash/submit_deposit', qaicash.submitDeposit.as_view(), name='Qaicash_submit_Deposit'),
    path('api/qaicash/submit_payout', qaicash.submitPayout.as_view(), name='Qaicash_submit_Payout'),
    path('api/qaicash/payout_transaction', qaicash.getPayoutTransaction.as_view(), name='Qaicash_payout_Transaction'),
    path('api/qaicash/approve_payout', qaicash.approvePayout.as_view(), name='Qaicash_approve_Payout'),
    path('api/qaicash/reject_payout', qaicash.rejectPayout.as_view(), name='Qaicash_reject_Payout'),
    path('api/qaicash/deposit_transaction', qaicash.getDepositTransaction.as_view(), name='Qaicash_deposit_Transaction'),
    path('api/qaicash/confirm', csrf_exempt(qaicash.transactionConfirm), name='Qaicash_Transaction_confirm'),
    path('api/qaicash/get_transaction_status', qaicash.get_transaction_status, name="Qaicash_Get_Transaction_Status"),
    path('api/qaicash/payout_method', qaicash.payoutMethod.as_view(), name='Qaicash_payout_Method'),
    path('api/qaicash/payout_bank_list', qaicash.getPayoutBankList.as_view(), name='Qaicash_payout_Banklist'),
    path('api/qaicash/payout_bank_limits', qaicash.getPayoutBankLimits.as_view(), name='Qaicash_payout_Banklimits'),
    path('api/paypal/create_payment', paypal.paypalCreatePayment.as_view(), name='paypal_Create_Payment'),
    path('api/paypal/get_order', paypal.paypalGetOrder.as_view(), name='paypal_Get_Order'),
    path('api/paypal/execute_payment', paypal.paypalExecutePayment.as_view(), name='paypal_Execute_Payment'),
    path('api/linepay/reserve_payment', csrf_exempt(linepay.reserve_payment), name="LINEpay_reserve_payment"),
    path('api/linepay/confirm_payment', csrf_exempt(linepay.confirm_payment), name="LINEpay_confirm_payment"),
    path('api/astropay/new_invoice', astropay.astroNewInvoice, name='AstroPay_new_invoice'),
    path('api/astropay/payment_status', astropay.astroPaymentStatus, name='AstroPay_Payment_Status'),
    path('api/astropay/sendCardToMobile_mobile', astropay.sendCardToMobile, name='AstroPay_Send_Card_To_Mobile'),
    path('api/astropay/checkUser', astropay.checkUser, name='AstroPay_Check_User'),
    path('api/astropay/sendCardToMobile_appid', astropay.sendCardToMobileWithAppId, name='AstroPay_Send_Card_To_Mobile_Appid'),
    path('api/astropay/verif_transtatus', astropay.verif_transtatus, name='AstroPay_verif_transtatus'),
    path('api/astropay/cancel_card', csrf_exempt(astropay.cancel_cashout_card), name='AstroPay_Cancel_Card'),
    path('api/astropay/capture_transaction', csrf_exempt(astropay.capture_transaction), name="AstroPay_Capture_Transaction"),
    path('api/asiapay/deposit', asiapay.submitDeposit.as_view(), name='AsiaPay_deposit'),
    path('api/asiapay/cashout', asiapay.submitCashout.as_view(), name='AsiaPay_cashout'),
    path('api/asiapay/depositFinish', asiapay.depositfinish.as_view(), name='AsiaPay_deposit_finish'),
    path('api/asiapay/orderStatus', asiapay.orderStatus.as_view(), name='AsiaPay_Order_Status'),
    path('api/asiapay/exchangeRate', asiapay.exchangeRate.as_view(), name='AsiaPay_Exchange_Rate'),
    path('api/asiapay/depositArrive', csrf_exempt(asiapay.depositArrive), name='AsiaPay_deposit_Arrive'),
    path('api/asiapay/cashoutArrive', csrf_exempt(asiapay.payoutArrive), name='AsiaPay_cashout_Arrive'),
    path('api/help2pay/deposit', help2pay.SubmitDeposit.as_view(), name='Help2pay_Deposit'),
    path('api/help2pay/deposit_result', help2pay.DepositResult.as_view(), name='Help2pay_deposit_result'),
    path('api/help2pay/deposit_success', help2pay.depositFrontResult, name = 'Help2pay_deposit_sucess'),
    path('api/help2pay/deposit_status', help2pay.depositStatus, name = 'Help2pay_deposit_status'),
    path('api/help2pay/submit_payout', csrf_exempt(help2pay.SubmitPayout.as_view()), name = 'Help2pay_submit_payout'),
    path('api/help2pay/request_withdraw', csrf_exempt(help2pay.ConfirmWithdrawRequest.as_view()), name = 'Help2pay_withdraw_request'),
    path('api/fgate/chargeCard', fgate.chargeCard.as_view(), name = 'fgate_Charge_Card'),
    path('api/circlepay/deposit', csrf_exempt(circlepay.create_deposit), name="CirclePay_create_deposit"),
    path('api/circlepay/confirm', csrf_exempt(circlepay.confirm_payment), name="CirclePay_Confirm_Payment"),
    path('api/circlepay/check_transaction', csrf_exempt(circlepay.check_transaction), name="CirclePay_check_transaction"),
    path('api/payzod/deposit', csrf_exempt(payzod.get_qr_code), name="Payzod_Deposit"),
    path('api/payzod/confirm', csrf_exempt(payzod.confirm_payment), name="CirclePay_Confirm_Payment"),
    path('api/payzod/check_transtatus', csrf_exempt(payzod.get_qr_code), name="Payzod_Check_Status"),
    path('api/paymentiq/verifyuser', csrf_exempt(paymentiq.verify_user), name="PaymentIQ_Verify_User"),
    path('api/paymentiq/authorize', csrf_exempt(paymentiq.authorize), name="Payment_IQ_Authorize"),
    path('api/paymentiq/transfer', csrf_exempt(paymentiq.transfer), name="Payment_IQ_Transfer"),
    path('api/paymentiq/cancel', csrf_exempt(paymentiq.cancel), name="Payment_IQ_Cancel"),
    path('api/scratchcard/deposit', csrf_exempt(scratchcard.create_deposit), name="Scratch_Card_Deposit"),
    path('api/scratchcard/confirm', csrf_exempt(scratchcard.confirm_transaction), name="Scratch_Card_Confirm"),
    path('api/transactions/get_transactions', accounting.transactions.get_transactions, name="Get_Transactions"),
    path('api/transactions/save_transaction', csrf_exempt(accounting.transactions.save_transaction), name="Save_Transaction")
]


