from django.shortcuts import render

from table.views import FeedDataView
from accounting.tables import DepositTable

class DepositView(FeedDataView):

    token = DepositTable.token

    def get_queryset(self):
        return super(DepositView, self).get_queryset()

    def people(request):
        return render(request, "index.html", {'deposit': get_queryset()})