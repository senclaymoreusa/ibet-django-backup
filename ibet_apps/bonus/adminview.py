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
        context['deposit_tiered_amount'] = DEPOSIT_TIERED_AMOUNTS
        context['turnover_tiered_amount'] = [[11, 11], [22, 22], [23, 23]]
        return render(request, "bonus_records.html", context)

        {'name': 'dp_01',
         'start_time': '12/02/2019',
         'end_time': '12/16/2019',
         'issued': True,
         'max_daily_times': '12',
         'max_total_times': '12',
         'max_associated_accounts': '12',
         'max_user': '12',
         'max_user_amount': '2',
         'max_target_user_amount': '2',
         'delivery_method': 'push',
         'status': 1,
         'players': {'target_all': False, 'target_player': ['2'], 'excluded_player': ['1']},
         'requirements': {
            'wager_multiple': [{'product': 'casino', 'multiple': '12', 'time_limit': '22', 'aggregate_method': 0},
                               {'product': 'live-casino', 'multiple': '37', 'time_limit': '22', 'aggregate_method': 0},
                               {'product': 'sports', 'multiple': '-1', 'time_limit': '22', 'aggregate_method': 0},
                               {'product': 'lottery', 'multiple': '-1', 'time_limit': '22', 'aggregate_method': 0}],
            'time_limit': '22',
             'must_have': ['0']
         },
         'type': 'triggered',
         'trigger_type': 'deposit',
         'trigger_subtype': 'first',
         'bonus_amount_list': {'amount_type': 'percentage', 'min_deposit': '23', 'bonus_percentage': '12',
                               'max_bonus_amount': '23'}, 'deposit_wager_base': '0'}

        {'bonus_amount_list': {'amount_type': 'fixed', 'min_deposit': '22'}, 'deposit_wager_base': '1'}

        {'requirements':
             {'wager_multiple':
                  [{'min_deposit': '100', 'bonus_percentage': '20', 'max_bonus_amount': '2000', 'casino_multiple': '12', 'live_casino_multiple': '12', 'sports_multiple': '12', 'lottery_multiple': '12', 'aggregate_method': 0},
                   {'min_deposit': '10000', 'bonus_percentage': '25', 'max_bonus_amount': '12500', 'casino_multiple': '13', 'live_casino_multiple': '13', 'sports_multiple': '13', 'lottery_multiple': '13', 'aggregate_method': 0},
                   {'min_deposit': '50000', 'bonus_percentage': '30', 'max_bonus_amount': '60000', 'casino_multiple': '16', 'live_casino_multiple': '16', 'sports_multiple': '16', 'lottery_multiple': '16', 'aggregate_method': 0},
                   {'min_deposit': '200000', 'bonus_percentage': '35', 'max_bonus_amount': '100000', 'casino_multiple': '20', 'live_casino_multiple': '20', 'sports_multiple': '20', 'lottery_multiple': '20', 'aggregate_method': 0}],
              'time_limit': '23',
              'must_have': ['2']},
         'type': 'triggered',
         'trigger_type': 'deposit',
         'trigger_subtype': 'first',
         'bonus_amount_list': {'amount_type': 'tiered'},
         'deposit_wager_base': '0'}



















