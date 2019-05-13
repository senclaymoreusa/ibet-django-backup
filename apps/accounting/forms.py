from django import forms
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Transaction

# from django.contrib.auth import get_user_model
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('user_id', 'transaction_type', 'amount', 'status', 'channel', 'request_time', 'arrive_time', 'review_status', 'remark')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_id'].disabled = True
        self.fields['channel'].disabled = True
        self.fields['amount'].disabled = True
        self.fields['status'].disabled = True
        self.fields['request_time'].disabled = True
        self.fields['arrive_time'].disabled = True
        self.fields['transaction_type'].disabled = True

class DepositReviewForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('user_id', 'amount', 'status', 'channel', 'request_time', 'arrive_time', 'review_status', 'remark')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_id'].disabled = True
        self.fields['channel'].disabled = True
        self.fields['amount'].disabled = True
        self.fields['status'].disabled = True
        self.fields['request_time'].disabled = True
        self.fields['arrive_time'].disabled = True
    
class WithdrawReviewForm(DepositReviewForm):
    pass