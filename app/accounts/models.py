# app/accounts/models.py

from django.db import models
from decimal import Decimal
from django.utils import timezone

# app의 커스텀 User 모델 참조
from app.models import User


# -----------------------------
# Account 모델
# -----------------------------
class Account(models.Model):
    """계좌 모델"""
    ACCOUNT_TYPES = [
        ('checking', '일반예금'),
        ('savings', '적금'),
        ('loan', '마이너스통장'),
        ('deposit', '정기예금'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='account_accounts',  # ✅ related_name 고유화
        verbose_name='사용자'
    )
    account_number = models.CharField(max_length=50, db_index=True, verbose_name='계좌번호')
    bank_code = models.CharField(max_length=10, verbose_name='은행코드')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, verbose_name='계좌유형')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), db_index=True, verbose_name='잔액')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'accounts_account'  # ✅ 테이블명 고유화
        verbose_name = '계좌'
        verbose_name_plural = '계좌들'
        unique_together = ['user', 'account_number']
        indexes = [
            models.Index(fields=['user', 'account_number']),
            models.Index(fields=['account_number']),
            models.Index(fields=['balance']),
        ]

    def __str__(self):
        return f"{self.user.nickname}의 {self.get_account_type_display()} ({self.account_number})"


# -----------------------------
# TransactionHistory 모델
# -----------------------------
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
        related_name='account_transactions',  # ✅ related_name 고유화
        verbose_name='계좌'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='거래금액')
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='거래후잔액')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name='거래유형')
    detail_type = models.CharField(max_length=50, choices=DETAIL_TYPES, null=True, blank=True, verbose_name='상세유형')
    transaction_detail = models.CharField(max_length=500, null=True, blank=True, verbose_name='거래내역상세')
    transaction_date = models.DateTimeField(db_index=True, verbose_name='거래일시')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'accounts_transaction_history'  # ✅ 테이블명 고유화
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
        if not self.pk:
            self.account.balance = self.balance_after
            self.account.save(update_fields=['balance', 'updated_at'])
        super().save(*args, **kwargs)


# -----------------------------
# Analysis 모델
# -----------------------------
class Analysis(models.Model):
    """분석 모델"""
    PERIOD_CHOICES = [
        ('daily', '일'),
        ('weekly', '주'),
        ('monthly', '월'),
        ('yearly', '년'),
        ('custom', '사용자정의'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='account_analyses',  # ✅ related_name 고유화
        verbose_name='사용자'
    )
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='총수입')
    total_expense = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='총지출')
    savings_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='저축금액')
    analysis_period = models.CharField(max_length=20, choices=PERIOD_CHOICES, verbose_name='분석기간')
    ai_analysis = models.TextField(null=True, blank=True, verbose_name='AI분석결과')
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name='설명')
    period_start = models.DateField(db_index=True, verbose_name='분석시작일')
    period_end = models.DateField(db_index=True, verbose_name='분석종료일')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'accounts_analysis'  # ✅ 테이블명 고유화
        verbose_name = '분석'
        verbose_name_plural = '분석들'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'period_start', 'period_end']),
            models.Index(fields=['period_start']),
            models.Index(fields=['period_end']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.nickname}의 {self.get_analysis_period_display()} 분석 ({self.period_start} ~ {self.period_end})"

    @property
    def savings_rate(self):
        if self.total_income > 0:
            return (self.savings_amount / self.total_income) * 100
        return 0


# -----------------------------
# Notification 모델
# -----------------------------
class Notification(models.Model):
    """알림 모델"""
    NOTIFICATION_TYPES = [
        ('transaction', '거래알림'),
        ('analysis', '분석알림'),
        ('system', '시스템알림'),
        ('budget', '예산알림'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='account_notifications',  # ✅ related_name 고유화
        verbose_name='사용자'
    )
    message = models.CharField(max_length=1000, verbose_name='메시지')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='system', verbose_name='알림유형')
    is_read = models.BooleanField(default=False, db_index=True, verbose_name='읽음여부')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='읽은시간')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'accounts_notifications'  # ✅ 테이블명 고유화
        verbose_name = '알림'
        verbose_name_plural = '알림들'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['is_read']),
            models.Index(fields=['created_at']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.user.nickname}에게 {self.get_notification_type_display()}: {self.message[:50]}..."

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])


# -----------------------------
# 시그널
# -----------------------------
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=TransactionHistory)
def create_transaction_notification(sender, instance, created, **kwargs):
    """거래내역 생성 시 알림 생성"""
    if created:
        Notification.objects.create(
            user=instance.account.user,
            message=f"{instance.get_transaction_type_display()} {instance.amount:,}원이 처리되었습니다.",
            notification_type='transaction'
        )
