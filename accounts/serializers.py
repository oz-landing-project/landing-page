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


# 1. AccountSerializer - 계좌 정보 시리얼라이저
class AccountSerializer(serializers.ModelSerializer):
    """
    계좌 정보를 직렬화하는 시리얼라이저
    - 사용자의 계좌 CRUD 및 주계좌 설정을 처리합니다.
    """
    class Meta:
        model = Account
        fields = (
            'id',
            'account_number',
            'account_name',
            'bank_code',
            'account_type',
            'balance',
            'is_primary',
            'is_active',
            'created_at'
        )
        read_only_fields = ('balance', 'created_at', 'is_active', 'user')

    def validate(self, data):
        """
        계좌번호가 이미 등록되었는지 유효성 검사
        """
        user = self.context['request'].user
        account_number = data.get('account_number')
        if account_number and Account.objects.filter(user=user, account_number=account_number).exists():
            raise serializers.ValidationError({"account_number": "이미 등록된 계좌번호입니다."})
        return data


# 2. TransactionHistorySerializer - 거래내역 시리얼라이저
class TransactionHistorySerializer(serializers.ModelSerializer):
    """
    거래내역 정보를 직렬화하는 시리얼라이저
    - 특정 계좌의 거래내역을 조회합니다.
    """
    account_name = serializers.CharField(source='account.account_name', read_only=True)
    bank_code = serializers.CharField(source='account.bank_code', read_only=True)

    class Meta:
        model = TransactionHistory
        fields = (
            'id',
            'account',
            'account_name',
            'bank_code',
            'transaction_type',
            'detail_type',
            'amount',
            'balance_after',
            'description',
            'memo',
            'counterpart_account',
            'counterpart_name',
            'transaction_date',
            'created_at'
        )
        read_only_fields = ('balance_after', 'created_at')