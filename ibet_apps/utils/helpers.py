import decimal
import logging

from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import CustomUser
# from games.views.eagameviews import requestEADeposit
# from games.views.transferwallet import TransferDeposit, TransferWithdraw

logger = logging.getLogger("django")


def addOrWithdrawBalance(username, balance, type_balance):
    user = CustomUser.objects.filter(username=username)
    logger.info("Updating " + user[0].username + " balance (" + type_balance + " " + str(balance) + ")")
    current_balance = user[0].main_wallet

    logger.info(current_balance)
    if type_balance == 'add':
        if user[0].ftd_time is None:
            user.update(ftd_time=timezone.now(), modified_time=timezone.now())
        logger.info("User's current balance is: " + str(current_balance))
        new_balance = current_balance + decimal.Decimal(balance)
        user.update(main_wallet=new_balance, modified_time=timezone.now())
        logger.info("User's new balance is: " + str(new_balance))
        referrer = user[0].referred_by

        if referrer:
            referr_object = get_user_model().objects.filter(username=referrer.username)
            data = Config.objects.all()[0]
            reward_points = referr_object[0].reward_points
            current_points = reward_points + data.Referee_add_balance_reward
            referr_object.update(reward_points=current_points, modified_time=timezone.now())

        # create = Transaction.objects.create(
        #     user_id=CustomUser.objects.filter(username=username).first(),
        #     amount=balance,
        #     transaction_type=0
        # )

        # action = UserAction(
        #     user= CustomUser.objects.filter(username=username).first(),
        #     ip_addr=self.request.META['REMOTE_ADDR'],
        #     event_type=3,
        #     dollar_amount=balance
        # )
        # action.save()
        return True

    else:
        if decimal.Decimal(balance) > current_balance:
            return False

        new_balance = current_balance - decimal.Decimal(balance)
        user.update(main_wallet=new_balance, modified_time=timezone.now())

        # obj, created = Transaction.objects.create(
        #     user_id=CustomUser.objects.filter(username=username).first(),
        #     amount=balance,
        #     transaction_type=1
        # )

        # action = UserAction(
        #     user= CustomUser.objects.filter(username=username).first(),
        #     ip_addr=self.request.META['REMOTE_ADDR'],
        #     event_type=4,
        #     dollar_amount=balance
        # )
        # action.save()
        return True


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip