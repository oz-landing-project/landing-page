from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    """알림 모델"""
    NOTIFICATION_TYPES = [
        ('transaction', '거래알림'),
        ('analysis', '분석알림'),
        ('system', '시스템알림'),
        ('budget', '예산알림'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='사용자'
    )
    message = models.CharField(
        max_length=1000,
        verbose_name='메시지'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        default='system',
        verbose_name='알림유형'
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='읽음여부'
    )
    read_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='읽은시간'
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
        db_table = 'notifications'
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
        """알림을 읽음으로 표시"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])