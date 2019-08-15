from django import forms
from django.forms import ModelForm

# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *

# from django.contrib.auth import get_user_model
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = (
            "user_id",
            "transaction_type",
            "amount",
            "status",
            "request_time",
            "arrive_time",
            "review_status",
            "remark",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['user_id'].disabled = True
        # self.fields['channel'].disabled = True
        # self.fields['amount'].disabled = True
        # self.fields['status'].disabled = True
        # self.fields['request_time'].disabled = True
        # self.fields['arrive_time'].disabled = True
        # self.fields['transaction_type'].disabled = True


class DepositReviewForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = (
            "user_id",
            "amount",
            "status",
            "request_time",
            "arrive_time",
            "review_status",
            "remark",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user_id"].disabled = True
        self.fields["amount"].disabled = True
        self.fields["status"].disabled = True
        self.fields["request_time"].disabled = True
        self.fields["arrive_time"].disabled = True


class WithdrawReviewForm(DepositReviewForm):
    pass


class UserDepositAccessManagementCreateFrom(ModelForm):
    class Meta:
        model = DepositAccessManagement
        fields = ("user_id", "deposit_channel")


class UserDepositAccessManagementEditFrom(forms.ModelForm):
    class Meta:
        model = DepositAccessManagement
        fields = ("deposit_channel",)

    def __init__(self, *args, **kwargs):
        super(UserDepositAccessManagementEditFrom, self).__init__(*args, **kwargs)

    def has_add_permission(self):
        return False


class DepositChannelForm(forms.ModelForm):
    class Meta:
        model = DepositChannel
        fields = (
            "thirdParty_name",
            "min_amount",
            "max_amount",
            "transaction_fee",
            "volume",
            "new_user_volume",
        )

