from django.shortcuts import render, get_object_or_404
from xadmin.views import CommAdminView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.db.models import Q

from accounting.models import Transaction, DepositAccessManagement, DepositChannel, WithdrawAccessManagement, WithdrawChannel
from users.models import CustomUser

import simplejson as json
import datetime
from django.core import serializers
from django.utils.timezone import timedelta

class DepositView(CommAdminView): 
    def get(self, request):
        get_type = request.GET.get('type')

        if get_type == 'getMemberInfo':
            user_id= request.GET.get('user')
            user = CustomUser.objects.get(pk=user_id)
            response_data = {
                'id': user_id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'balance': user.main_wallet,
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        

        elif get_type == 'getLatestDeposit':
            user= request.GET.get('user')
            within_this_month = datetime.date.today() - datetime.timedelta(days=30)
            latest_deposit = Transaction.objects.filter(Q(user_id_id=user) & Q(transaction_type=0) & Q(request_time__gte=within_this_month))

            def myconverter(o):
                if isinstance(o, datetime.date):
                    return o.__str__()

            response_deposit_data = []
            for deposit in latest_deposit:
                depositDict = {}
                depositDict["payment"] = deposit.get_channel_display()
                depositDict["tran_no"] = deposit.transaction_id
                depositDict["time_app"] = deposit.request_time
                depositDict["bank"] = deposit.bank
                depositDict["branch"] = "..."
                depositDict["city"] = "..."
                depositDict["name"] = "..."
                depositDict["account"] = deposit.payer_id
                depositDict["amount"] = deposit.amount
                depositDict["status"] = deposit.get_status_display()
                response_deposit_data.append(depositDict)
            return HttpResponse(json.dumps(response_deposit_data, default = myconverter), content_type="application/json")


        else:
            context = super().get_context()
            title = 'Deposits'
            context["breadcrumbs"].append({'url': '/deposit/', 'title': title})
            context['title'] = title

            # CHANNEL
            depositChannel = DepositChannel.objects.all()
            # PENDING
            pending_trans = Transaction.objects.filter(Q(status=3) & Q(transaction_type=0))
            # SUCCESS
            success_trans = Transaction.objects.filter(Q(status=0) & Q(transaction_type=0))

            # channels
            channel_data = []
            for channel in depositChannel:
                depositDict = {}
                depositDict["channel_name"] = channel.get_thridParty_name_display()
                depositDict["min_deposit"] = channel.min_amount
                depositDict["max_deposit"] = channel.max_amount
                depositDict["fee"] = channel.transaction_fee
                # depositDict["volume"] = 
                # depositDict["new_users_volume"] = 
                # depositDict["blocked_risk_level"] = 
                depositDict["status"] = channel.switch
                channel_data.append(depositDict)
            context['channel_data'] = channel_data

            # pending transaction
            pending_tran = []
            for pending_transaction in pending_trans:
                pendingDict = {}
                pendingDict["id"] = pending_transaction.user_id_id
                pendingDict["username"] = CustomUser.objects.get(pk=pending_transaction.user_id_id).username
                # pendingDict["first_name"] = CustomUser.objects.get(pk=pending_transaction.user_id_id).first_name
                # pendingDict["last_name"] = CustomUser.objects.get(pk=pending_transaction.user_id_id).last_name
                # pendingDict["main_wallet"] = CustomUser.objects.get(pk=pending_transaction.user_id_id).main_wallet
                pendingDict["payment"] = pending_transaction.get_channel_display()
                pendingDict["tran_no"] = pending_transaction.transaction_id
                pendingDict["app_time"] = pending_transaction.request_time
                pendingDict["bank"] = pending_transaction.bank
                # pendingDict["branch"] =
                pendingDict["amount"] = pending_transaction.amount
                pending_tran.append(pendingDict)
            context['pending_tran'] = pending_tran

            # success transaction
            success_tran = []
            for success_transaction in success_trans:
                successDict = {}
                successDict["id"] = success_transaction.user_id_id
                successDict["username"] = CustomUser.objects.get(pk=success_transaction.user_id_id).username
                successDict["payment"] = success_transaction.channel
                successDict["tran_no"] = success_transaction.transaction_id
                successDict["app_time"] = success_transaction.request_time
                successDict["bank"] = success_transaction.bank
            #     # pendingDict["branch"] =
                successDict["amount"] = success_transaction.amount
                success_tran.append(successDict)
            context['success_tran'] = success_tran

            return render(request, 'deposits.html', context)


def edit_deposit_channel(request, channel_name):
    channel = get_object_or_404(DepositChannel, channel_name=channel_name)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.channel = request.channel
            post.save()

def deposit_channel_update(request, pk):
    book = get_object_or_404(DepositChannel, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
    else:
        form = BookForm(instance=book)
    return save_book_form(request, form, 'books/includes/partial_book_update.html')

