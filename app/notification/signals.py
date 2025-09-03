from django.db.models.signals import post_save
from django.dispatch import receiver
from app.accounts.models import TransactionHistory
from .models import Notification


@receiver(post_save, sender=TransactionHistory)
def create_transaction_notification(sender, instance, created, **kwargs):
    """거래내역 생성시 알림 생성"""
    if created:
        message = f"{instance.get_transaction_type_display()} {instance.amount:,}원이 처리되었습니다."
        Notification.objects.create(
            user=instance.account.user,
            message=message,
            notification_type='transaction'
        )