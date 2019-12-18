from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers
from rest_framework import status
from xadmin.views import CommAdminView

from bonus.models import *
from games.models import GameProvider
from utils.constants import *
from utils.admin_helper import *

logger = logging.getLogger('django')


class BonusRecordsView(CommAdminView):

    def get(self, request):
        context = super().get_context()
        context["breadcrumbs"].append("Bonuses / Bonus records")
        context['time'] = timezone.now()
        context['bonuses_types'] = BONUS_TYPE_CHOICES
        context['bonuses_status'] = BONUS_STATUS_CHOICES
        context['game_provider'] = GameProvider.objects.all()
        context['groups'] = UserGroup.objects.all()
        context['must_have'] = BONUS_MUST_HAVE
        return render(request, "bonus_records.html", context)


class BonusTransactionsView(CommAdminView):

    def get(self, request):
        context = super().get_context()
        context["breadcrumbs"].append("Bonuses / Bonus transactions")
        context['time'] = timezone.now()
        context['bonuses_types'] = BONUS_TYPE_CHOICES
        context['bonuses_status'] = USER_BONUS_EVENT_TYPE_CHOICES
        return render(request, "bonus_transactions.html", context)
