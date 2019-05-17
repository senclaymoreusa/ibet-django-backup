from rest_framework import serializers
from .models import ThirdParty, Transaction, DepositChannel

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
    


   
