from django.shortcuts import render
from django.urls import reverse
from xadmin.views import CommAdminView
from django.http import HttpResponse

from django.utils import timezone

import simplejson as json
import logging
import requests

logger = logging.getLogger("django")


def get_bonus():
    url = 'http://bonus/api/bonuses/'
    r = requests.get(url)
    bonus = r.json()
    print(bonus)
    return bonus

class BonusRecordView(CommAdminView):
    def get(self, request, *args, **kwargs):
        context = super().get_context()
        context["breadcrumbs"].append("Bonus records")
        context['time'] = timezone.now()

        return render(request, "bonus_records.html", context)
