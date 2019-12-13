from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone

from accounting.models import Transaction
from users.models import CustomUser
import json

import random

def get_transactions(request):
    user = CustomUser.objects.get(username=request.GET["userid"])
    all_transactions = Transaction.objects.filter(user_id=user.id).order_by('-request_time')
    # res = serializers.serialize('json', all_transactions)
    return JsonResponse({
        'results': list(all_transactions.values())
    })

def save_transaction(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = CustomUser.objects.get(pk=request.user.pk)
        txn_id = request.user.username+"-"+timezone.datetime.today().isoformat()+"-"+str(random.randint(0, 10000000))
        bank_info = {
            'bank': data['bank'],
            'bank_acc_no': data['bank_acc_no'],
            'real_name': data['real_name']
        }
        status = 2
        if data['type'] == 0:
            status = 3
        try:

            txn = Transaction(
                transaction_id=txn_id,
                user_id=user,
                amount=data['amount'],
                currency=data['currency'],
                method="Local Bank Transfer",
                transaction_type=data['type'],
                bank_info=bank_info,
                channel=11, # 11 = LBT
                status=status
            )
            txn.save()
            return JsonResponse({
                'success': True,
                'transaction_id': txn_id
            })
        except Exception as e:
            logger.error(repr(e))
            return JsonResponse({
                'success': False,
                'transaction_id': None
            })
        