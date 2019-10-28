from django.shortcuts import render
from xadmin.views import CommAdminView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.db.models import Q, Sum, Count
from django.db.models.functions import Coalesce
from accounting.models import *
from users.models import CustomUser
from django.utils import timezone
from django.urls import reverse

import simplejson as json
import logging

logger = logging.getLogger("django")


class GetWithdrawals(CommAdminView):
    def get(self, request, page):
        context = super().get_context()

        page = int(page)
        return render(request, 'withdrawals.html', context=context, content_type="text/html; charset=utf-8")


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
            within_this_month = timezone.now() - timezone.timedelta(days=30)
            latest_withdraw = Transaction.objects.filter(
                Q(user_id_id=user)
                & Q(transaction_type=TRANSACTION_WITHDRAWAL)
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
            withdrawal_trans = Transaction.objects.filter(transaction_type=TRANSACTION_WITHDRAWAL)

            # PENDING
            pending_trans = withdrawal_trans.filter(review_status=REVIEW_PEND) 
            # APPROVED
            approved_trans = withdrawal_trans.filter(review_status=REVIEW_APP) 
            # REJECTED
            rejected_trans = withdrawal_trans.filter(review_status=REVIEW_REJ) 
            # SUCCESSFUL
            success_trans = withdrawal_trans.filter(status=TRAN_SUCCESS)
            # FAILED
            failed_trans = withdrawal_trans.filter(status=TRAN_FAIL)
            # RESEND
            resend_trans = withdrawal_trans.filter(status=TRAN_RESEND)

            return render(request, "withdrawals.html", context)


def myconverter(o):
    if isinstance(o, timezone.date):
        return o.__str__()