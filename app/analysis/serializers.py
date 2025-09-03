# app/analysis/serializers.py
from rest_framework import serializers
from io import BytesIO
import pandas as pd
from django.core.files.base import ContentFile
from app.analysis.models import Analysis

# matplotlib은 설치 전에도 서버 임포트가 죽지 않게 '선행 시도'만 하고,
# 실제 그리기 시점에 없으면 친절한 에러를 내도록 처리
try:
    import matplotlib
    matplotlib.use("Agg")  # 서버/도커/CI에서도 안전한 백엔드
    import matplotlib.pyplot as plt
except Exception:  # 설치 전이면 여기로 떨어짐
    plt = None


class AnalysisRunRequestSerializer(serializers.Serializer):
    """분석 실행 요청 검증"""
    about = serializers.CharField(max_length=100)
    type = serializers.ChoiceField(choices=[c[0] for c in Analysis.PERIOD_TYPE_CHOICES])
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    description = serializers.CharField(allow_blank=True, required=False)

    def validate(self, attrs):
        if attrs["period_start"] > attrs["period_end"]:
            raise serializers.ValidationError("period_start가 period_end보다 뒤일 수 없습니다.")
        return attrs


class AnalysisSerializer(serializers.ModelSerializer):
    """분석 결과 응답"""
    result_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Analysis
        fields = [
            "id", "user", "about", "type",
            "period_start", "period_end",
            "description", "created_at", "updated_at",
            "result_image_url",
        ]
        read_only_fields = ("id", "user", "created_at", "updated_at", "result_image_url")

    def get_result_image_url(self, obj):
        request = self.context.get("request")
        if obj.result_image and hasattr(obj.result_image, "url"):
            url = obj.result_image.url
            return request.build_absolute_uri(url) if request else url
        return None


class AnalysisExecuteSerializer(AnalysisRunRequestSerializer):
    """
    검증 + DataFrame(pandas) 생성 + 시각화(matplotlib) + 저장까지 한 번에.
    view의 get_serializer_context()에서 'transactions' QuerySet을 반드시 주입하세요.
    """

    # ---- DataFrame 생성 (필드명은 프로젝트 거래모델에 맞게 조정) ----
    @staticmethod
    def _make_dataframe(
        qs,
        *,
        date_key="transaction_date",   # 예: "date"
        category_key="category",       # 예: "transaction_category"
        amount_key="amount",           # 예: "price"
        type_key="transaction_type",   # 예: "type"
    ):
        data = list(qs.values(date_key, category_key, amount_key, type_key))
        if not data:
            return None, (date_key, category_key, amount_key, type_key)
        df = pd.DataFrame(data)
        # 날짜 캐스팅
        df[date_key] = pd.to_datetime(df[date_key])
        return df, (date_key, category_key, amount_key, type_key)

    # ---- 차트 렌더링 → ContentFile ----
    @staticmethod
    def _render_chart(df, *, category_key, amount_key, title="Category Spending"):
        if plt is None:
            raise serializers.ValidationError("서버에 matplotlib가 설치되어 있지 않습니다.")
        fig = plt.figure(figsize=(8, 6))
        try:
            summary = df.groupby(category_key)[amount_key].sum().sort_index()
            summary.plot(kind="bar", title=title)
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            buf = BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            return ContentFile(buf.read(), name="analysis_result.png")
        finally:
            plt.close(fig)

    # ---- 생성 로직 ----
    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        qs = self.context.get("transactions")
        if qs is None:
            raise serializers.ValidationError("transactions QuerySet이 누락되었습니다.")

        # ⚠️ 여기 키들은 너희 거래 모델 필드명에 맞춰 필요한 경우 바꿔주세요.
        df, keys = self._make_dataframe(qs)
        if df is None:
            raise serializers.ValidationError("해당 기간에 거래내역이 없습니다.")
        _date_key, category_key, amount_key, _type_key = keys

        img = self._render_chart(df, category_key=category_key, amount_key=amount_key, title=validated_data["about"])

        analysis = Analysis.objects.create(
            user=user,
            about=validated_data["about"],
            type=validated_data["type"],
            period_start=validated_data["period_start"],
            period_end=validated_data["period_end"],
            description=validated_data.get("description", ""),
            result_image=img,
        )
        return analysis
