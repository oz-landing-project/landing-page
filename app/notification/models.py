from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.TextField()
    type = models.CharField(max_length=50, blank=True, default="")  # e.g. TRANSACTION, ANALYSIS
    related_id = models.CharField(max_length=64, blank=True, default="")  # 선택

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
        ]

    def __str__(self):
        head = self.message[:30]
        return f"[{self.user_id}] {head}{'...' if len(self.message) > 30 else ''}"
