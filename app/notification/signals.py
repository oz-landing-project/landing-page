from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

# 거래 생성 시 알림 예시
try:
    from app.accounts.models import Transaction
except Exception:
    Transaction = None

if Transaction is not None:
    @receiver(post_save, sender=Transaction, dispatch_uid="notify_on_transaction_create")
    def notify_on_transaction_create(sender, instance, created, **kwargs):
        if not created:
            return
        user = getattr(instance, "user", None) or getattr(getattr(instance, "account", None), "user", None)
        if not user:
            return
        amount = getattr(instance, "amount", None)
        detail = getattr(instance, "transaction_detail", "")
        msg = f"거래가 등록되었습니다: {detail} (금액: {amount})"
        Notification.objects.create(
            user=user,
            message=msg,
            type="TRANSACTION",
            related_id=str(instance.pk),
        )

# 분석 완료 시 알림 예시
try:
    from app.analysis.models import Analysis
except Exception:
    Analysis = None

if Analysis is not None:
    @receiver(post_save, sender=Analysis, dispatch_uid="notify_on_analysis_done")
    def notify_on_analysis_done(sender, instance, created, **kwargs):
        if getattr(instance, "status", "") != "DONE":
            return
        user = getattr(instance, "user", None)
        if not user:
            return
        period = getattr(instance, "analysis_period", "")
        msg = f"{period} 분석이 완료되었습니다."
        Notification.objects.get_or_create(
            user=user,
            type="ANALYSIS",
            related_id=str(instance.pk),
            defaults={"message": msg},
        )
