from django.db import models
from django.conf import settings
from decimal import Decimal


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
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analyses',
        verbose_name='사용자'
    )
    total_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='총수입'
    )
    total_expense = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='총지출'
    )
    savings_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='저축금액'
    )
    analysis_period = models.CharField(
        max_length=20,
        choices=PERIOD_CHOICES,
        verbose_name='분석기간'
    )
    ai_analysis = models.TextField(
        null=True, blank=True,
        verbose_name='AI분석결과'
    )
    description = models.CharField(
        max_length=500,
        null=True, blank=True,
        verbose_name='설명'
    )
    period_start = models.DateField(
        db_index=True,
        verbose_name='분석시작일'
    )
    period_end = models.DateField(
        db_index=True,
        verbose_name='분석종료일'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='생성일시'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일시'
    )

    class Meta:
        db_table = 'analysis'
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
        """저축률 계산"""
        if self.total_income > 0:
            return (self.savings_amount / self.total_income) * 100
        return 0