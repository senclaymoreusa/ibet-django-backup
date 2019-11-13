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
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    except Exception as e:
        print(repr(e))


def des_encode(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    cipher_text = cipher.encrypt(data)
    return cipher_text

def generateHash(message):
    hash = hashlib.sha256(message.encode('utf-8')).hexdigest()
    return hash


def transferRequest(user, amount, from_wallet, to_wallet):
    if from_wallet == "main":
        transfer_to = TransferDeposit(user, amount, from_wallet)
        function_name = to_wallet + 'Deposit'
        status = getattr(transfer_to, function_name)()
        if status == CODE_SUCCESS:
            field_name = to_wallet + '_wallet'
            user.main_wallet -= Decimal(float(amount))
            old_amount = getattr(user, field_name)
            new_amount = old_amount + amount
            setattr(user, field_name, new_amount)
            user.save()
            logger.info("main wallet transfer to " + str(to_wallet))
            return True

        logger.info("Fail transfer money from main to " + str(to_wallet))
        return False

    else:
        transfer_from = TransferWithdraw(user, amount, to_wallet)
        function_name = from_wallet + 'Withdraw'
        status = getattr(transfer_from, function_name)()
        if status == CODE_SUCCESS:

            from_field_name = from_wallet + '_wallet'
            from_old_amount = getattr(user, from_field_name)
            from_new_amount = from_old_amount - Decimal(float(amount))
            setattr(user, from_field_name, from_new_amount)

            if to_wallet == "main":
                old_amount = user.main_wallet
                user.main_wallet = old_amount + Decimal(float(amount))
                user.save()
                logger.info("Transfer money from " + str(to_wallet) + "to main")
                return True
            else:
                transfer_to = TransferDeposit(user, amount, from_wallet)
                function_name = to_wallet + 'Deposit'
                status = getattr(transfer_to, function_name)()
                if status == CODE_SUCCESS:
                    to_field_name = to_wallet + '_wallet'
                    to_old_amount = getattr(user, to_field_name)
                    to_new_amount = to_old_amount + Decimal(float(amount))
                    setattr(user, to_field_name, to_new_amount)
                    user.save()
                    logger.info("Transfer money from " + str(from_wallet) + " to " + str(to_wallet))
                    return True
                else:
                    function_name = from_wallet + 'Deposit'
                    status = getattr(transfer_to, function_name)()
                    if status == CODE_SUCCESS:
                        from_field_name = from_wallet + '_wallet'
                        from_old_amount = getattr(user, from_field_name)
                        from_new_amount = from_old_amount + Decimal(float(amount))
                        setattr(user, from_field_name, from_new_amount)
                        user.save()
                        logger.info("Fail transfer money from " + str(from_wallet) + " to " + str(to_wallet))
                        return False
        user.save()
        return False