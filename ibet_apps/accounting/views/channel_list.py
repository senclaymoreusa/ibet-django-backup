from django.shortcuts import render, get_object_or_404
from xadmin.views import CommAdminView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.template.loader import render_to_string
from django.core import exceptions

from accounting.models import *
from users.models import CustomUser

import simplejson as json
import datetime
from django.core import serializers
from django.utils.timezone import timedelta

from utils.constants import *


class ChannelListView(CommAdminView):
    def get(self, request):
        get_type = request.GET.get("type")

        if get_type == "getChannelInfo":
            deposit_channel = request.GET.get("current_deposit_channel")
            current_channel_obj = DepositChannel.objects.get(pk=deposit_channel)
            context = super().get_context()
            context[
                "current_channel_name"
            ] = current_channel_obj.get_thirdParty_name_display()

            response_data = {
                "channel_id": deposit_channel,
                "name": current_channel_obj.get_thirdParty_name_display(),
                "channel_status": current_channel_obj.get_switch_display(),
                "min_deposit": current_channel_obj.min_amount,
                "max_deposit": current_channel_obj.max_amount,
                "transaction_fee": current_channel_obj.transaction_fee,
                "volumn": current_channel_obj.volume,
                "limit_access": current_channel_obj.limit_access,
            }
            return HttpResponse(
                json.dumps(response_data), content_type="application/json"
            )

        else:
            context = super().get_context()
            title = "Payment methods"
            context["breadcrumbs"].append({"url": "/deposit/", "title": title})
            context["title"] = title

            # CHANNEL
            depositChannel = DepositChannel.objects.all()
            # PENDING
            pending_trans = Transaction.objects.filter(
                Q(status=tran_pending_type) & Q(transaction_type=0)
            )
            # SUCCESS
            success_trans = Transaction.objects.filter(
                Q(status=tran_success_type) & Q(transaction_type=0)
            )
            # FAILED
            fail_trans = Transaction.objects.filter(
                Q(status=tran_fail_type) & Q(transaction_type=0)
            )
            # CANCELLED
            cancelled_trans = Transaction.objects.filter(
                Q(status=tran_cancel_type) & Q(transaction_type=0)
            )

            # channels
            channel_data = []
            for channel in depositChannel:
                depositDict = {}
                depositDict["channel_id"] = channel.pk
                depositDict["channel_name"] = channel.get_thirdParty_name_display()
                depositDict["min_deposit"] = channel.min_amount
                depositDict["max_deposit"] = channel.max_amount
                depositDict["fee"] = channel.transaction_fee
                depositDict["volume"] = channel.volume
                depositDict["new_users_volume"] = channel.new_user_volume
                # depositDict["blocked_risk_level"] = channel.blocked_risk_level
                depositDict["status"] = channel.get_switch_display()
                channel_data.append(depositDict)
            context["channel_data"] = channel_data
            return render(request, "channels.html", context)

    def post(self, request):
        post_type = request.POST.get("type")

        if post_type == "deleteChannel":
            deposit_channel = request.POST.get("deposit_channel")
            # find choice label from choice value
            deposit_channel_label = None
            for channel_id, name in CHANNEL_CHOICES:
                if name == deposit_channel:
                    deposit_channel_label = str(channel_id)
                    break
            delete_channel = get_object_or_404(
                DepositChannel, thirdParty_name=deposit_channel_label
            )
            delete_channel.delete()
            return HttpResponseRedirect(reverse("xadmin:channel_list"))

        elif post_type == "edit_channel_detail":
            channel_id = request.POST.get("channel_id_number")
            channel_status = request.POST.get("channel_status")

            min_deposit = request.POST.get("min_deposit")
            max_deposit = request.POST.get("max_deposit")

            transaction_fee = request.POST.get("transaction_fee")
            volumn = request.POST.get("volumn")
            limit_access = request.POST.get("limit_access")
            new_user_volumn = request.POST.get("new_user_volumn")

            DepositChannel.objects.filter(pk=channel_id).update(
                min_amount=min_deposit,
                max_amount=max_deposit,
                transaction_fee=transaction_fee,
                switch=channel_status,
            )

            return HttpResponseRedirect(reverse("xadmin:channel_list"))
