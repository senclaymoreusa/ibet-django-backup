from django.shortcuts import render, get_object_or_404
from xadmin.views import CommAdminView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.template.loader import render_to_string

from accounting.models import *
from users.models import CustomUser
from django.core import serializers
from django.utils import timezone
from django.utils.timezone import timedelta
from utils.constants import *

import simplejson as json
import logging

logger = logging.getLogger("django")


class DepositView(CommAdminView):
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
                "vip_level": "Normal",
            }
            return HttpResponse(
                json.dumps(response_data), content_type="application/json"
            )

        elif get_type == "getLatestDeposit":
            user = request.GET.get("user")
            within_this_month = timezone.now() - timezone.timedelta(days=30)
            latest_deposit = Transaction.objects.filter(
                Q(user_id_id=user)
                & Q(transaction_type=TRANSACTION_DEPOSIT)
                & Q(request_time__gte=within_this_month)
            )
            logger.info('Find ' + str(latest_deposit.count()) + ' latest deposits')

            response_deposit_data = []
            for deposit in latest_deposit:
                depositDict = {}
                bankAccount = deposit.user_bank_account
                if bankAccount == None:
                    depositDict["bank"] = ""
                    depositDict["branch"] = ""
                    depositDict["city"] = ""
                    depositDict["name"] = ""
                    depositDict["account"] = ""
                else:
                    bank = bankAccount.bank
                    depositDict["bank"] = bank.name
                    depositDict["branch"] = bank.branch
                    depositDict["city"] = bank.city
                    depositDict["name"] = bankAccount
                    depositDict["account"] = deposit.user_bank_account

                depositDict["payment"] = deposit.get_channel_display()
                depositDict["tran_no"] = deposit.transaction_id
                depositDict["time_app"] = deposit.request_time.strftime(
                    "%d/%m/%y %H:%M:%S"
                )
                depositDict["amount"] = deposit.amount
                depositDict["tran_code"] = deposit.order_id
                depositDict["status"] = deposit.get_review_status_display()
                response_deposit_data.append(depositDict)
            return HttpResponse(
                json.dumps(response_deposit_data, default=myconverter),
                content_type="application/json",
            )

        else:
            context = super().get_context()
            title = "Finance / Deposits"
            context["breadcrumbs"].append({"title": title})
            context["title"] = title
            context["time"] = timezone.now()

            deposit_trans = Transaction.objects.filter(
                transaction_type=TRANSACTION_DEPOSIT
            )

            # PENDING DEPOSIT
            pending_trans = deposit_trans.filter(review_status=REVIEW_PEND)
            # SUCCESS DEPOSIT
            success_trans = deposit_trans.filter(review_status=REVIEW_APP)
            # FAILED DEPOSIT
            fail_trans = deposit_trans.filter(review_status=REVIEW_REJ)
            # CANCELLED DEPOSIT
            cancelled_trans = deposit_trans.filter(status=TRAN_CANCEL_TYPE)

            # pending deposit transaction
            pending_tran = []
            for pending_transaction in pending_trans:
                pendingDict = {}
                pendingDict["pk"] = pending_transaction.pk
                pendingDict["id"] = pending_transaction.user_id_id
                pendingDict["username"] = pending_transaction.user_id.username
                pendingDict["payment"] = pending_transaction.get_channel_display()
                pendingDict["tran_no"] = pending_transaction.transaction_id
                pendingDict["app_time"] = pending_transaction.request_time

                user_account = pending_transaction.user_bank_account
                if user_account == None:
                    pendingDict["bank"] = ""
                    pendingDict["branch"] = ""
                    pendingDict["city"] = ""
                    pendingDict["name"] = ""
                    pendingDict["account"] = ""
                else:
                    bank = user_account.bank
                    pendingDict["bank"] = bank.name
                    pendingDict["branch"] = bank.branch
                    pendingDict["city"] = bank.city
                    pendingDict["name"] = user_account.account_name
                    pendingDict["account"] = user_account.account_number

                pendingDict["trans_code"] = pending_transaction.order_id
                pendingDict["amount"] = pending_transaction.amount
                pending_tran.append(pendingDict)
            context["pending_tran"] = pending_tran

            # success transaction
            success_tran = []
            for success_transaction in success_trans:
                successDict = {}
                successDict["id"] = success_transaction.user_id_id
                successDict["username"] = CustomUser.objects.get(
                    pk=success_transaction.user_id_id
                ).username
                successDict["payment"] = success_transaction.get_channel_display()
                successDict["tran_no"] = success_transaction.transaction_id
                successDict["app_time"] = success_transaction.request_time
                successDict["arr_time"] = success_transaction.arrive_time

                user_account = success_transaction.user_bank_account
                if user_account == None:
                    successDict["bank"] = ""
                    successDict["branch"] = ""
                    successDict["city"] = ""
                    successDict["name"] = ""
                    successDict["account"] = ""
                else:
                    bank = user_account.bank
                    successDict["bank"] = bank.name
                    successDict["branch"] = bank.branch
                    successDict["city"] = bank.city
                    successDict["name"] = user_account.account_name
                    successDict["account"] = user_account.account_number

                successDict["trans_code"] = success_transaction.order_id
                successDict["amount"] = success_transaction.amount
                successDict["note"] = success_transaction.remark
                success_tran.append(successDict)
            context["success_tran"] = success_tran

            # failed transaction
            fail_tran = []
            for fail_transaction in fail_trans:
                failDict = {}
                failDict["id"] = fail_transaction.user_id_id
                failDict["username"] = CustomUser.objects.get(
                    pk=fail_transaction.user_id_id
                ).username
                failDict["payment"] = fail_transaction.get_channel_display()
                failDict["tran_no"] = fail_transaction.transaction_id
                failDict["app_time"] = fail_transaction.request_time

                user_account = fail_transaction.user_bank_account
                if user_account == None:
                    failDict["bank"] = ""
                    failDict["branch"] = ""
                    failDict["city"] = ""
                    failDict["name"] = ""
                    failDict["account"] = ""
                else:
                    bank = user_account.bank
                    failDict["bank"] = bank.name
                    failDict["branch"] = bank.branch
                    failDict["city"] = bank.city
                    failDict["name"] = user_account.account_name
                    failDict["account"] = user_account.account_number

                failDict["trans_code"] = fail_transaction.order_id
                failDict["amount"] = fail_transaction.amount
                fail_tran.append(failDict)
            context["fail_tran"] = fail_tran

            # cancelled transaction
            cancelled_tran = []
            for cancelled_transaction in cancelled_trans:
                cancelledDict = {}
                cancelledDict["id"] = cancelled_transaction.user_id_id
                cancelledDict["username"] = CustomUser.objects.get(
                    pk=cancelled_transaction.user_id_id
                ).username
                cancelledDict["payment"] = cancelled_transaction.get_channel_display()
                cancelledDict["tran_no"] = cancelled_transaction.transaction_id
                cancelledDict["app_time"] = cancelled_transaction.request_time

                user_account = cancelled_transaction.user_bank_account
                if user_account == None:
                    cancelledDict["bank"] = ""
                    cancelledDict["branch"] = ""
                    cancelledDict["city"] = ""
                    cancelledDict["name"] = ""
                    cancelledDict["account"] = ""
                else:
                    bank = user_account.bank
                    cancelledDict["bank"] = bank.name
                    cancelledDict["branch"] = bank.branch
                    cancelledDict["city"] = bank.city
                    cancelledDict["name"] = user_account.account_name
                    cancelledDict["account"] = user_account.account_number

                cancelledDict["trans_code"] = cancelled_transaction.order_id
                cancelledDict["amount"] = cancelled_transaction.amount
                cancelled_tran.append(cancelledDict)
            context["cancelled_tran"] = cancelled_tran

            return render(request, "deposits.html", context)

    def post(self, request):
        post_type = request.POST.get("type")

        if post_type == "audit_deposit":
            deposit_notes = request.POST.get("deposit_notes")
            dep_trans_no = request.POST.get("dep_trans_no")
            current_tran = Transaction.objects.filter(pk=dep_trans_no)
            current_tran.update(remark=deposit_notes)
            if "deposit-review-app" in request.POST:
                current_tran.update(review_status=REVIEW_APP)
                logger.info('Finish update the status of deposit' + str(dep_trans_no) + ' to Approve')
            elif "deposit-review-rej" in request.POST:
                current_tran.update(review_status=REVIEW_REJ)
                logger.info('Finish update the status of deposit' + str(dep_trans_no) + ' to Reject')
            elif "deposit-review-appnext" in request.POST:
                current_tran.update(review_status=REVIEW_APP)
                logger.info('Finish update the status of deposit' + str(dep_trans_no) + ' to Approve')
            elif "deposit-review-rejnext" in request.POST:
                current_tran.update(review_status=REVIEW_REJ)
                logger.info('Finish update the status of deposit' + str(dep_trans_no) + ' to Reject')
            return HttpResponseRedirect(reverse("xadmin:deposit_view"))

        elif post_type == "reviewTransaction":
            dep_trans_no = request.POST.get("dep_trans_no")
            result = request.POST.get("result")
            current_deposit = Transaction.objects.get(pk=dep_trans_no)
            
            if result == "Approve":
                current_deposit.review_status = REVIEW_APP
                logger.info('Finish update the status of deposit' + str(dep_trans_no) + ' to Approve')
            else:
                current_deposit.review_status = REVIEW_REJ
                logger.info('Finish update the status of deposit' + str(dep_trans_no) + ' to Reject')
            current_deposit.save()
            return HttpResponse(status=200)


def myconverter(o):
    if isinstance(o, timezone.date):
        return o.__str__()
