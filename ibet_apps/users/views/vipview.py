from django.contrib.auth import get_user_model
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views import View
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import timedelta, localtime, now
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth, TruncYear, TruncDate, Coalesce
from django.contrib import messages
from django.shortcuts import render
from django.template.defaulttags import register
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.conf import settings
from dateutil.relativedelta import relativedelta
from django.shortcuts import render_to_response
from decimal import Decimal

from xadmin.views import CommAdminView
from utils.constants import *
from accounting.models import *
from users.models import CustomUser, UserAction, Commission, UserActivity, ReferLink
from operation.models import Notification, NotificationToUsers
from utils.admin_helper import *


import logging
import simplejson as json
import datetime


logger = logging.getLogger('django')


class VIPView(CommAdminView):
    def get(self, request):
        context = super().get_context()
        context['time'] = timezone.now()
        title = "VIP overview"
        context["breadcrumbs"].append(
            {'url': '/vip_overview/', 'title': title})
        context["title"] = title
        return render(request, 'vip/vip_management.html', context)

