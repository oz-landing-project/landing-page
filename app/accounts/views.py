# app/accounts/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q  # ← Sum 제거

from .models import Account, TransactionHistory
from .serializers import AccountSerializer, TransactionHistorySerializer


# -----------------------------------
# 1. 계좌 뷰셋
# - 계좌 생성/조회/수정/삭제
# - 주계좌(primary) 설정 기능 추가
# -----------------------------------
class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """로그인한 사용자의 계좌만 조회"""
        return Account.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        """계좌 생성 시 소유자 자동 주입"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def set_primary(self, request, pk=None):
        """
        [POST] /api/accounts/{id}/set_primary/
        → 해당 계좌를 주계좌로 설정
        """
        account = self.get_object()

        if account.user != request.user:
            return Response(
                {"detail": "본인 계좌만 변경할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 기존 주계좌 해제 후 현재 계좌를 주계좌로
        Account.objects.filter(user=request.user).update(is_primary=False)
        account.is_primary = True
        account.save(update_fields=["is_primary"])

        return Response(
            {"detail": f"{account.account_name} 계좌가 주계좌로 설정되었습니다."},
            status=status.HTTP_200_OK,
        )


# -----------------------------------
# 2. 거래내역 뷰셋 (조회 전용)
# - 지원: 목록(list), 상세(retrieve)
# - 미지원: 생성/수정/삭제/통계
# -----------------------------------
class TransactionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    거래내역 조회 전용
    - 필터:
      ?q=검색어            (설명/메모)
      ?type=DEPOSIT        (거래유형)
      ?account=3           (특정 계좌)
      ?start=YYYY-MM-DD    (이후)
      ?end=YYYY-MM-DD      (이전)
    """
    serializer_class = TransactionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = TransactionHistory.o
