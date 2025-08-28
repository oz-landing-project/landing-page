import pandas as pd
import matplotlib.pyplot as plt
import os
from django.conf import settings
from accounts.models import TransactionHistory
from .models import Analysis
from io import BytesIO
from django.core.files.base import ContentFile

class Analyzer:
    def __init__(self, user, about, type_, period_start, period_end):
        self.user = user
        self.about = about
        self.type = type_
        self.period_start = period_start
        self.period_end = period_end

    def run(self):
        # 1. 거래내역 가져오기
        qs = TransactionHistory.objects.filter(
            account__user=self.user,
            transaction_date__range=[self.period_start, self.period_end]
        )

        if not qs.exists():
            raise ValueError("해당 기간에 거래내역이 없습니다.")

        # 2. DataFrame 생성
        data = list(qs.values("transaction_date", "amount", "transaction_type"))
        df = pd.DataFrame(data)

        # 3. 시각화
        plt.figure(figsize=(6, 4))
        if self.about == "총 지출":
            df_expense = df[df["transaction_type"] == "withdrawal"]
            df_expense.groupby(df_expense["transaction_date"].dt.date)["amount"].sum().plot(kind="bar")
            plt.title("총 지출 분석")
        elif self.about == "총 수입":
            df_income = df[df["transaction_type"] == "deposit"]
            df_income.groupby(df_income["transaction_date"].dt.date)["amount"].sum().plot(kind="bar")
            plt.title("총 수입 분석")

        # 4. 이미지 저장 (메모리 → FileField)
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        analysis = Analysis.objects.create(
            user=self.user,
            about=self.about,
            type=self.type,
            period_start=self.period_start,
            period_end=self.period_end,
            description=f"{self.about} 분석 결과",
        )
        analysis.result_image.save(f"analysis_{analysis.id}.png", ContentFile(buffer.read()), save=True)
        buffer.close()

        return analysis
