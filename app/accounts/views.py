from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum
from .models import Account, TransactionHistory
from .serializers import AccountSerializer, TransactionHistorySerializer


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def set_primary(self, request, pk=None):
        account = self.get_object()
        # 기존 주계좌 해제
        Account.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
        # 새 주계좌 설정
        account.is_primary = True
        account.save()
        return Response({'message': '주계좌로 설정되었습니다.'})


class TransactionHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TransactionHistory.objects.filter(account__user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            total_deposits=Sum('amount', filter=Q(transaction_type='DEPOSIT')),
            total_withdrawals=Sum('amount', filter=Q(transaction_type='WITHDRAW'))
        )
        return Response(stats)