# 구현할 시리얼라이저들
#
# 구현해야 할 시리얼라이저들:
# 1. AccountSerializer - 계좌 정보 시리얼라이저
# 2. TransactionHistorySerializer - 거래내역 시리얼라이저
#
# 필요한 import들:
# from rest_framework import serializers
# from .models import Account, TransactionHistory

from rest_framework import serializers
from .models import Account, TransactionHistory


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            'id',
            'account_number',
            'account_name',
            'bank_code',
            'account_type',
            'balance',
            'is_active',
            'is_primary',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['balance', 'is_primary', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        return Account.objects.create(user=user, **validated_data)


class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = [
            'id',
            'account',
            'amount',
            'balance_after',
            'transaction_type',
            'detail_type',
            'description',
            'memo',
            'counterpart_account',
            'counterpart_name',
            'transaction_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['balance_after', 'created_at', 'updated_at']
