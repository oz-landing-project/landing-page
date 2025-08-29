from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Analysis
from .serializers import AnalysisSerializer


class AnalysisViewSet(viewsets.ModelViewSet):
    serializer_class = AnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Analysis.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """최신 분석 결과 조회"""
        latest_analysis = self.get_queryset().first()
        if latest_analysis:
            serializer = self.get_serializer(latest_analysis)
            return Response(serializer.data)
        return Response({'message': '분석 결과가 없습니다.'})