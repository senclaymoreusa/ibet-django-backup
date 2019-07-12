from rest_framework import serializers
from .models import ThirdParty, Transaction, DepositChannel, WithdrawChannel
from utils.constants import *

class depositMethodSerialize(serializers.Serializer):
    # specify what fields are required when we save object into database
    thridParty_name = serializers.ChoiceField(choices=CHANNEL_CHOICES, default=2)
    currency = serializers.ChoiceField(choices=CURRENCY_CHOICES, default=0)
    method = serializers.CharField(required=True)
    min_amount = serializers.DecimalField(required=True, max_digits=None, decimal_places=2)
    max_amount = serializers.DecimalField(required=True, max_digits=None, decimal_places=2)

    def create(self, validated_data):
        p, created = DepositChannel.objects.get_or_create(**validated_data)
        if (created): print("Inserted row(s) into SQL database:")
        else: print("Updated row(s) into SQL database:")
        print(validated_data)
        return p

class bankListSerialize(serializers.Serializer):
    currency = serializers.ChoiceField(choices=CURRENCY_CHOICES, default=0)
    method = serializers.ChoiceField(choices=DEPOSIT_METHOD_CHOICES, default=0)


class bankLimitsSerialize(serializers.Serializer):
    bank = serializers.CharField(required=True)
    thridParty_name = serializers.IntegerField(required=True, min_value=0, max_value=5)
    currency = serializers.CharField(required=True)
    method = serializers.CharField(required=True)
    min_amount = serializers.DecimalField(required=True, max_digits=None, decimal_places=2)
    max_amount = serializers.DecimalField(required=True, max_digits=None, decimal_places=2)
    def create(self, validated_data):
        return DepositChannel.objects.get_or_create(**validated_data)

    
class submitDepositSerialize(serializers.ModelSerializer):
    # transaction_id         = serializers.UUIDField(format='hex')
    # amount            = serializers.DecimalField(max_digits = 10, decimal_places=2, required=True)
    # currency        = serializers.CharField(required=True)
    # language       = serializers.CharField(required=True)
    # user_id        = serializers.CharField(required=True)
    # method            = serializers.CharField(required=True)
    class Meta:
        model = Transaction
        fields = ('order_id','amount', 'currency','language','user_id','method')


class submitPayoutSerialize(serializers.Serializer):
    order_id         = serializers.CharField(required=True)
    amount            = serializers.DecimalField(max_digits = 10, decimal_places=2, required=True)
    currency        = serializers.CharField(required=True)
    language       = serializers.CharField(required=True)
    user_id        = serializers.CharField(required=True)
    method            = serializers.CharField(required=True)
    
    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)

   
class payoutTransactionSerialize(serializers.Serializer):
    
    order_id         = serializers.CharField(required=True)
    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)



class approvePayoutSerialize(serializers.Serializer):
    order_id         = serializers.CharField(required=True)
    user_id        = serializers.CharField(required=True)
    remark        = serializers.CharField(required=False)
    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)

    def update(self, instance, validated_data):

        instance.order_id = validated_data.get('order_id', instance.order_id)
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.remark = validated_data.get('remark', instance.remark)
        
        instance.save() 
        return instance
class depositThirdPartySerialize(serializers.Serializer):
    order_id         = serializers.CharField(required=True)
    user_id        = serializers.CharField(required=True)
    method        = serializers.CharField(required=True)
    amount        = serializers.CharField(required=True)
    status        = serializers.CharField(required=True)
    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)

    def update(self, instance, validated_data):

        instance.order_id = validated_data.get('order_id', instance.order_id)
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.method = validated_data.get('method', instance.method)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.status = validated_data.get('status', instance.status)
        instance.save() 
        return instance
class payoutMethodSerialize(serializers.Serializer):
     
    currency         = serializers.CharField(required=True)
    def create(self, validated_data):
        return WithdrawChannel.objects.create(**validated_data)

    def update(self, instance, validated_data):

        instance.currency = validated_data.get('currency', instance.currency)
        instance.save() 
        return instance
class payoutBanklistSerialize(serializers.Serializer):
     
    currency         = serializers.CharField(required=True)
    method         = serializers.CharField(required=True)
    def create(self, validated_data):
        return WithdrawChannel.objects.create(**validated_data)

    def update(self, instance, validated_data):

        instance.currency = validated_data.get('currency', instance.currency)
        instance.method = validated_data.get('method', instance.method)
        instance.save() 
        return instance
class payoutBanklimitsSerialize(serializers.Serializer):
    
    currency         = serializers.CharField(required=True)
    method         = serializers.CharField(required=True)
    bank           = serializers.CharField(required=True)
    def create(self, validated_data):
        return WithdrawChannel.objects.create(**validated_data)

    def update(self, instance, validated_data):

        instance.currency = validated_data.get('currency', instance.currency)
        instance.method = validated_data.get('method', instance.method)
        
        instance.save() 
        return instance

class paypalCreatePaymentSerialize(serializers.Serializer):
    
    currency         = serializers.CharField(required=True)
    amount           = serializers.CharField(required=True)
    user             = serializers.CharField(required=True)
    def create(self, validated_data):
        return Transaction.objects.get_or_create(**validated_data)

    
class paypalgetOrderSerialize(serializers.Serializer):
    order_id  = serializers.CharField(required=True)
    user             = serializers.CharField(required=True)
    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)
    
class paypalExecutePaymentSerialize(serializers.Serializer):
    payer_id = serializers.CharField(required=True)
    payment_id = serializers.CharField(required=True)
    user             = serializers.CharField(required=True)
    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)
    

class astroPaymentStatusSerialize(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('order_id', 'user_id', 'amount', 'bank', 'currency', 'channel','status')


class asiapayDepositSerialize(serializers.Serializer):
    order_id           = serializers.CharField(required=True)
    userid             = serializers.CharField(required=True)
    currency           = serializers.ChoiceField(choices=CURRENCY_CHOICES,default=0)           
    # channel            = serializers.ChoiceField(choices=CHANNEL_CHOICES,default=4) 
    # status             = serializers.ChoiceField(choices=STATE_CHOICES, default=3)
    method          = serializers.ChoiceField(choices=ASIAPAY_BANK_CHOICES)
    PayWay          = serializers.ChoiceField(choices=ASIAPAY_PAYWAY_CHOICES)
    amount          = serializers.CharField(required=True)
    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)
class asiapayCashoutSerialize(serializers.Serializer):
    order_id           = serializers.CharField(required=True)
    userid             = serializers.CharField(required=True)
    currency           = serializers.ChoiceField(choices=CURRENCY_CHOICES,default=0)           
    amount             = serializers.CharField(required=True)
    cashoutMethod      = serializers.ChoiceField(choices=ASIAPAY_CASHOUTMETHOD_CHOICES)
    CashCardNumber     = serializers.CharField(required=True)
    CashCardChName     = serializers.CharField(required=True)
    CashBankDetailName     = serializers.CharField(required=True)
    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)

class asiapayDepositFinishSerialize(serializers.Serializer):
    order_id           = serializers.CharField(required=True)
    userid             = serializers.CharField(required=True)
    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)
class asiapayOrderStatusFinishSerialize(serializers.Serializer):
    order_id           = serializers.CharField(required=True)
    userid             = serializers.CharField(required=True)
    CmdType            = serializers.ChoiceField(choices=ASIAPAY_CMDTYPE)
    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)
class asiapayExchangeRateFinishSerialize(serializers.Serializer):
    Amount             = serializers.CharField(required=True)
    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)
class asiapayDepositArriveSerialize(serializers.Serializer):
    StatusCode       = serializers.CharField(required=True)
    RevCardNumber    = serializers.CharField(required=True)
    amount         = serializers.CharField(required=True)
    order_id          = serializers.CharField(required=True)
    uID              = serializers.CharField(required=True)   
    ProcessDate      = serializers.CharField(required=True)
    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)
    

