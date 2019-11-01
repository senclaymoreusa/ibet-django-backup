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


class ModifyWithdrawal(CommAdminView):
    def post(self, request):
        txn_num = request.POST.get()
        pass

def myconverter(o):
    if isinstance(o, timezone.date):
        return o.__str__()