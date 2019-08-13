import decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import CustomUser


def addOrWithdrawBalance(username, balance, type_balance):
    user = CustomUser.objects.filter(username=username)

    currrent_balance = user[0].main_wallet
    # if balance.isdigit() == False:
    #     return HttpResponse('Failed')

    if type_balance == 'add':
        if user[0].ftd_time is None:
            user.update(ftd_time=timezone.now(), modified_time=timezone.now())

        new_balance = currrent_balance + decimal.Decimal(balance)
        user.update(main_wallet=new_balance, modified_time=timezone.now())
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
        if decimal.Decimal(balance) > currrent_balance:
            return HttpResponse('The balance is not enough', status=200)

        new_balance = currrent_balance - decimal.Decimal(balance)
        user.update(main_wallet=new_balance, modified_time=timezone.now())

        obj, created = Transaction.objects.create(
            user_id=CustomUser.objects.filter(username=username).first(),
            amount=balance,
            transaction_type=1
        )

        # action = UserAction(
        #     user= CustomUser.objects.filter(username=username).first(),
        #     ip_addr=self.request.META['REMOTE_ADDR'],
        #     event_type=4,
        #     dollar_amount=balance
        # )
        # action.save()
        return created