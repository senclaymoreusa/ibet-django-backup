from django.shortcuts import render
from xadmin.views import CommAdminView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.db.models import Q, Sum, Count
from django.db.models.functions import Coalesce
from accounting.models import *
from users.models import CustomUser

import datetime
import simplejson as json
import logging

logger = logging.getLogger("django")


class WithdrawalView(CommAdminView):
    def get(self, request):
        get_type = request.GET.get("type")

        if get_type == "getMemberInfo":
            user_id = request.GET.get("user")
            user = CustomUser.objects.get(pk=user_id)
            logger.info("Get user" + str(user))
            response_data = {
                "id": user_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "balance": user.main_wallet,
                "risk_level": user.get_risk_level_display(),
                "vip_level": "Normal"
            }
            return HttpResponse(
                json.dumps(response_data), content_type="application/json"
            )

        elif get_type == "getLatestWithdraw":
            user = request.GET.get("user")
            within_this_month = datetime.date.today() - datetime.timedelta(days=30)
            latest_withdraw = Transaction.objects.filter(
                Q(user_id_id=user)
                & Q(transaction_type=TRANSACTION_WITHDRAW)
                & Q(request_time__gte=within_this_month)
            )
            logger.info('Find ' + str(latest_withdraw.count()) + ' latest withdrawals')

            response_withdraw_data = []
            for withdraw in latest_withdraw:
                withdrawDict = {}
                withdrawDict["tran_no"] = withdraw.transaction_id
                withdrawDict["app_time"] = withdraw.request_time.strftime(
                    "%d/%m/%y %H:%M:%S"
                )

                bankAccount = withdraw.user_bank_account
                if bankAccount == None:
                    withdrawDict["bank"] = ""
                    withdrawDict["city"] = ""
                    withdrawDict["name"] = ""
                    withdrawDict["account"] = ""
                else:
                    bank = bankAccount.bank
                    withdrawDict["bank"] = bank.name
                    withdrawDict["city"] = bank.city
                    withdrawDict["name"] = bankAccount
                    withdrawDict["account"] = withdraw.user_bank_account

                withdrawDict["amount"] = withdraw.amount
                withdrawDict["status"] = withdraw.get_review_status_display()
                response_withdraw_data.append(withdrawDict)
            return HttpResponse(
                json.dumps(response_withdraw_data, default=myconverter),
                content_type="application/json",
            )

        else:
            context = super().get_context()
            title = "Finance / Withdrawals"
            context["breadcrumbs"].append({"url": "/withdrawal/", "title": title})
            context['time'] = timezone.now()

            # WITHDRAWAL TRANSACTIONS
            withdrawal_trans = Transaction.objects.filter(transaction_type=TRANSACTION_WITHDRAW)

            # PENDING
            pending_trans = withdrawal_trans.filter(review_status=REVIEW_PEND) 
            # APPROVED
            approved_trans = withdrawal_trans.filter(review_status=REVIEW_APP) 
            # REJECTED
            rejected_trans = withdrawal_trans.filter(review_status=REVIEW_REJ) 
            # SUCCESSFUL
            success_trans = withdrawal_trans.filter(status=TRAN_SUCCESS_TYPE) 
            # FAILED
            failed_trans = withdrawal_trans.filter(status=TRAN_FAIL_TYPE)
            # RESEND
            resend_trans = withdrawal_trans.filter(status=TRAN_RESEND_TYPE) 

            # pending transaction
            pending_tran = []
            for pending_transaction in pending_trans:
                pendingDict = {}
                pendingDict["pk"] = pending_transaction.pk
                pendingDict["id"] = pending_transaction.user_id_id
                pendingDict["username"] = pending_transaction.user_id.username
                pendingDict["tran_no"] = pending_transaction.transaction_id
                pendingDict["app_time"] = pending_transaction.request_time
                pendingDict["vip"] = "vip"
                pendingDict["risk"] = pending_transaction.user_id.get_risk_level_display()

                user_account = pending_transaction.user_bank_account
                if user_account == None:
                    pendingDict["bank"] = ''
                    pendingDict["account"] = ''
                else:
                    pendingDict["bank"] = user_account.bank.name
                    pendingDict["account"] = user_account.bank.account_number

                pendingDict["balance"] = pending_transaction.user_id.main_wallet
                pendingDict["amount"] = pending_transaction.amount
                
                # withdrawal today
                pendingDict["withdrawal_today"] = (
                    pending_trans.filter(
                        Q(arrive_time__gte=datetime.date.today())
                        & Q(user_id_id=pending_transaction.user_id_id)
                    )
                    .values("amount")
                    .aggregate(sum=Sum("amount"))['sum']
                )
                if pendingDict["withdrawal_today"] == None:
                    pendingDict["withdrawal_today"] = "0"

                pendingDict["withdrawal_count_today"] = pending_trans.filter(
                    Q(arrive_time__gte=datetime.date.today())
                    & Q(user_id_id=pending_transaction.user_id_id)
                ).aggregate(count=Count("amount"))['count']

                pendingDict["channel"] = pending_transaction.get_channel_display()
                pending_tran.append(pendingDict)
            context["pending_tran"] = pending_tran

            # approved transaction
            approved_tran = []
            for approved_transaction in approved_trans:
                approvedDict = {}
                approvedDict["id"] = approved_transaction.user_id_id
                approvedDict["username"] = approved_transaction.user_id.username
                approvedDict["tran_no"] = approved_transaction.transaction_id
                user_account = approved_transaction.user_bank_account
                if user_account == None:
                    approvedDict["bank"] = ''
                    approvedDict["city"] = ''
                    approvedDict["name"] = ''
                    approvedDict["account"] = ''
                else:
                    bank = user_account.bank
                    approvedDict["bank"] = bank.name
                    approvedDict["city"] = bank.city
                    approvedDict["name"] = user_account.account_name
                    approvedDict["account"] = user_account.account_number

                approvedDict["amount"] = approved_transaction.amount
                approvedDict["app_time"] = approved_transaction.request_time
                # auditor
                approvedDict["audit_time"] = "..."
                approvedDict["processing_time"] = approved_transaction.arrive_time
                approvedDict["auditor"] = "auditor"
                approvedDict["channel"] = approved_transaction.get_channel_display()
                approvedDict["note"] = approved_transaction.remark
                approved_tran.append(approvedDict)
            context["approved_tran"] = approved_tran


            # rejected transaction
            rejected_tran = []
            for rejected_transaction in rejected_trans:
                rejectedDict = {}
                rejectedDict["id"] = rejected_transaction.user_id_id
                rejectedDict["username"] = rejected_transaction.user_id.username
                rejectedDict["tran_no"] = rejected_transaction.transaction_id
                user_account = rejected_transaction.user_bank_account
                if user_account == None:
                    rejectedDict["bank"] = ''
                    rejectedDict["city"] = ''
                    rejectedDict["name"] = ''
                    rejectedDict["account"] = ''
                else:
                    bank = user_account.bank
                    rejectedDict["bank"] = bank.name
                    rejectedDict["city"] = bank.city
                    rejectedDict["name"] = user_account.account_name
                    rejectedDict["account"] = user_account.account_number

                rejectedDict["amount"] = rejected_transaction.amount
                rejectedDict["app_time"] = "..."
                # auditor
                rejectedDict["audit_time"] = "..."
                rejectedDict["process_time"] = rejected_transaction.request_time
                rejectedDict["auditor"] = "auditor"
                rejectedDict["channel"] = rejected_transaction.get_channel_display()
                rejected_tran.append(rejectedDict)
            context["rejected_tran"] = rejected_tran


            # successful transaction
            success_tran = []
            for success_transaction in success_trans:
                successDict = {}
                successDict["id"] = success_transaction.user_id_id
                successDict["username"] = success_transaction.user_id.username
                successDict["tran_no"] = success_transaction.transaction_id
                user_account = success_transaction.user_bank_account
                if user_account == None:
                    successDict["bank"] = ''
                    successDict["city"] = ''
                    successDict["name"] = ''
                    successDict["account"] = ''
                else:
                    bank = user_account.bank
                    successDict["bank"] = bank.name
                    successDict["city"] = bank.city
                    successDict["name"] = user_account.account_name
                    successDict["account"] = user_account.account_number

                successDict["amount"] = success_transaction.amount
                successDict["app_time"] = "..."
                # auditor
                successDict["audit_time"] = "..."
                successDict["process_time"] = success_transaction.request_time
                successDict["auditor"] = "auditor"
                successDict["channel"] = success_transaction.get_channel_display()
                success_tran.append(successDict)
            context["success_tran"] = success_tran

            # failed transaction
            failed_tran = []
            for failed_transaction in failed_trans:
                failedDict = {}
                failedDict["id"] = failed_transaction.user_id_id
                failedDict["username"] = failed_transaction.user_id.username
                failedDict["tran_no"] = failed_transaction.transaction_id
                user_account = failed_transaction.user_bank_account
                if user_account == None:
                    failedDict["bank"] = ''
                    failedDict["city"] = ''
                    failedDict["name"] = ''
                    failedDict["account"] = ''
                else:
                    bank = user_account.bank
                    failedDict["bank"] = bank.name
                    failedDict["city"] = bank.city
                    failedDict["name"] = user_account.account_name
                    failedDict["account"] = user_account.account_number

                failedDict["amount"] = failed_transaction.amount
                failedDict["app_time"] = "..."
                # auditor
                failedDict["audit_time"] = "..."
                failedDict["process_time"] = failed_transaction.request_time
                failedDict["auditor"] = "auditor"
                failedDict["channel"] = failed_transaction.get_channel_display()
                failed_tran.append(failedDict)
            context["failed_tran"] = failed_tran

            return render(request, "withdrawals.html", context)

    def post(self, request):
        post_type = request.POST.get("type")

        if post_type == "audit_withdraw":
            withdraw_notes = request.POST.get("withdraw_notes")
            wtd_trans_no = request.POST.get("wtd_trans_no")
            current_tran = Transaction.objects.filter(pk=wtd_trans_no)
            current_tran.update(remark=withdraw_notes)
            if 'withdraw-review-app' in request.POST:
                current_tran.update(review_status=REVIEW_APP)
                logger.info('Finish update the status of withdrawal' + str(wtd_trans_no) + ' to Approve')
            elif 'withdraw-review-rej' in request.POST:
                current_tran.update(review_status=REVIEW_REJ)
                logger.info('Finish update the status of withdrawal' + str(wtd_trans_no) + ' to Reject')
            elif 'withdraw-review-appnext' in request.POST:
                current_tran.update(review_status=REVIEW_APP)
                logger.info('Finish update the status of withdrawal' + str(wtd_trans_no) + ' to Approve')
            elif 'withdraw-review-rejnext' in request.POST:
                current_tran.update(review_status=REVIEW_REJ)
                logger.info('Finish update the status of withdrawal' + str(wtd_trans_no) + ' to Reject')

            return HttpResponseRedirect(reverse('xadmin:withdrawal_view'))

def myconverter(o):
    if isinstance(o, datetime.date):
        return o.__str__()