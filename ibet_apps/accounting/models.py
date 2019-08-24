from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from utils.constants import *

# from users.models import CustomUser

import uuid


class Bank(models.Model):
    bank_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, default=0)
    province = models.CharField(max_length=200, default=0, null=True, blank=True)
    city = models.CharField(max_length=200, default=0, null=True, blank=True)
    branch = models.CharField(max_length=200, default=0, null=True, blank=True)


class BankAccount(models.Model):
    account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=200, default=0)
    account_number = models.CharField(max_length=200, default=0)


class ThirdParty(models.Model):
    thirdParty_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    thirdParty_name = models.SmallIntegerField(
        choices=CHANNEL_CHOICES, default=2, verbose_name=_("Name")
    )
    method = models.CharField(max_length=30, verbose_name=_("Method"))
    channel = models.CharField(max_length=30, verbose_name=_("Channel"))
    currency = models.SmallIntegerField(
        choices=CURRENCY_CHOICES, default=0, verbose_name=_("Currency")
    )
    min_amount = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, verbose_name=_("Min Amount")
    )
    max_amount = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, verbose_name=_("Max Amount")
    )
    switch = models.SmallIntegerField(choices=THIRDPARTY_STATUS_CHOICES, default=0)
    # flat fee for each transaction
    transaction_fee = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        blank=True,
        verbose_name=_("Transaction Fee"),
    )
    # % fee for each transaction
    transaction_fee_per = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        blank=True,
        verbose_name=_("Transaction Fee Percentage"),
    )

    # required verifications: id, phone, email
    req_ver = models.CharField(max_length=200, null=True, blank=True)

    # market
    market = models.SmallIntegerField(choices=MARKET_CHOICES)

    # the maximum number of money to be routed to this channel (%)
    volume = models.DecimalField(max_digits=20, decimal_places=2, default=100)
    new_user_volume = models.DecimalField(max_digits=20, decimal_places=2, default=100)

    # control new users volumn
    limit_access = models.BooleanField(default=False)
    block_risk_level = models.SmallIntegerField(choices=RISK_LEVEL, null=True, blank=True)
    vip_level = models.SmallIntegerField(choices=VIP_CHOICES, null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "{0}".format(self.thirdParty_name)


class DepositChannel(ThirdParty):
    priority = models.IntegerField(default=0, verbose_name=_("Priority"))
    deposit_channel = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
<<<<<<< HEAD
        related_name="sb",
=======
        related_name="thirdparty",
>>>>>>> 2a38346977367b31b709a5703b222a3447a5b916
        through="DepositAccessManagement",
        through_fields=("deposit_channel", "user_id"),
    )

    class Meta:
        verbose_name = "Deposit Channel"
        verbose_name_plural = "Deposit Channels"

    def __str__(self):
        return self.get_thirdParty_name_display()


class WithdrawChannel(ThirdParty):
    class Meta:
        verbose_name = "Withdraw Channel"
        verbose_name_plural = "Withdraw Channels"

    def __str__(self):
        return self.get_thirdParty_name_display()


class Transaction(models.Model):
    transaction_id = models.CharField(
        max_length=200, default=0, verbose_name=_("Transaction id")
    )
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Member")
    )
    order_id = models.CharField(max_length=200, default=0, verbose_name=_("Order id"))
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Apply Amount")
    )
    currency = models.SmallIntegerField(
        choices=CURRENCY_CHOICES, default=0, verbose_name=_("Currency")
    )
    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default="en-Us",
        verbose_name=_("Language"),
    )
    depositorTier = models.SmallIntegerField(
        default=0, verbose_name=_("Depositor Tier")
    )
    method = models.CharField(max_length=200, blank=True, verbose_name=_("Method"))
    last_updated = models.DateTimeField(
        default=timezone.now, verbose_name=_("Status Last Updated")
    )
    request_time = models.DateTimeField(
        default=timezone.now, verbose_name=_("Time of Application")
    )
    arrive_time = models.DateTimeField(
<<<<<<< HEAD
        default=timezone.now, verbose_name=_("Account Time")
=======
        null=True, blank=True, verbose_name=_("Arrive Time")
>>>>>>> 2a38346977367b31b709a5703b222a3447a5b916
    )
    status = models.SmallIntegerField(
        choices=STATE_CHOICES, default=2, verbose_name=_("Status")
    )
    channel = models.SmallIntegerField(
        choices=CHANNEL_CHOICES, default=0, verbose_name=_("Payment")
    )
    transaction_type = models.SmallIntegerField(
        choices=TRANSACTION_TYPE_CHOICES, default=0, verbose_name=_("Transaction Type")
    )
    review_status = models.SmallIntegerField(
        choices=REVIEW_STATE_CHOICES, default=1, verbose_name=_("Review status")
    )
    remark = models.CharField(max_length=200, blank=True, verbose_name=_("Memo"))
    transfer_from = models.CharField(
        max_length=200, null=True, blank=True, verbose_name=_("From")
    )
    transfer_to = models.CharField(
        max_length=200, null=True, blank=True, verbose_name=_("To")
    )
    product = models.SmallIntegerField(
        choices=GAME_TYPE_CHOICES, default=4, verbose_name=_("Product")
    )
    # payer_id is Returned by Paypal
    # payer_id = models.CharField(max_length = 100, default=0)

    # The user Account
    user_bank_account = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, null=True, blank=True
    )

    # Auditor upload transaction success image
    transaction_image = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{0}: {1}, {2}, {3}".format(
            self.user_id, self.transaction_type, self.order_id, self.status
        )


class DepositAccessManagement(models.Model):
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        on_delete=models.CASCADE,
        related_name="deposit_user",
    )
    deposit_channel = models.ForeignKey(
        DepositChannel,
        on_delete=models.CASCADE,
        related_name="deposit_access_channel",
        verbose_name=_("Channel"),
    )

    class Meta:
        unique_together = (("user_id", "deposit_channel"),)
        verbose_name = "Deposit Access management"
        verbose_name_plural = verbose_name


class WithdrawAccessManagement(models.Model):
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        on_delete=models.CASCADE,
        related_name="withdraw_user",
    )
    withdraw_channel = models.ForeignKey(
        WithdrawChannel,
        on_delete=models.CASCADE,
        related_name="withdraw_access_channel",
        verbose_name=_("Channel"),
    )

    class Meta:
        unique_together = (("user_id", "withdraw_channel"),)
        verbose_name = "Withdraw Access management"
        verbose_name_plural = verbose_name
