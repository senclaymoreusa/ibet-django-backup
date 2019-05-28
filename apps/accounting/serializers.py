from rest_framework import serializers
from .models import ThirdParty, Transaction, DepositChannel, WithdrawChannel

class depositMethodSerialize(serializers.ModelSerializer):
     
    class Meta:
        model = DepositChannel
        fields = ('thridParty_name','method','currency', 'min_amount','max_amount')
    
    

class bankListSerialize(serializers.ModelSerializer):
    class Meta:
        model = DepositChannel
        fields = ('thridParty_id','thridParty_name', 'currency','min_amount', 'max_amount', 'transaction_fee', 'switch', 'method')
    

class bankLimitsSerialize(serializers.ModelSerializer):
    class Meta:
        model = DepositChannel
        fields = ('thridParty_id','thridParty_name', 'currency','min_amount', 'max_amount', 'transaction_fee', 'switch', 'method')
    
class submitDepositSerialize(serializers.Serializer):
    order_id         = serializers.CharField(required=True)
    amount            = serializers.DecimalField(max_digits = 10, decimal_places=2, required=True)
    currency        = serializers.CharField(required=True)
    language       = serializers.CharField(required=True)
    user_id        = serializers.CharField(required=True)
    method            = serializers.CharField(required=True)
    
    
   
    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)

    def update(self, instance, validated_data):

        instance.order_id = validated_data.get('order_id', instance.order_id)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.currency = validated_data.get('currency', instance.currency)
        instance.language = validated_data.get('language', instance.language)
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.method = validated_data.get('method', instance.method)
        
        
        instance.save() 
        return instance

class submitPayoutSerialize(serializers.Serializer):
    order_id         = serializers.CharField(required=True)
    amount            = serializers.DecimalField(max_digits = 10, decimal_places=2, required=True)
    currency        = serializers.CharField(required=True)
    language       = serializers.CharField(required=True)
    user_id        = serializers.CharField(required=True)
    method            = serializers.CharField(required=True)
    
    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)

    def update(self, instance, validated_data):

        instance.order_id = validated_data.get('order_id', instance.order_id)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.currency = validated_data.get('currency', instance.currency)
        instance.language = validated_data.get('language', instance.language)
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.method = validated_data.get('method', instance.method)
        
        
        instance.save() 
        return instance
   
class payoutTransactionSerialize(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('order_id','method', 'request_time','amount', 'currency', 'status', 'user_id')

class approvePayoutSerialize(serializers.Serializer):
    order_id         = serializers.CharField(required=True)
    user_id        = serializers.CharField(required=True)
    remark        = serializers.CharField(required=True)
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
