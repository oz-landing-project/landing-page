from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from .constants import BANK_CODE, ACCOUNT_TYPES, TRANSACTION_TYPES, TRANSACTION_METHOD


class Account(models.Model):
    """
    계좌 모델
    
    사용자의 은행 계좌 정보를 관리합니다.
    필요에 따라 필드를 추가할 수 있습니다.
    """
    # 기본 정보
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='accounts',
        verbose_name='사용자'
    )
    account_number = models.CharField(
        '계좌번호',
        max_length=50,
        db_index=True
    )
    account_name = models.CharField(
        '계좌명',
        max_length=100,
        help_text='사용자가 지정한 계좌 별칭'
    )
    bank_code = models.CharField(
        '은행코드',
        max_length=10,
        choices=BANK_CODE
    )
    account_type = models.CharField(
        '계좌유형',
        max_length=20,
        choices=ACCOUNT_TYPES,
        default='CHECKING'
    )
    
    # 잔액 정보
    balance = models.DecimalField(
        '잔액',
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        db_index=True
    )
    
    # 계좌 상태
    is_active = models.BooleanField('활성 상태', default=True)
    is_primary = models.BooleanField('주계좌 여부', default=False)
    
    # 타임스탬프
    created_at = models.DateTimeField('생성일시', auto_now_add=True)
    updated_at = models.DateTimeField('수정일시', auto_now=True)
    
    class Meta:
        db_table = 'accounts'
        verbose_name = '계좌'
        verbose_name_plural = '계좌들'
        indexes = [
            models.Index(fields=['user', 'account_number']),
            models.Index(fields=['account_number']),
            models.Index(fields=['balance']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
        unique_together = ['user', 'account_number']
    
    def __str__(self):
        return f"{self.user.nickname}의 {self.account_name} ({self.get_bank_code_display()})"
    
    def save(self, *args, **kwargs):
        # 첫 번째 계좌는 자동으로 주계좌로 설정
        if not self.pk and not self.user.accounts.exists():
            self.is_primary = True
        super().save(*args, **kwargs)


class TransactionHistory(models.Model):
    """
    거래내역 모델
    
    계좌의 모든 거래 내역을 기록합니다.
    필요에 따라 필드를 추가할 수 있습니다.
    """
    # 기본 정보
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='계좌'
    )
    
    # 거래 정보
    amount = models.DecimalField(
        '거래금액',
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    balance_after = models.DecimalField(
        '거래후잔액',
        max_digits=15,
        decimal_places=2
    )
    transaction_type = models.CharField(
        '거래유형',
        max_length=20,
        choices=TRANSACTION_TYPES
    )
    detail_type = models.CharField(
        '상세유형',
        max_length=50,
        choices=TRANSACTION_METHOD,
        null=True,
        blank=True
    )
    
    # 거래 상세
    description = models.CharField(
        '거래내역',
        max_length=200,
        help_text='거래 설명'
    )
    memo = models.TextField(
        '메모',
        max_length=500,
        blank=True,
        help_text='사용자 메모'
    )
    
    # 상대방 정보 (이체 시)
    counterpart_account = models.CharField(
        '상대방계좌',
        max_length=50,
        blank=True
    )
    counterpart_name = models.CharField(
        '상대방명',
        max_length=100,
        blank=True
    )
    
    # 거래 일시
    transaction_date = models.DateTimeField(
        '거래일시',
        db_index=True
    )
    
    # 타임스탬프
    created_at = models.DateTimeField('생성일시', auto_now_add=True)
    updated_at = models.DateTimeField('수정일시', auto_now=True)
    
    class Meta:
        db_table = 'transaction_history'
        verbose_name = '거래내역'
        verbose_name_plural = '거래내역들'
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['account', 'transaction_date']),
            models.Index(fields=['transaction_date']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['detail_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.account.account_name} - {self.get_transaction_type_display()} {self.amount:,}원"
    
    def save(self, *args, **kwargs):
        """거래내역 저장 시 계좌 잔액 업데이트"""
        if not self.pk:  # 새로운 거래내역인 경우
            # 계좌 잔액 업데이트
            self.account.balance = self.balance_after
            self.account.save(update_fields=['balance', 'updated_at'])
        super().save(*args, **kwargs)