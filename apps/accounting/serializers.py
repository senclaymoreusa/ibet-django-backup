from rest_framework import serializers
from .models import ThirdParty, Transaction

class depositMethodSerialize(serializers.ModelSerializer):
    method = serializers.CharField(write_only=True) 
    currency = serializers.CharField(read_only=True) 
    min_amount = serializers.FloatField(read_only=True) 
    max_amount = serializers.FloatField(read_only=True) 
    class Meta:
        model = ThirdParty
        fields = ('method','currency', 'min_amount','max_amount')
    
    

class bankListSerialize(serializers.ModelSerializer):
    class Meta:
        model = ThirdParty
        fields = ('thridParty_id','thridParty_name', 'currency','min_amount', 'max_amount', 'transaction_fee', 'switch', 'method')
    

class bankLimitsSerialize(serializers.ModelSerializer):
    class Meta:
        model = ThirdParty
        fields = ('thridParty_id','thridParty_name', 'currency','min_amount', 'max_amount', 'transaction_fee', 'switch', 'method')
    


   
