import decimal
import logging

from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import CustomUser
# from games.views.eagameviews import requestEADeposit
# from games.views.transferwallet import TransferDeposit, TransferWithdraw
from games.transferwallet import TransferDeposit, TransferWithdraw
from utils.constants import *
from decimal import Decimal

logger = logging.getLogger("django")


"""
:param request: Http request in API views
:returns: IPv4 address
"""
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def des_encode(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    cipher_text = cipher.encrypt(data)
    return cipher_text

def generateHash(message):
    hash = hashlib.sha256(message.encode('utf-8')).hexdigest()
    return hash



def transferRequest(user, amount, from_wallet, to_wallet):
    
    # print(user, amount, from_wallet, to_wallet)
    # print(user.main_wallet)
    if from_wallet == "main":
        tranfer_to = TransferDeposit(user, amount, from_wallet)
        funcion_name = to_wallet + 'Deposit'
        status = getattr(tranfer_to, funcion_name)()
        if status == CODE_SUCCESS:
            field_name = to_wallet + '_wallet'
            user.main_wallet -= amount
            old_amount = getattr(user, field_name)
            new_amount = old_amount + amount
            setattr(user, field_name, new_amount)
        else:
            user.main_wallet = user.main_wallet - Decimal(float(amount))
        user.save()

    else:
        tranfer_from = TransferWithdraw(user, amount, to_wallet)
        funcion_name = from_wallet + 'Withdraw'
        status = getattr(tranfer_from, funcion_name)()
        if status == CODE_SUCCESS:

            from_field_name = from_wallet + '_wallet'
            from_old_amount = getattr(user, from_field_name)
            from_new_amount = from_old_amount - Decimal(float(amount))
            setattr(user, from_field_name, from_new_amount)

            if to_wallet == "main":
                old_amount = user.main_wallet
                # print("old amount :" + str(old_amount))
                user.main_wallet = old_amount + Decimal(float(amount))
                # print("new amount :" + str(user.main_wallet))
                
            else:
                tranfer_to = TransferDeposit(user, amount, from_wallet)
                funcion_name = to_wallet + 'Deposit'
                status = getattr(tranfer_to, funcion_name)()
                if status == CODE_SUCCESS:
                    to_field_name = to_wallet + '_wallet'
                    to_old_amount = getattr(user, to_field_name)
                    to_new_amount = to_old_amount + Decimal(float(amount))
                    setattr(user, to_field_name, to_new_amount)

                else:
                    funcion_name = from_wallet + 'Deposit'
                    getattr(tranfer_to, funcion_name)()
                    from_field_name = from_wallet + '_wallet'
                    from_old_amount = getattr(user, from_field_name)
                    from_new_amount = from_old_amount + Decimal(float(amount))
                    setattr(user, from_field_name, from_new_amount)

            user.save()