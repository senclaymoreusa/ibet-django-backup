from django.shortcuts import render
from xadmin.views import CommAdminView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy

from accounting.models import Transaction, DepositAccessManagement, DepositChannel, WithdrawAccessManagement, WithdrawChannel


class DepositView(CommAdminView): 
    def get(self, request):
        context = super().get_context()
        title = 'Deposits'
        context["breadcrumbs"].append({'url': '/deposit/', 'title': title})
        context['title'] = title

        # variables
        depositChannel = DepositChannel.objects.all()


        # channels
        channel_data = []
        for channel in depositChannel:
            depositDict = {}
            # context["channel"] = channel.



        return render(request, 'deposits.html', context)
