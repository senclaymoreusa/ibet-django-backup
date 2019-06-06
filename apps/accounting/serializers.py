from rest_framework import serializers
from .models import ThirdParty, Transaction, DepositChannel, WithdrawChannel

class depositMethodSerialize(serializers.Serializer):
    currency         = serializers.CharField(required=True)
    

class bankListSerialize(serializers.Serializer):
    currency         = serializers.CharField(required=True)
    method         = serializers.CharField(required=True)
    
class bankLimitsSerialize(serializers.Serializer):
    currency         = serializers.CharField(required=True)
    method         = serializers.CharField(required=True)
    bank           = serializers.CharField(required=True)
    
    
class submitDepositSerialize(serializers.Serializer):
    order_id         = serializers.CharField(required=True)
    amount            = serializers.DecimalField(max_digits = 10, decimal_places=2, required=True)
    currency        = serializers.CharField(required=True)
    language       = serializers.CharField(required=True)
    user_id        = serializers.CharField(required=True)
    method            = serializers.CharField(required=True)
    
class submitPayoutSerialize(serializers.Serializer):
    order_id         = serializers.CharField(required=True)
    amount            = serializers.DecimalField(max_digits = 10, decimal_places=2, required=True)
    currency        = serializers.CharField(required=True)
    language       = serializers.CharField(required=True)
    user_id        = serializers.CharField(required=True)
    method            = serializers.CharField(required=True)
    
class payoutTransactionSerialize(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('order_id','method', 'request_time','amount', 'currency', 'status', 'user_id')

class approvePayoutSerialize(serializers.Serializer):
    order_id         = serializers.CharField(required=True)
    user_id        = serializers.CharField(required=True)
    remark        = serializers.CharField(required=True)
    
class depositThirdPartySerialize(serializers.Serializer):
    order_id         = serializers.CharField(required=True)
    user_id        = serializers.CharField(required=True)
    method        = serializers.CharField(required=True)
    amount        = serializers.CharField(required=True)
    status        = serializers.CharField(required=True)
    
class payoutMethodSerialize(serializers.Serializer):
     
    currency         = serializers.CharField(required=True)
    
class payoutBanklistSerialize(serializers.Serializer):
     
    currency         = serializers.CharField(required=True)
    method         = serializers.CharField(required=True)
    
class payoutBanklimitsSerialize(serializers.Serializer):
     
    currency         = serializers.CharField(required=True)
    method         = serializers.CharField(required=True)
    bank           = serializers.CharField(required=True)
    

class paypalCreatePaymentSerialize(serializers.Serializer):
    
    
    currency         = serializers.CharField(required=True)
    amount           = serializers.CharField(required=True)
    user             = serializers.CharField(required=True)
    
class paypalgetOrderSerialize(serializers.Serializer):
    order_id  = serializers.CharField(required=True)
    user             = serializers.CharField(required=True)
    
class paypalExecutePaymentSerialize(serializers.Serializer):
    payer_id = serializers.CharField(required=True)
    payment_id = serializers.CharField(required=True)
    user             = serializers.CharField(required=True)
    
    
