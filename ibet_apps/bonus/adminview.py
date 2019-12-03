from django.http import HttpResponse
from django.shortcuts import render
from xadmin.views import CommAdminView

from bonus.models import *
from games.models import GameProvider
from utils.constants import *
from utils.admin_helper import *


class BonusRecordsView(CommAdminView):

    def get(self, request):
        context = super().get_context()
        context["breadcrumbs"].append("Bonuses / Bonus records")
        context['time'] = timezone.now()
        context['bonuses_types'] = BONUS_TYPE_CHOICES
        context['bonuses_status'] = BONUS_STATUS_CHOICES
        context['game_provider'] = GameProvider.objects.all()
        context['groups'] = UserGroup.objects.all()
        return render(request, "bonus_records.html", context)

    def post(self, request):
        post_type = request.POST.get("type")

        if post_type == "newBonus":
            print("in")
            bonus_dict = request.POST.get("bonusDict")
            print(bonus_dict)
            return HttpResponse(status=200)
