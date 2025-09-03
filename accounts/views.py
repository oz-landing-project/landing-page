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


# 1. AccountViewSet - 계좌 CRUD 및 주계좌 설정
class AccountViewSet(viewsets.ModelViewSet):
    """
    계좌 정보 CRUD 및 주계좌 설정을 위한 뷰셋
    - `/accounts/`: 계좌 목록 조회, 생성
    - `/accounts/<pk>/`: 특정 계좌 조회, 수정, 삭제
    - `/accounts/<pk>/set_primary/`: 주계좌 설정
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """요청한 사용자의 계좌만 반환"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """새로운 계좌 생성 시 사용자 자동 할당"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], url_path='set-primary')
    def set_primary(self, request, pk=None):
        """특정 계좌를 주계좌로 설정하고 기존 주계좌 해제"""
        account = self.get_object()
        
        # 기존 주계좌를 찾아 is_primary를 False로 설정
        current_primary_account = self.get_queryset().filter(is_primary=True).first()
        if current_primary_account and current_primary_account != account:
            current_primary_account.is_primary = False
            current_primary_account.save()
            
        # 선택한 계좌를 주계좌로 설정
        account.is_primary = True
        account.save()
        
        return Response({'status': '주계좌로 설정되었습니다.'}, status=status.HTTP_200_OK)


# 2. TransactionHistoryViewSet - 거래내역 조회 및 통계
class TransactionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    거래내역 조회 및 통계 기능을 제공하는 뷰셋
    - `/accounts/transactions/`: 모든 계좌의 거래내역 조회
    - `/accounts/<pk>/transactions/`: 특정 계좌의 거래내역 조회
    """
    queryset = TransactionHistory.objects.all()
    serializer_class = TransactionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """요청한 사용자의 거래내역만 반환"""
        return self.queryset.filter(account__user=self.request.user)

    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        """일별 거래 금액 합산 통계"""
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({"error": "날짜(date)를 지정해주세요. (YYYY-MM-DD)"}, status=status.HTTP_400_BAD_REQUEST)

        # 해당 날짜의 거래내역만 필터링
        queryset = self.get_queryset().filter(transaction_date__date=date_str)
        
        # 입금과 출금 금액 합산
        summary = queryset.aggregate(
            total_deposit=Sum('amount', filter=Q(transaction_type='DEPOSIT')),
            total_withdraw=Sum('amount', filter=Q(transaction_type='WITHDRAW'))
        )
        
        return Response({
            "date": date_str,
            "total_deposit": summary['total_deposit'] or 0,
            "total_withdraw": summary['total_withdraw'] or 0
        }, status=status.HTTP_200_OK)