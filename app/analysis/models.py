# app/analysis/models.py
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, F

class Analysis(models.Model):
    PERIOD_TYPE_CHOICES = [
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="analyses",
        db_index=True,
        verbose_name="사용자",
    )

    about = models.CharField("분석 주제", max_length=100)
    type = models.CharField("주기", max_length=10, choices=PERIOD_TYPE_CHOICES, db_index=True)

    period_start = models.DateField("분석 시작일", db_index=True)
    period_end   = models.DateField("분석 종료일", db_index=True)

    description = models.TextField("설명", blank=True)
    result_image = models.ImageField("결과 이미지", upload_to="analysis_results/", blank=True, null=True)

    created_at = models.DateTimeField("생성일시", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일시", auto_now=True)

    class Meta:
        # ✅ DB에 이미 존재하는 실제 테이블명으로 고정
        db_table = "analysis"
        ordering = ["-created_at"]
        verbose_name = "분석"
        verbose_name_plural = "분석들"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["user", "period_start", "period_end"]),
            models.Index(fields=["type"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(period_start__lte=F("period_end")),
                name="analysis_period_order_ok",
            ),
        ]

    def clean(self):
        if self.period_start and self.period_end and self.period_start > self.period_end:
            raise ValidationError("분석 기간이 올바르지 않습니다.")

    def __str__(self):
        return f"{self.user} - {self.about} ({self.period_start} ~ {self.period_end})"
