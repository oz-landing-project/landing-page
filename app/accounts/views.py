# 구현할 API 뷰들
#
# 구현해야 할 뷰들:
# 1. AccountViewSet - 계좌 CRUD 및 주계좌 설정
# 2. TransactionHistoryViewSet - 거래내역 조회 및 통계
#
# 필요한 import들:
# from rest_framework import viewsets, permissions, status
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from django.db.models import Q, Sum
# from .models import Account, TransactionHistory
# from .serializers import AccountSerializer, TransactionHistorySerializer

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum
from .models import Account, TransactionHistory
from .serializers import AccountSerializer, TransactionHistorySerializer


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 로그인한 사용자 계좌만 조회
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'], url_path='set-primary')
    def set_primary(self, request, pk=None):
        """
        해당 계좌를 주계좌로 설정
        """
        account = self.get_object()

        # 주계좌가 아닌지, 그리고 사용자 소유인지 확인
        if account.user != request.user:
            return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

        if account.is_primary:
            return Response({'detail': '이미 주계좌입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        # 기존 주계좌 해제
        Account.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
        # 선택한 계좌를 주계좌로 설정
        account.is_primary = True
        account.save(update_fields=['is_primary'])

        return Response({'detail': '주계좌로 설정되었습니다.'}, status=status.HTTP_200_OK)


class TransactionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 로그인한 사용자의 거래내역만 조회
        return TransactionHistory.objects.filter(account__user=self.request.user).order_by('-transaction_date')

    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """
        거래내역 통계 예시: 총 입금액, 총 출금액, 거래 건수 등
        기간 필터링 가능 (query params: start_date, end_date)
        """
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        transactions = TransactionHistory.objects.filter(account__user=user)
        if start_date:
            transactions = transactions.filter(transaction_date__gte=start_date)
        if end_date:
            transactions = transactions.filter(transaction_date__lte=end_date)

        total_deposit = transactions.filter(transaction_type='DEPOSIT').aggregate(total=Sum('amount'))['total'] or 0
        total_withdraw = transactions.filter(transaction_type='WITHDRAW').aggregate(total=Sum('amount'))['total'] or 0
        total_count = transactions.count()

        data = {
            'total_deposit': total_deposit,
            'total_withdraw': total_withdraw,
            'total_transactions': total_count,
        }
        return Response(data, status=status.HTTP_200_OK)
