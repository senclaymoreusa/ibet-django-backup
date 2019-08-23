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
from itertools import chain



class ChannelListView(CommAdminView):
    def get(self, request):
        get_type = request.GET.get("type")

        if get_type == "getChannelInfo":
            channel = request.GET.get("current_channel")
            context = super().get_context()
            
            current_channel = DepositChannel.objects.get(pk=channel)
            current_type = "Deposit"
            if current_channel is None:
                current_channel = WithdrawChannel.objects.get(pk=channel)
                current_type = "Withdraw"
                   
            context[
                "current_channel_name"
            ] = current_channel.get_thirdParty_name_display()

            response_data = {
                "channel_id": str(current_channel),
                "name": current_channel.get_thirdParty_name_display(),
                "channel_status": current_channel.get_switch_display(),
                "min_deposit": current_channel.min_amount,
                "max_deposit": current_channel.max_amount,
                "transaction_fee": current_channel.transaction_fee,
                "volumn": current_channel.volume,
                "limit_access": current_channel.limit_access,
                # methods part
                "method": current_channel.method,
                "type": current_type,
                "channel": current_channel.get_thirdParty_name_display(),
                "market": "market",
                "supplier": "supplier"
            }
            return HttpResponse(
                json.dumps(response_data), content_type="application/json"
            )
        elif get_type == "channel_filter":
            print("get")

        else:
            context = super().get_context()
            title = "Finance / Payment methods"
            context["breadcrumbs"].append({"url": "/deposit/", "title": title})

            # CHANNEL
            depositChannel = DepositChannel.objects.all()
            withdrawChannel = WithdrawChannel.objects.all()
            channels = list(chain(depositChannel, withdrawChannel))

            # channels
            channel_data = []
            for channel in channels:
                channelDict = {}
                channelDict["id"] = channel.pk
                channelDict["method"] = channel.method
                channelDict["channel"] = channel.get_thirdParty_name_display()
                channelDict["supplier"] = "supplier"
                try:
                    channel._meta.get_field('deposit_channel')
                    channelDict["type"] = "Deposit"
                except models.FieldDoesNotExist:
                    channelDict["type"] = "Withdrawal"
                    
                channelDict["market"] = "market"
                channelDict["min"] = channel.min_amount
                channelDict["max"] = channel.max_amount
                channelDict["flat_fee"] = "flat fee"
                channelDict["fee"] = channel.transaction_fee
                channelDict["volume"] = channel.volume
                channelDict["require"] = "require"
                channelDict["vip_level"] = "vip level"
                channelDict["risk_level"] = channel.get_block_risk_level_display()
                channelDict["new_users_volume"] = channel.new_user_volume
                channelDict["status"] = channel.get_switch_display()
                channel_data.append(channelDict)
            context["channel_data"] = channel_data
            return render(request, "channels.html", context)

    def post(self, request):
        post_type = request.POST.get("type")

        if post_type == "edit_channel_detail":
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

        # elif post_type == "deleteChannel":
        #     deposit_channel = request.POST.get("deposit_channel")
        #     # find choice label from choice value
        #     deposit_channel_label = None
        #     for channel_id, name in CHANNEL_CHOICES:
        #         if name == deposit_channel:
        #             deposit_channel_label = str(channel_id)
        #             break
        #     delete_channel = get_object_or_404(
        #         DepositChannel, thirdParty_name=deposit_channel_label
        #     )
        #     delete_channel.delete()
            return HttpResponseRedirect(reverse("xadmin:channel_list"))

        

