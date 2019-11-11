from django.http import HttpResponse
from django.shortcuts import render
from xadmin.views import CommAdminView

from bonus.models import *
from utils.constants import *
from utils.admin_helper import *

class BonusRecordsView(CommAdminView):

    def get(self, request):
        context = super().get_context()
        context["breadcrumbs"].append("Bonuses / Bonus records")
        context['time'] = timezone.now()
        context['bonuses_types'] = BONUS_TYPE_CHOICES
        context['bonuses_status'] = BONUS_STATUS_CHOICES
        return render(request, "bonus_records.html", context)
