from django.shortcuts import render, get_object_or_404
from xadmin.views import CommAdminView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.template.loader import render_to_string
from django.core import exceptions
from decimal import Decimal

from accounting.models import *
from users.models import CustomUser

import simplejson as json
import logging
from django.core import serializers
from django.utils.timezone import timedelta

from utils.constants import *
from itertools import chain

logger = logging.getLogger("django")


class ChannelListView(CommAdminView):
    def get(self, request):
        get_type = request.GET.get("type")

        if get_type == "getChannelInfo":
            channel = request.GET.get("current_channel")
            context = super().get_context()
            
            if DepositChannel.objects.filter(pk=channel).exists():
                current_channel = DepositChannel.objects.get(pk=channel)
                current_type = "Deposit"
            else:
                current_channel = WithdrawChannel.objects.get(pk=channel)
                current_type = "Withdraw"
                   
            context[
                "current_channel_name"
            ] = current_channel.get_thirdParty_name_display()
            logger.info('Get Channel ' + str(context["current_channel_name"]) + ' info')

            response_data = {
                "channel_id": str(current_channel),
                "name": current_channel.get_thirdParty_name_display(),
                "channel_status": current_channel.get_switch_display(),
                "min_deposit": str(current_channel.min_amount),
                "max_deposit": current_channel.max_amount,
                "transaction_fee": current_channel.transaction_fee,
                "transaction_fee_per": current_channel.transaction_fee_per,
                "volume": current_channel.volume,
                "new_user_volume": current_channel.new_user_volume,
                "limit_access": current_channel.limit_access,
                # methods part
                "method": current_channel.method,
                "type": current_type,
                "channel": current_channel.get_thirdParty_name_display(),
                "market": current_channel.get_market_display(),
                "supplier": current_channel.supplier
            }
            logger.info('Append Channel ' + str(context["current_channel_name"]) + ' details')
            return HttpResponse(
                json.dumps(response_data, default=decimal_default), content_type="application/json"
            )

        else:
            context = super().get_context()
            title = "Finance / Payment methods"
            context["breadcrumbs"].append({"url": "/deposit/", "title": title})
            context['time'] = timezone.now()

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
                channelDict["supplier"] = channel.supplier
                try:
                    channel._meta.get_field('deposit_channel')
                    channelDict["type"] = "Deposit"
                except models.FieldDoesNotExist:
                    channelDict["type"] = "Withdrawal"
                    
                channelDict["market"] = channel.get_market_display()
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
            context["markets_choices"] = MARKET_CHOICES
            context["types_choices"] = ("Deposit", "Withdrawal")
            context["status_choices"] = THIRDPARTY_STATUS_CHOICES
            return render(request, "channels.html", context)

    def post(self, request):
        post_type = request.POST.get("type")

        if post_type == "edit_channel_detail":
            channel_id = request.POST.get("channel_id_number")
            channel_status = request.POST.get("channel_status")

            min_deposit = request.POST.get('min_deposit')
            max_deposit = request.POST.get("max_deposit")

            transaction_fee = request.POST.get("transaction_fee")
            transaction_fee_per = request.POST.get("transaction_fee_per")
            volume = request.POST.get("volume")
            if str(request.POST.get("limit_access_yes")) == "on":
                limit_access = True
            else:
                limit_access = False
            new_user_volume = request.POST.get("new_user_volume")

            if DepositChannel.objects.filter(pk=channel_id).exists():
                channel = DepositChannel.objects.filter(pk=channel_id)
            else:
                channel = WithdrawChannel.objects.filter(pk=channel_id)

            if min_deposit == '':
                return JsonResponse({ "code": 1, "message": "Please Fill MINIMUM DEPOSIT"})
            elif max_deposit == '':
                return JsonResponse({ "code": 1, "message": "Please Fill MAXIMUM DEPOSIT"})
            elif transaction_fee == '':
                return JsonResponse({ "code": 1, "message": "Please Fill TRANSACTION FEE"})
            elif transaction_fee_per == '':
                return JsonResponse({ "code": 1, "message": "Please Fill TRANSACTION FEE PERCENTAGE"})
            elif volume == '':
                return JsonResponse({ "code": 1, "message": "Please Fill VOLUME"})
            elif new_user_volume == '':
                return JsonResponse({ "code": 1, "message": "Please Fill NEW USER VOLUME"})
            else:
                channel.update(
                    min_amount=min_deposit,
                    max_amount=max_deposit,
                    transaction_fee=transaction_fee,
                    transaction_fee_per=transaction_fee_per,
                    switch=channel_status,
                    limit_access = limit_access,
                    new_user_volume = new_user_volume,
                    volume = volume, 
                )
                logger.info("Update Channel '%s' details" % channel)
                return HttpResponseRedirect(reverse("xadmin:channel_list"))
            # Delete Channel
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
            
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    logger.info(TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__))
        

