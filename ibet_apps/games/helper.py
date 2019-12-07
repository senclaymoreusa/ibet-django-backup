import decimal
import logging
import uuid

from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import CustomUser, UserWallet
from games.models import GameProvider
# from games.views.eagameviews import requestEADeposit
# from games.views.transferwallet import TransferDeposit, TransferWithdraw
from games.transferwallet import TransferDeposit, TransferWithdraw
from django.db import IntegrityError, transaction
from utils.constants import *
from decimal import Decimal
from pyDes import des, CBC, PAD_PKCS5
from datetime import datetime

import base64, hashlib
import random

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
    success = False
    if from_wallet == "main":

        try:
            with transaction.atomic():
                user.main_wallet -= Decimal(float(amount))
                user.save()
                print("main wallet transfer to " + str(to_wallet))
                logger.info("main wallet transfer to " + str(to_wallet))
                to_provider = GameProvider.objects.get(provider_name=to_wallet)
                wallet, created = UserWallet.objects.get_or_create(user=user, provider=to_provider)
                wallet.wallet_amount = wallet.wallet_amount + Decimal(float(amount))
                wallet.save()
                success = True
        
        except IntegrityError:
            print("Save data to database error when transfer money from main wallet to " + str(to_wallet))
            logger.error("Save data to database error when transfer money from main wallet to " + str(to_wallet))
            success = False
        
        if success:
            transfer_to = TransferDeposit(user, amount, from_wallet)
            function_name = to_wallet + 'Deposit'
            status = getattr(transfer_to, function_name)()
            if status != CODE_SUCCESS:
                field_name = to_wallet + '_wallet'
                try:
                    with transaction.atomic():
                        user.main_wallet += Decimal(float(amount))
                        # old_amount = getattr(user, field_name)
                        # new_amount = old_amount + amount
                        # setattr(user, field_name, new_amount)
                        user.save()
                        logger.info("main wallet transfer to " + str(to_wallet))
                        to_provider = GameProvider.objects.get(provider_name=to_wallet)
                        to_wallet_obj, created = UserWallet.objects.get_or_create(user=user, provider=to_provider)
                        to_wallet_obj.wallet_amount = to_wallet_obj.wallet_amount - Decimal(float(amount))
                        to_wallet_obj.save()
                        logger.info("Rollback database because fail to transfer money from main wallet to " + str(to_wallet))
                        return False
                except IntegrityError:
                    logger.error("Save data to database error when transfer money from main wallet to " + str(to_wallet))
                    return False
            else:
                return True
        else:
            return False

        # logger.info("Fail transfer money from main to " + str(to_wallet))
        # return False

    else:
        
        if to_wallet == "main":

            try:
                with transaction.atomic():
                    user.main_wallet += Decimal(float(amount))
                    user.save()

                    from_provider = GameProvider.objects.get(provider_name=from_wallet)
                    from_wallet_obj, created = UserWallet.objects.get_or_create(user=user, provider=from_provider)
                    from_wallet_obj.wallet_amount = from_wallet_obj.wallet_amount - Decimal(float(amount))
                    from_wallet_obj.save()
                    success = True

            except IntegrityError:
                    logger.error("Save data to database error when transfer money from " + str(from_wallet) + "to main wallet" )
                    success = False
            
            if success:
                transfer_from = TransferWithdraw(user, amount, to_wallet)
                function_name = from_wallet + 'Withdraw'
                status = getattr(transfer_from, function_name)()
                if status != CODE_SUCCESS:
                    try:
                        with transaction.atomic():
                            user.main_wallet -= Decimal(float(amount))
                            user.save()

                            from_provider = GameProvider.objects.get(provider_name=from_wallet)
                            from_wallet_obj, created = UserWallet.objects.get_or_create(user=user, provider=from_provider)
                            from_wallet_obj.wallet_amount = from_wallet_obj.wallet_amount + Decimal(float(amount))
                            from_wallet_obj.save()
                            logger.info("Rollback database because fail to transfer money from " + str(from_wallet) + "to main wallet")
                            return False
                    except IntegrityError:
                        logger.error("Save data to database error when transfer money from " + str(to_wallet) + "to main wallet")
                        return False
                return True
            else:
                return False

        else:

            try:
                with transaction.atomic():
                    from_provider = GameProvider.objects.get(provider_name=from_wallet)
                    from_wallet_obj, created = UserWallet.objects.get_or_create(user=user, provider=from_provider)
                    from_wallet_obj.wallet_amount = from_wallet_obj.wallet_amount - Decimal(float(amount))
                    from_wallet_obj.save()

                    to_provider = GameProvider.objects.get(provider_name=to_wallet)
                    to_wallet_obj, created = UserWallet.objects.get_or_create(user=user, provider=to_provider)
                    to_wallet_obj.wallet_amount = to_wallet_obj.wallet_amount + Decimal(float(amount))
                    to_wallet_obj.save()
                    success = True
                    
            except IntegrityError:
                logger.error("Save data to database error when transfer money from " + str(from_wallet) + "to "  + str(from_wallet))
                return False
                    
            if success:
                transfer_from = TransferWithdraw(user, amount, to_wallet)
                function_name = from_wallet + 'Withdraw'
                from_status = getattr(transfer_from, function_name)()

                if from_status != CODE_SUCCESS:

                    try:
                        with transaction.atomic():
                            
                            from_provider = GameProvider.objects.get(provider_name=from_wallet)
                            from_wallet_obj, created = UserWallet.objects.get_or_create(user=user, provider=from_provider)
                            from_wallet_obj.wallet_amount = from_wallet_obj.wallet_amount + Decimal(float(amount))
                            from_wallet_obj.save()
                            
                            to_provider = GameProvider.objects.get(provider_name=to_wallet)
                            to_wallet_obj, created = UserWallet.objects.get_or_create(user=user, provider=to_provider)
                            to_wallet_obj.wallet_amount = to_wallet_obj.wallet_amount - Decimal(float(amount))
                            to_wallet_obj.save()
                            logger.error("Withdraw request: Fail to transfer money from " + str(from_wallet) + " to "  + str(to_wallet) + ", and wallets already rollback")
                            return False
                    
                    except IntegrityError:
                        logger.error("Rollback database because fail to transfer money from " + str(from_wallet) + "to "  + str(to_wallet))
                        return False
                    
                else:
                    
                    transfer_to = TransferDeposit(user, amount, to_wallet)
                    function_name = to_wallet + 'Deposit'
                    to_status = getattr(transfer_to, function_name)()
                    # withdraw success from from_wallet but fail deposit from to_wallet
                    if to_status != CODE_SUCCESS:

                        try:
                            with transaction.atomic():

                                user.main_wallet += Decimal(float(amount))
                                logger.info("Fail to request deposit " + str(to_wallet) + " , and save the amount to main wallet")
                                user.save()

                                to_provider = GameProvider.objects.get(provider_name=to_wallet)
                                to_wallet_obj, created = UserWallet.objects.get_or_create(user=user, provider=to_provider)
                                to_wallet_obj.wallet_amount = to_wallet_obj.wallet_amount - Decimal(float(amount))
                                to_wallet_obj.save()
                                logger.error("Deposit request: Fail to transfer money from " + str(from_wallet) + " to "  + str(to_wallet) + ", and wallets already rollback")
                                return False
                        
                        except IntegrityError:
                            logger.error("Rollback database because fail to transfer money from " + str(from_wallet) + " to "  + str(to_wallet))
                            return False
                    
                    return True
            else:
                return False



def des_decrypt(s):
    encrypt_key = SA_ENCRYPT_KEY
    iv = encrypt_key
    k = des(encrypt_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(base64.b64decode(s), padmode=PAD_PKCS5)
    return de

def MD5(code):
    res = hashlib.md5(code.encode()).hexdigest()
    return res

def generateTxnId():
    now = datetime.now()
    return str(random.randint(0, 100)) + str(now.year) + str(now.month) + str(now.day) + str(now.second)