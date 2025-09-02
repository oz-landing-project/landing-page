from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Account, TransactionHistory
from .serializers import AccountSerializer, TransactionHistorySerializer


class AccountViewSet(viewsets.ModelViewSet):
    """
    계좌 관리 API
    
    계좌 생성, 조회, 수정, 삭제 기능을 제공합니다.
    """
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    거래내역 조회 API
    
    사용자의 거래내역을 조회할 수 있습니다.
    """
    serializer_class = TransactionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_accounts = Account.objects.filter(user=self.request.user)
        return TransactionHistory.objects.filter(account__in=user_accounts)

    @swagger_auto_schema(
        operation_description="최근 거래내역 10건 조회",
        responses={200: TransactionHistorySerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """최근 거래내역 조회"""
        queryset = self.get_queryset()[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)