from django.shortcuts import render, get_object_or_404
from xadmin.views import CommAdminView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.template.loader import render_to_string

from accounting.models import *
from users.models import CustomUser

import simplejson as json
import datetime
from django.core import serializers
from django.utils.timezone import timedelta

from utils.constants import *

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
                depositDict["payment"] = deposit.deposit_channel
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




        # elif get_type == 'getChannelInfo':
        #     deposit_channel = request.GET.get('current_deposit_channel')
        #     current_channel_obj = DepositChannel.objects.get(pk=deposit_channel)
        #     context = super().get_context()
        #     context['current_channel_name'] = current_channel_obj.get_thridParty_name_display()
            
        #     response_data = {
        #         'name': current_channel_obj.get_thridParty_name_display(),
        #         'status': current_channel_obj.get_switch_display(),
        #         'min_deposit': current_channel_obj.min_amount,
        #         'max_deposit': current_channel_obj.max_amount,
        #         'transaction_fee': current_channel_obj.transaction_fee,
        #         'volumn': current_channel_obj.volume,
        #         'limit_access': current_channel_obj.limit_access,
        #     }
        #     return HttpResponse(json.dumps(response_data), content_type="application/json")
        #     # return render(request, 'deposits.html', context)

            



        else:
            context = super().get_context()
            title = 'Deposits'
            context["breadcrumbs"].append({'url': '/deposit/', 'title': title})
            context['title'] = title

            # CHANNEL
            depositChannel = DepositChannel.objects.all()
            # PENDING
            pending_trans = Transaction.objects.filter(Q(status=tran_pending_type) & Q(transaction_type=0))
            # SUCCESS
            success_trans = Transaction.objects.filter(Q(status=tran_success_type) & Q(transaction_type=0))
            # FAILED
            fail_trans = Transaction.objects.filter(Q(status=tran_fail_type) & Q(transaction_type=0))
            # CANCELLED
            cancelled_trans = Transaction.objects.filter(Q(status=tran_cancel_type) & Q(transaction_type=0))

            # channels
            channel_data = []
            for channel in depositChannel:
                depositDict = {}
                depositDict["channel_id"] = channel.pk
                depositDict["channel_name"] = channel.get_thridParty_name_display()
                depositDict["min_deposit"] = channel.min_amount
                depositDict["max_deposit"] = channel.max_amount
                depositDict["fee"] = channel.transaction_fee
                # depositDict["volume"] = 
                # depositDict["new_users_volume"] = 
                # depositDict["blocked_risk_level"] = 
                depositDict["status"] = channel.get_switch_display()
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
                pendingDict["payment"] = pending_transaction.deposit_channel
                pendingDict["tran_no"] = pending_transaction.transaction_id
                pendingDict["app_time"] = pending_transaction.request_time
                channel = pending_transaction.deposit_channel
                # pendingDict["bank"] = DepositChannel.objects.get(pk=channel)
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
                successDict["payment"] = success_transaction.deposit_channel
                successDict["tran_no"] = success_transaction.transaction_id
                successDict["app_time"] = success_transaction.request_time
                # successDict["bank"] = success_transaction.bank
            #     # pendingDict["branch"] =
                successDict["amount"] = success_transaction.amount
                success_tran.append(successDict)
            context['success_tran'] = success_tran

            # failed transaction
            fail_tran = []
            for fail_transaction in fail_trans:
                failDict = {}
                failDict["id"] = fail_transaction.user_id_id
                failDict["username"] = CustomUser.objects.get(pk=fail_transaction.user_id_id).username
                failDict["payment"] = fail_transaction.channel
                failDict["tran_no"] = fail_transaction.transaction_id
                failDict["app_time"] = fail_transaction.request_time
                failDict["arr_time"] = fail_transaction.arrive_time
                failDict["bank"] = fail_transaction.bank
            #     # pendingDict["branch"] =
                failDict["amount"] = fail_transaction.amount
                fail_tran.append(failDict)
            context['fail_tran'] = fail_tran

            # cancelled transaction
            cancelled_tran = []
            for cancelled_transaction in cancelled_trans:
                cancelledDict = {}
                failDict["id"] = cancelled_transaction.user_id_id
                failDict["username"] = CustomUser.objects.get(pk=cancelled_transaction.user_id_id).username
                failDict["payment"] = cancelled_transaction.channel
                failDict["tran_no"] = cancelled_transaction.transaction_id
                failDict["app_time"] = cancelled_transaction.request_time
                failDict["arr_time"] = cancelled_transaction.arrive_time
                failDict["bank"] = cancelled_transaction.bank
            #     # pendingDict["branch"] =
                failDict["amount"] = cancelled_transaction.amount
                cancelled_tran.append(cancelledDict)
            context['cancelled_tran'] = cancelled_tran

            return render(request, 'deposits.html', context)






    # def post(self, request):
    #     post_type = request.POST.get('type')
    #     deposit_channel = request.POST.get('deposit_channel')

    #     if post_type == "getChannelInfo":
    #         # return HttpResponseRedirect(reverse('xadmin:deposit_view', args=[deposit_channel]))
    #         return render(request, 'deposits.html', {'current_deposit_channel': deposit_channel})

