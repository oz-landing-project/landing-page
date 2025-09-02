from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from app.analysis.models import Analysis
from app.analysis.serializers import (
    AnalysisSerializer,
    AnalysisExecuteSerializer,
)

# 거래 모델 임포트(이름이 다를 수 있어 유연하게)
try:
    from app.accounts.models import TransactionHistory as Tx
except Exception:
    try:
        from app.accounts.models import Transaction as Tx
    except Exception:
        Tx = None

class AnalysisView(ListCreateAPIView):
    """
    분석 관리 API
    
    GET: 내 분석 목록 조회
    POST: 분석 실행 & 저장
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Swagger 스키마 생성 시 AnonymousUser 처리
        if getattr(self, 'swagger_fake_view', False):
            return Analysis.objects.none()
        return Analysis.objects.filter(user=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        return AnalysisExecuteSerializer if self.request.method == "POST" else AnalysisSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if self.request.method == "POST" and Tx is not None:
            start = self.request.data.get("period_start")
            end   = self.request.data.get("period_end")
            if start and end:
                # NOTE: 날짜/필드명은 프로젝트에 맞게 조정
                qs = Tx.objects.filter(
                    account__user=self.request.user,
                    transaction_date__range=[start, end],
                )
                ctx["transactions"] = qs
        return ctx

    @swagger_auto_schema(
        operation_description="분석 목록 조회",
        responses={200: AnalysisSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="새로운 분석 실행",
        request_body=AnalysisExecuteSerializer,
        responses={201: AnalysisSerializer}
    )
    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        analysis = s.save()  # Analysis 인스턴스
        out = AnalysisSerializer(analysis, context={"request": request}).data
        return Response(out, status=status.HTTP_201_CREATED)


class AnalysisDetailView(RetrieveAPIView):
    """분석 상세 조회"""
    permission_classes = [IsAuthenticated]
    serializer_class = AnalysisSerializer

    def get_queryset(self):
        # Swagger 스키마 생성 시 AnonymousUser 처리
        if getattr(self, 'swagger_fake_view', False):
            return Analysis.objects.none()
        return Analysis.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="분석 상세 정보 조회",
        responses={200: AnalysisSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
