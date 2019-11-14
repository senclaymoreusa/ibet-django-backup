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
