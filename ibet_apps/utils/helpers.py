import decimal
import logging

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import DatabaseError, transaction
from django.core.exceptions import ObjectDoesNotExist
from users.models import CustomUser, Config

logger = logging.getLogger("django")


def addOrWithdrawBalance(username, balance, type_balance):
    try:
        user = CustomUser.objects.get(username=username)

        logger.info("Updating " + user.username + " balance (" + type_balance + " " + str(balance) + ")")
        current_balance = user.main_wallet

        logger.info(current_balance)
        with transaction.atomic():
            if type_balance == 'add':
                if user.ftd_time is None:
                    user.ftd_time = timezone.now()
                    user.modified_time = timezone.now()
                    
                logger.info("User's current balance is: " + str(current_balance))
                new_balance = current_balance + decimal.Decimal(balance)
                user.main_wallet = new_balance
                user.modified_time = timezone.now()
                referrer = user.referred_by

                logger.info("User's new balance is: " + str(new_balance))

                if referrer:
                    referr_object = get_user_model().objects.filter(username=referrer.username)
                    data = Config.objects.all()[0]
                    reward_points = referr_object[0].reward_points
                    current_points = reward_points + data.Referee_add_balance_reward
                    referr_object.update(reward_points=current_points, modified_time=timezone.now())

                user.save()
                return True
            else:
                if decimal.Decimal(balance) > current_balance:
                    return False

                new_balance = current_balance - decimal.Decimal(balance)
                user.main_wallet=new_balance
                user.modified_time=timezone.now()
                user.save()
                return True

    except (Exception, ObjectDoesNotExist) as e:
        logger.critical("FATAL__ERROR::addOrWithdrawBalance::Unable to update user's balance", exc_info=1)
        logger.error(repr(e))
        # logger.error(f"user {username} does not exist")
        return False


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip