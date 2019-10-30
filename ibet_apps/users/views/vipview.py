from django.http import HttpResponse
from django.views import View
from django.utils import timezone
from django.shortcuts import render
from xadmin.views import CommAdminView

import logging
import simplejson as json
import datetime


logger = logging.getLogger('django')


class VIPView(CommAdminView):
    def get(self, request):
        get_type = request.GET.get("type")
        if get_type == "getVIPInfo":
            response_data ={}
            return HttpResponse(
                json.dumps(response_data), content_type="application/json"
            )
        else:
            context = super().get_context()
            context['time'] = timezone.now()
            title = "VIP overview"
            context["breadcrumbs"].append({'title': title})
            context["title"] = title
            return render(request, 'vip/vip_management.html', context)

