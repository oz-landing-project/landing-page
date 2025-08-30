from rest_framework import serializers
from .models import Account, TransactionHistory


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'account_number', 'bank_code', 'account_type', 'balance', 'created_at']
        read_only_fields = ['id', 'balance', 'created_at']


class TransactionHistorySerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(source='account.account_number', read_only=True)
    
    class Meta:
        model = TransactionHistory
        fields = [
            'id', 'account', 'account_number', 'amount', 'balance_after',
            'transaction_detail', 'transaction_type', 'detail_type',
            'transaction_date', 'created_at'
        ]
        read_only_fields = ['id', 'balance_after', 'created_at']