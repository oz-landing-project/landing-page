from django.db import models
from django.conf import settings
from decimal import Decimal


class Account(models.Model):
    """계좌 모델"""
    ACCOUNT_TYPES = [
        ('checking', '일반예금'),
        ('savings', '적금'),
        ('loan', '마이너스통장'),
        ('deposit', '정기예금'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='accounts',
        verbose_name='사용자'
    )
    account_number = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name='계좌번호'
    )
    bank_code = models.CharField(
        max_length=10,
        verbose_name='은행코드'
    )
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPES,
        verbose_name='계좌유형'
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        db_index=True,
        verbose_name='잔액'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일시'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일시'
    )

    class Meta:
        db_table = 'accounts'
        verbose_name = '계좌'
        verbose_name_plural = '계좌들'
        indexes = [
            models.Index(fields=['user', 'account_number']),
            models.Index(fields=['account_number']),
            models.Index(fields=['balance']),
        ]
        unique_together = ['user', 'account_number']

    def __str__(self):
        return f"{self.user.nickname}의 {self.get_account_type_display()} ({self.account_number})"


class TransactionHistory(models.Model):
    """거래내역 모델"""
    TRANSACTION_TYPES = [
        ('deposit', '입금'),
        ('withdrawal', '출금'),
    ]

    DETAIL_TYPES = [
        ('deposit', '입금'),
        ('transfer', '계좌이체'),
        ('auto_transfer', '자동이체'),
        ('card_payment', '카드결제'),
        ('atm_withdrawal', 'ATM출금'),
        ('interest', '이자입금'),
    ]

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='계좌'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='거래금액'
    )
    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='거래후잔액'
    )
    transaction_detail = models.CharField(
        max_length=500,
        null=True, blank=True,
        verbose_name='거래내역상세'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        verbose_name='거래유형'
    )
    detail_type = models.CharField(
        max_length=50,
        choices=DETAIL_TYPES,
        null=True, blank=True,
        verbose_name='상세유형'
    )
    transaction_date = models.DateTimeField(
        db_index=True,
        verbose_name='거래일시'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일시'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일시'
    )

    class Meta:
        db_table = 'transaction_history'
        verbose_name = '거래내역'
        verbose_name_plural = '거래내역들'
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['account', 'transaction_date']),
            models.Index(fields=['transaction_date']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.account.user.nickname} - {self.get_transaction_type_display()} {self.amount}원"

    def save(self, *args, **kwargs):
        """거래내역 저장시 계좌 잔액 업데이트"""
        if not self.pk:  # 새로운 거래내역인 경우
            self.account.balance = self.balance_after
            self.account.save(update_fields=['balance', 'updated_at'])
        super().save(*args, **kwargs)