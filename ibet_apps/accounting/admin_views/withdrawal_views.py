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
        search_params = request.GET.get('search_params')
        status = request.GET.get('status')
        date_from = request.GET.get('from')
        date_to = request.GET.get('to')

        print("search params: " + str(search_params))
        print("status: " + str(status))
        print("from: ", date_from)
        print("to: ", date_to)

        page = int(page)
        txn_type = Q(transaction_type=TRANSACTION_WITHDRAWAL)

        all_transactions = Transaction.objects.filter(txn_type).order_by('-request_time')
        # filter by status
        if status and status != 'all':
            all_transactions = filterByStatus(status, all_transactions)
        # do further filtering using search params, if any
        if search_params:
            name = Q(username__icontains=search_params)
            ids = Q(pk__icontains=search_params)
            ref_nos = Q(transaction_id__icontains=search_params)

            # get username & user id matches
            usernames = CustomUser.objects.filter(name)  # get QuerySet of users that match param
            user_ids = CustomUser.objects.filter(ids)  # get QuerySet of user_ids that match param
            all_user_matches = Q(user_id__in=(usernames | user_ids))

            all_transactions = all_transactions.filter(ref_nos | all_user_matches).order_by('-request_time')
        if date_from:
            from_date = timezone.datetime.strptime(date_from, "%m/%d/%Y")
            from_date = pytz.utc.localize(from_date)
            from_query = Q(request_time__gte=from_date)
            all_transactions = all_transactions.filter(from_query)
        if date_to:
            to_date = timezone.datetime.strptime(date_to, "%m/%d/%Y")
            to_date = pytz.utc.localize(to_date)
            to_query = Q(request_time__lte=to_date)
            all_transactions = all_transactions.filter(to_query)

        curr_page = all_transactions[page * 20:(page + 1) * 20]
        txn_count = all_transactions.count()

        print("deposit count: (to count total pages)")
        print(txn_count)
        total_pages = (txn_count - 1) // 20 if (txn_count - 1) // 20 > 0 else 0
        context['page_no'] = page
        context['total_pages'] = total_pages

        if page > txn_count // 20:
            raise Http404("This page does not exist")

        context['title'] = "Withdrawals"
        context['time'] = timezone.now()

        txn_data = []
        for trans in curr_page:
            trans_data = dict()
            trans_data["id"] = trans.user_id_id
            trans_data["username"] = trans.user_id.username
            trans_data["payment"] = trans.get_channel_display()
            trans_data["method"] = trans.method
            trans_data["tran_no"] = trans.transaction_id
            trans_data["app_time"] = trans.request_time.strftime('%d %B %Y %X') if trans.request_time else ''
            trans_data["arr_time"] = trans.arrive_time.strftime('%d %B %Y %X') if trans.arrive_time else ''
            trans_data["order_id"] = trans.order_id
            trans_data["amount"] = trans.amount
            trans_data["note"] = trans.remark
            trans_data["pk"] = trans.pk
            trans_data["status"] = trans.get_status_display()
            txn_data.append(trans_data)

        context['transactions'] = txn_data  # array of txn objects
        return render(request, 'withdrawals.html', context=context, content_type="text/html; charset=utf-8")


def filterByStatus(status, transactions):
    # check for status
    status_code = TRAN_STATUS_DICT[status]
    status_type = Q(status=status_code)
    all_transactions = transactions.filter(status_type).order_by('-request_time')

    return all_transactions


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