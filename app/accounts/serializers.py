# 구현할 시리얼라이저들
#
# 구현해야 할 시리얼라이저들:
# 1. AccountSerializer - 계좌 정보 시리얼라이저
# 2. TransactionHistorySerializer - 거래내역 시리얼라이저
#
# 필요한 import들:
# from rest_framework import serializers
# from .models import Account, TransactionHistory


# app/accounts/serializers.py

from rest_framework import serializers
from .models import Account, TransactionHistory


# -------------------------------
# 1. 계좌(Account) 시리얼라이저
# -------------------------------
class AccountSerializer(serializers.ModelSerializer):
    # user는 서버에서 자동 주입되므로 클라이언트는 입력할 필요 없음 (read_only)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Account
        fields = [
            "id",
            "user",             # 계좌 소유자
            "account_number",   # 계좌번호
            "account_name",     # 계좌명 (별칭)
            "bank_code",        # 은행 코드
            "account_type",     # 계좌 유형 (예: 체크, 예금 등)
            "balance",          # 잔액
            "is_active",        # 계좌 활성화 여부
            "is_primary",       # 주계좌 여부
            "created_at",       # 생성일
            "updated_at",       # 수정일
        ]
        # balance와 날짜 같은 값은 서버에서만 관리 → 읽기 전용
        read_only_fields = ["balance", "created_at", "updated_at", "is_primary"]

    def validate(self, attrs):
        """
        같은 사용자(user) 내에서 계좌번호(account_number)가 중복되지 않도록 체크.
        (DB unique_together에서도 막히지만, 여기서도 미리 검증해서 친절한 에러 주기)
        """
        request = self.context.get("request")
        if request and request.user and attrs.get("account_number"):
            qs = Account.objects.filter(
                user=request.user, account_number=attrs["account_number"]
            )
            if self.instance:  # 업데이트 상황이면 자기 자신은 제외
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"account_number": "이미 등록된 계좌번호입니다."})
        return super().validate(attrs)

    def create(self, validated_data):
        """
        계좌 생성 시 user를 request.user로 자동 설정
        """
        request = self.context.get("request")
        if request and request.user and not validated_data.get("user"):
            validated_data["user"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        계좌 수정 시 balance는 직접 바꾸지 못하게 막음.
        balance는 오직 거래(TransactionHistory)를 통해 변경됨.
        """
        validated_data.pop("balance", None)
        return super().update(instance, validated_data)


# --------------------------------------
# 2. 거래내역(TransactionHistory) 시리얼라이저
# --------------------------------------
class TransactionHistorySerializer(serializers.ModelSerializer):
    # balance_after는 서버가 계산해서 넣어주므로 읽기 전용
    balance_after = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = TransactionHistory
        fields = [
            "id",
            "account",            # 어떤 계좌에서 일어난 거래인지
            "amount",             # 거래 금액
            "balance_after",      # 거래 후 잔액 (자동 계산됨)
            "transaction_type",   # 거래 유형 (입금/출금 등)
            "detail_type",        # 상세 유형 (카드결제, 이체 등)
            "description",        # 거래 설명
            "memo",               # 사용자 메모
            "counterpart_account",# 상대방 계좌 (이체 시)
            "counterpart_name",   # 상대방 이름 (이체 시)
            "transaction_date",   # 거래 발생 일시
            "created_at",         # 생성일
            "updated_at",         # 수정일
        ]
        read_only_fields = ["balance_after", "created_at", "updated_at"]

    def validate_amount(self, value):
        """
        거래 금액은 반드시 0보다 커야 함.
        """
        if value <= 0:
            raise serializers.ValidationError("거래 금액은 0보다 커야 합니다.")
        return value

    def _is_outgoing(self, tx_type: str):
        """
        거래유형이 '출금(OUT)'인지 '입금(IN)'인지 분류.
        - 프로젝트의 TRANSACTION_TYPES에 맞춰 조정 가능.
        """
        t = (tx_type or "").upper()
        out_types = {"WITHDRAW", "TRANSFER_OUT", "PAYMENT", "EXPENSE", "OUT"}
        in_types = {"DEPOSIT", "TRANSFER_IN", "INCOME", "REFUND", "IN"}
        if t in out_types:
            return True   # 출금
        if t in in_types:
            return False  # 입금
        return None       # 알 수 없음 → 오류 처리

    def validate(self, attrs):
        """
        - 본인 계좌인지 확인
        - 거래유형이 올바른지 확인
        - 거래 후 잔액이 음수가 되지 않도록 확인
        """
        account = attrs.get("account")
        amount = attrs.get("amount")
        tx_type = attrs.get("transaction_type")

        if not account:
            raise serializers.ValidationError({"account": "계좌를 지정하세요."})

        # 본인 계좌인지 확인
        request = self.context.get("request")
        if request and request.user and account.user_id != request.user.id:
            raise serializers.ValidationError({"account": "본인 소유의 계좌만 거래할 수 있습니다."})

        # 거래 방향(입금/출금) 판별
        direction = self._is_outgoing(tx_type)
        if direction is None:
            raise serializers.ValidationError({"transaction_type": "알 수 없는 거래유형입니다."})

        # 새 잔액 계산
        current_balance = account.balance or 0
        new_balance = current_balance - amount if direction else current_balance + amount

        if new_balance < 0:
            raise serializers.ValidationError({"amount": "잔액이 부족합니다."})

        # create()에서 쓰기 위해 임시 저장
        self._new_balance = new_balance
        return attrs

    def create(self, validated_data):
        """
        거래 생성 시 balance_after를 서버에서 계산하여 기록.
        Account 모델의 save()에서 balance가 자동 갱신됨.
        """
        validated_data["balance_after"] = getattr(self, "_new_balance", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        거래내역은 수정 불가 (회계 데이터는 기록 보존이 중요하기 때문).
        """
        raise serializers.ValidationError("거래내역은 수정할 수 없습니다.")
