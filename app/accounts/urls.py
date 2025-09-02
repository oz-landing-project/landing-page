# 구현할 URL 패턴들
#
# 구현해야 할 URL들:
# router = DefaultRouter()
# router.register(r'', AccountViewSet, basename='account')
# router.register(r'transactions', TransactionHistoryViewSet, basename='transaction')

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AccountViewSet, TransactionHistoryViewSet

# 라우터 생성 후 뷰셋 등록
# /api/accounts/              -> Account 목록/생성 (GET/POST)
# /api/accounts/{id}/         -> Account 상세/수정/삭제 (GET/PUT/PATCH/DELETE)
# /api/accounts/{id}/set_primary/ -> 주계좌 설정 (POST)

# /api/accounts/transactions/             -> 거래내역 목록/생성 (GET/POST)
# /api/accounts/transactions/{id}/        -> 거래내역 상세 (GET) 및 삭제/수정 정책에 따라 제한
# /api/accounts/transactions/summary/     -> 거래 통계 (GET)  (custom action)
router = DefaultRouter()
router.register(r'', AccountViewSet, basename='account')
router.register(r'transactions', TransactionHistoryViewSet, basename='transaction')


urlpatterns = [
    # 여기에 URL 패턴들을 추가하세요
    path('', include(router.urls)),
]