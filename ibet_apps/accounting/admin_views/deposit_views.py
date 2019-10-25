from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.template.loader import render_to_string
from django.core import serializers
from django.utils import timezone

from accounting.models import Transaction
from users.models import CustomUser
from xadmin.views import CommAdminView
from utils.constants import *

import simplejson as json
import logging

logger = logging.getLogger("django")

class GetDeposits(CommAdminView):
    def get(self, request, page):
        context = super().get_context()
        search_params = request.GET.get('search_params')
        print("search params:")
        print(search_params)
        page = int(page)
        type_deposit = Q(transaction_type=TRANSACTION_DEPOSIT)
        deposits = Transaction.objects.filter(type_deposit).order_by('-request_time')

        if search_params:
            name = Q(username__icontains=search_params)
            ids = Q(pk__icontains=search_params)
            ref_nos = Q(transaction_id__icontains=search_params)

            # get username & user id matches
            usernames = CustomUser.objects.filter(name)  # get QuerySet of users that match param
            user_ids = CustomUser.objects.filter(ids)  # get QuerySet of user_ids that match param
            all_user_matches = Q(user_id__in=(usernames | user_ids))

            all_transactions = deposits.filter(ref_nos | all_user_matches).order_by('-request_time')

            curr_page = all_transactions[page*20:(page+1)*20]
            deposit_count = all_transactions.count()
        else:
            curr_page = deposits[page*20:(page+1)*20]
            deposit_count = deposits.count()
        print(deposit_count)
        context['page_no'] = page
        context['total_pages'] = (deposit_count - 1) // 20

        if page > deposit_count // 20:
            raise Http404("This page does not exist")

        context['title'] = "Deposits"
        context['time'] = timezone.now()

        txn_data = []
        for trans in curr_page:
            trans_data = dict()
            trans_data["id"] = trans.user_id_id
            trans_data["username"] = trans.user_id.username
            trans_data["payment"] = trans.get_channel_display()
            trans_data["method"] = trans.method
            trans_data["tran_no"] = trans.transaction_id
            trans_data["app_time"] = trans.request_time
            trans_data["arr_time"] = trans.arrive_time
            trans_data["order_id"] = trans.order_id
            trans_data["amount"] = trans.amount
            trans_data["note"] = trans.remark
            trans_data["pk"] = trans.pk
            trans_data["status"] = trans.get_status_display()
            txn_data.append(trans_data)

        context['transactions'] = txn_data  # array of txn objects
        return render(request, 'deposits.html', context=context, content_type="text/html; charset=utf-8")

    def post(self):
        return render()

class DepositView(CommAdminView):
    def get(self, request):
        context = super().get_context()
        title = "Deposits"
        context["breadcrumbs"].append({"title": title})
        context["title"] = title
        context["time"] = timezone.now()

        deposit_trans = Transaction.objects.filter(
            transaction_type=TRANSACTION_DEPOSIT
        )
        # print(deposit_trans)

        # pending deposit transaction
        pending_tran = []
        success_tran = []
        fail_tran = []
        cancel_tran = []
        all_trans = []
        for trans in deposit_trans:
            trans_data = {}
            trans_data["id"] = trans.user_id_id
            trans_data["username"] = trans.user_id.username
            trans_data["payment"] = trans.get_channel_display()
            trans_data["tran_no"] = trans.transaction_id
            trans_data["app_time"] = trans.request_time
            trans_data["arr_time"] = trans.arrive_time
            trans_data["order_id"] = trans.order_id
            trans_data["amount"] = trans.amount
            trans_data["note"] = trans.remark
            trans_data["status"] = trans.get_status_display()
            all_trans.append(trans_data)
            if trans.status == TRAN_SUCCESS_TYPE:
                success_tran.append(trans_data)
            if trans.status == TRAN_CREATE_TYPE:
                pending_tran.append(trans_data)
            if trans.status == TRAN_FAIL_TYPE:
                fail_tran.append(trans_data)
            if trans.status == TRAN_CANCEL_TYPE:
                cancel_tran.append(trans_data)

        context["all_trans"] = all_trans
        context["pending_tran"] = pending_tran
        context["success_tran"] = success_tran
        context["fail_tran"] = fail_tran
        context["cancel_tran"] = cancel_tran

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


class UserInfo(CommAdminView):
    def get(self, request):
        get_type = request.GET.get("type")
        user_id = request.GET.get("user")

        if get_type == "getMemberInfo":
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
            user = CustomUser.objects.get(pk=user_id)
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


def myconverter(o):
    if isinstance(o, timezone.date):
        return o.__str__()

# user_account = cancelled_transaction.user_bank_account
# if user_account == None:
#     cancelledDict["bank"] = ""
#     cancelledDict["branch"] = ""
#     cancelledDict["city"] = ""
#     cancelledDict["name"] = ""
#     cancelledDict["account"] = ""
# else:
#     bank = user_account.bank
#     cancelledDict["bank"] = bank.name
#     cancelledDict["branch"] = bank.branch
#     cancelledDict["city"] = bank.city
#     cancelledDict["name"] = user_account.account_name
#     cancelledDict["account"] = user_account.account_number