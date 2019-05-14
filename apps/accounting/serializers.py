from rest_framework import serializers
from .models import ThirdParty

class depositMethodSerialize(serializers.ModelSerializer):
    class Meta:
        model = ThirdParty
        fields = ('method', 'currency', 'minTransactionAmount', 'maxTransactionAmount')