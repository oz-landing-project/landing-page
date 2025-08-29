from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Account, TransactionHistory
from .serializers import AccountSerializer, TransactionHistorySerializer


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_accounts = Account.objects.filter(user=self.request.user)
        return TransactionHistory.objects.filter(account__in=user_accounts)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """최근 거래내역 조회"""
        queryset = self.get_queryset()[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)