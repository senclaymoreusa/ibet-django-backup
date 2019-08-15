from django.shortcuts import render
from xadmin.views import CommAdminView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.db.models import Q, Sum, Count
from django.db.models.functions import Coalesce
import datetime

from accounting.models import (
    Transaction,
    DepositAccessManagement,
    DepositChannel,
    WithdrawAccessManagement,
    WithdrawChannel,
)
from users.models import CustomUser


class WithdrawalView(CommAdminView):
    def get(self, request):
        context = super().get_context()
        title = "Withdrawals"
        context["breadcrumbs"].append({"url": "/withdrawal/", "title": title})
        context["title"] = title

        # CHANNEL
        withdrawalChannel = WithdrawChannel.objects.all()
        # PENDING
        pending_trans = Transaction.objects.filter(Q(status=3) & Q(transaction_type=1))
        # SUCCESS
        success_trans = Transaction.objects.filter(Q(status=0) & Q(transaction_type=1))

        # channels
        channel_data = []
        for channel in withdrawalChannel:
            withdrawalDict = {}
            withdrawalDict["channel_name"] = channel.thirdParty_name
            withdrawalDict["min_deposit"] = channel.min_amount
            withdrawalDict["max_deposit"] = channel.max_amount
            withdrawalDict["fee"] = channel.transaction_fee
            # depositDict["volume"] =
            # depositDict["new_users_volume"] =
            # depositDict["blocked_risk_level"] =
            withdrawalDict["status"] = channel.switch
            channel_data.append(withdrawalDict)
        context["channel_data"] = channel_data

        # pending transaction
        pending_tran = []
        for pending_transaction in pending_trans:
            pendingDict = {}
            pendingDict["id"] = pending_transaction.user_id_id
            pendingDict["username"] = CustomUser.objects.get(
                pk=pending_transaction.user_id_id
            ).username
            pendingDict["tran_no"] = pending_transaction.transaction_id
            pendingDict["app_time"] = pending_transaction.request_time
            # pendingDict["bank"] = pending_transaction.bank
            # pendingDict["branch"] =
            pendingDict["amount"] = pending_transaction.amount
            pendingDict["balance"] = CustomUser.objects.get(
                pk=pending_transaction.user_id_id
            ).main_wallet
            # withdrawal today
            pendingDict["withdrawal_today"] = (
                pending_trans.filter(
                    Q(arrive_time__gte=datetime.date.today())
                    & Q(user_id_id=pending_transaction.user_id_id)
                )
                .values("amount")
                .aggregate(sum=Sum("amount"))
            )
            pendingDict["withdrawal_count_today"] = pending_trans.filter(
                Q(arrive_time__gte=datetime.date.today())
                & Q(user_id_id=pending_transaction.user_id_id)
            ).aggregate(count=Count("amount"))
            pendingDict["channel"] = pending_transaction.withdraw_channel
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
            successDict["payment"] = success_transaction.withdraw_channel
            successDict["tran_no"] = success_transaction.transaction_id
            successDict["app_time"] = success_transaction.request_time
            # successDict["bank"] = success_transaction.bank
            #     # pendingDict["branch"] =
            successDict["amount"] = success_transaction.amount
            success_tran.append(successDict)
        context["success_tran"] = success_tran

        return render(request, "withdrawals.html", context)

