from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone
from django.db.models import Q

import datetime

from accounting.models import Transaction
from users.models import CustomUser, WithdrawAccounts
from utils.admin_helper import utcToLocalDatetime
from utils.constants import *
import json
import pytz
import random
import logging

logger = logging.getLogger('django')


def addWithdrawAccount(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = CustomUser.objects.get(pk=data["user_id"])
            name = data.get("full_name")
            if (name):
                user.first_name = name.split(" ")[0]
                user.last_name = name.split(" ")[1]
                user.save()

            new_acc = WithdrawAccounts(
                user=user,
                account_no=data["acc_no"]
            )
            new_acc.save()
            return JsonResponse({
                'success': True,
                'message': "Added new bank account for withdrawal"
            })
        except Exception as e:
            logger.info(repr(e))
            return JsonResponse({
                'success': False,
                'message': "Parameters incorrect or missing"
            })

def get_transactions(request):
    user_id = request.GET.get("user_id")
    trans_type = request.GET.get("type")
    time_from = request.GET.get("time_from")
    time_to = request.GET.get("time_to")
    status = request.GET.get("status")

    if not time_from and not time_to:
        logger.info("Getting transaction history: You have to select start or end date")
        return JsonResponse({
            'success': False,
            'results': "You have to select start or end date"
        })

    try:
        user = CustomUser.objects.get(pk=user_id)
        # DEPOSIT = 0, WITHDRAWAL = 1, TRANSFER = 4, BONUS = 5, ADJUSTMENT = 6, COMMISSION = 7
        transaction_filter = Q(user_id__pk=user_id)
        # transaction_filter = Q()
        if trans_type and trans_type == '0':
            transaction_filter &= Q(transaction_type=TRANSACTION_DEPOSIT)
        elif trans_type and trans_type == '1':
            transaction_filter &= Q(transaction_type=TRANSACTION_WITHDRAWAL)
        elif trans_type and trans_type == '2':
            transaction_filter &= Q(transaction_type=TRANSACTION_TRANSFER)
        elif trans_type and trans_type == '3':
            transaction_filter &= Q(transaction_type=TRANSACTION_BONUS)
        elif trans_type and trans_type == '4':
            transaction_filter &= Q(transaction_type=TRANSACTION_ADJUSTMENT)
        elif trans_type and trans_type == '5':
            transaction_filter &= Q(transaction_type=TRANSACTION_COMMISSION)
        
        # SUCCESS_TYPE = 0  # deposit / withdraw
        # FAIL_TYPE = 1, REJECTED_TYPE = 8  # withdraw # deposit / withdraw
        # PENDING_TYPE = 3, RISK_REVIEW = 9 # withdraw # deposit / withdraw
        # CANCEL_TYPE = 5  # deposit / withdraw
        if status and status == '1': # pedding
            transaction_filter &= (Q(status=TRAN_PENDING_TYPE) | Q(status=TRAN_RISK_REVIEW))
        elif status and status == '2': # fail
            transaction_filter &= (Q(status=TRAN_FAIL_TYPE) | Q(status=TRAN_REJECTED_TYPE))
        elif status and status == '0': # success
            transaction_filter &= (Q(status=TRAN_SUCCESS_TYPE))
        elif status and status == '3':  #cancel
            transaction_filter &= (Q(status=TRAN_CANCEL_TYPE))

        current_tz = timezone.get_current_timezone()
        tz = pytz.timezone(str(current_tz))

        if time_from:
            time_from = datetime.datetime.strptime(time_from, '%m/%d/%Y')
            min_time_from = tz.localize(datetime.datetime.combine(time_from, datetime.time.min)) 
            transaction_filter &= Q(request_time__gt=min_time_from)

        if time_to:
            time_to= datetime.datetime.strptime(time_to, '%m/%d/%Y')
            max_time_to = tz.localize(datetime.datetime.combine(time_to, datetime.time.max))  
            transaction_filter &= Q(request_time__lt=max_time_to)
            

        all_transactions = Transaction.objects.filter(transaction_filter).order_by('-request_time')

        trans_data = []
        for tran in all_transactions:
            data = dict()
            data["transaction_id"] = tran.transaction_id
            data["request_time"] = tran.request_time
            data["transaction_type"] = tran.get_transaction_type_display()
            data["channel"] = tran.get_channel_display()
            data["amount"] = tran.amount
            data["balance"] = tran.current_balance
            data["status"] = tran.get_status_display()
            trans_data.append(data)
        # res = serializers.serialize('json', all_transactions)
        logger.info("Successfully get transaction history")
        return JsonResponse({
            'success': True,
            'results': trans_data,
            'full_raw_data': list(all_transactions.values())
        })
    except Exception as e:
        logger.error("(Error) Getting transaction history error: ", e)
        return JsonResponse({
            'success': False,
            'error_message': "There is something wrong"
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
        status = 2 if data['type'] == 0 else 3
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

def get_transaction_by_id(request):
    if request.method == "GET":
        transaction_id = request.GET.get("transaction_id")

        try:
            tran = Transaction.objects.get(transaction_id=transaction_id)
            
            trans_data = {
                'transaction_id': tran.transaction_id,
                'amount': tran.amount,
                'balance': tran.current_balance,
                'currency': tran.get_currency_display(),
                'request_time': tran.request_time,
                'transaction_type':  tran.get_transaction_type_display(),
                'channel':  tran.get_channel_display(),
                'status':  tran.get_status_display()
            }

            return JsonResponse({
                'success': True,
                'results': trans_data
            })

        except Exception as e:
            logger.error(repr(e))
            return JsonResponse({
                'success': False,
                'results': "There is something wrong"
            })
