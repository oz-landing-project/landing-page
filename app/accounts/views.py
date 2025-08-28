from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import TransactionHistory
from .serializers import TransactionHistorySerializer

# -------------------------
# 일반 유저 전용 거래내역
# -------------------------
class UserTransactionHistoryView(generics.ListCreateAPIView):
    serializer_class = TransactionHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 로그인한 유저의 계좌에 속한 거래내역만 조회
        return TransactionHistory.objects.filter(account__user=self.request.user)

    def perform_create(self, serializer):
        # 새 거래내역 추가 시, 본인 계좌에만 추가 가능
        account = serializer.validated_data["account"]
        if account.user != self.request.user:
            raise PermissionError("본인 계좌에만 거래내역을 추가할 수 있습니다.")
        serializer.save()

    def delete(self, request, *args, **kwargs):
        transaction_id = request.data.get("id")
        try:
            transaction = TransactionHistory.objects.get(id=transaction_id, account__user=request.user)
            transaction.delete()
            return Response({"message": "삭제 성공"}, status=status.HTTP_204_NO_CONTENT)
        except TransactionHistory.DoesNotExist:
            return Response({"error": "거래내역이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)


# -------------------------
# 관리자 전용 거래내역
# -------------------------
class AdminTransactionHistoryView(generics.ListCreateAPIView):
    queryset = TransactionHistory.objects.all()
    serializer_class = TransactionHistorySerializer
    permission_classes = [IsAdminUser]  # ✅ 관리자만 접근 가능

    def delete(self, request, *args, **kwargs):
        transaction_id = request.data.get("id")
        try:
            transaction = TransactionHistory.objects.get(id=transaction_id)
            transaction.delete()
            return Response({"message": "삭제 성공"}, status=status.HTTP_204_NO_CONTENT)
        except TransactionHistory.DoesNotExist:
            return Response({"error": "거래내역이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)



