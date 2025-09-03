from rest_framework import serializers
from .models import Account, TransactionHistory


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ('user', 'account_number', 'created_at', 'updated_at')


class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
# 구현할 시리얼라이저들
#
# 구현해야 할 시리얼라이저들:
# 1. AccountSerializer - 계좌 정보 시리얼라이저
# 2. TransactionHistorySerializer - 거래내역 시리얼라이저
#
# 필요한 import들:
# from rest_framework import serializers
# from .models import Account, TransactionHistory