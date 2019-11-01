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
import pytz

logger = logging.getLogger("django")


# class TestView(CommAdminView):
#     def get(self, request, type, page):
#         if type == "deposits":
#             return render(request, 'deposits.html')
#         else:
#             return render(request, 'withdrawals.html')

# class GetDeposits(CommAdminView):
class GetTransactions(CommAdminView):
    def get(self, request, txn_type, page=0):
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
        txn_q = Q(transaction_type=TRANSACTION_DEPOSIT) if txn_type == "deposit" else Q(transaction_type=TRANSACTION_WITHDRAWAL)
        
        all_transactions = Transaction.objects.select_related('user_id').filter(txn_q).order_by('-request_time')
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

        # print("transaction count: (to count total pages)")
        # print(txn_count)
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
            trans_data["channel"] = trans.get_channel_display()
            trans_data["method"] = trans.method
            trans_data["tran_no"] = trans.transaction_id
            trans_data["app_time"] = trans.request_time.strftime('%d %B %Y %X') if trans.request_time else ''
            trans_data["arr_time"] = trans.arrive_time.strftime('%d %B %Y %X') if trans.arrive_time else ''
            trans_data["order_id"] = trans.order_id
            trans_data["amount"] = trans.amount
            trans_data["note"] = trans.remark
            trans_data["pk"] = trans.pk
            trans_data["status"] = trans.get_status_display()

            trans_data["risk_level"] = trans.user_id.get_risk_level_display()
            # trans_data["player_segment"] = trans.user_id.player_segment
            trans_data["user_status"] = trans.user_id.get_member_status_display()

            txn_data.append(trans_data)

        context['transactions'] = txn_data  # array of txn objects
        if txn_type == "deposit":
            return render(request, 'deposits.html', context=context, content_type="text/html; charset=utf-8")
        else:
            return render(request, 'withdrawals.html', context=context, content_type="text/html; charset=utf-8")

def filterByStatus(status, transactions):
    # check for status
    status_code = TRAN_STATUS_DICT[status]
    status_type = Q(status=status_code)
    all_transactions = transactions.filter(status_type).order_by('-request_time')

    return all_transactions


class ConfirmSettlement(CommAdminView):
    def post(self, request):
        txn_pk = request.POST.get("dep_trans_no")
        result = request.POST.get("result")
        # print(dep_trans_no)
        # print(result)
        current_deposit = Transaction.objects.get(pk=txn_pk)

        if result == "approve":
            current_deposit.status = 0
            logger.info('Finish update the status of deposit ' + str(txn_pk) + ' to Approve')
        else:
            current_deposit.status = 1
            logger.info('Finish update the status of deposit ' + str(txn_pk) + ' to Reject')
        current_deposit.save()
        return HttpResponse(status=200)

class UserInfo(CommAdminView):
    def get(self, request):
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

class GetLatestTransactions(CommAdminView):
    def get(self, request):
        get_type = request.GET.get("type")
        user_id = request.GET.get("user")
        txn_q = Q(transaction_type=TRANSACTION_DEPOSIT) if get_type == "deposits" else Q(transaction_type=TRANSACTION_WITHDRAWAL)
        
        user = CustomUser.objects.get(pk=user_id)

        latest_transactions = Transaction.objects.filter(
            Q(user_id_id=user)
            & txn_q
        ).order_by('-request_time')
        logger.info('Find ' + str(latest_transactions.count()) + ' latest ' + get_type)

        # within_this_month = timezone.now() - timezone.timedelta(days=30)
        # month_query = Q(request_time__gte=within_this_month)
        txn_data = []

        for trans in latest_transactions[:20]:
            txn = dict()
            txn["payment"] = trans.get_channel_display()
            txn["tran_no"] = trans.transaction_id
            txn["time_app"] = trans.request_time.strftime("%d %B %Y %X")
            txn["amount"] = trans.amount
            txn["order_id"] = trans.order_id
            txn["status"] = trans.get_status_display()
            txn_data.append(txn)
        return HttpResponse(
            json.dumps(txn_data, default=myconverter),
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