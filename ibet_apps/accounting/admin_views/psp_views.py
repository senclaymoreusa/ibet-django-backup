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


class PaymentConfig(CommAdminView):
    def get(self, request):
        context = super().get_context()
        title = "Payment Configuration"
        context["breadcrumbs"].append({"title": title})
        context["title"] = title
        context["time"] = timezone.now()

        deposit_psp = DepositChannel.objects.all()
        # withdraw_psp = WithdrawChannel.objects.all()
        context["suppliers"] = deposit_psp
        # print(context["suppliers"])

        return render(request, "channels.html", context)
