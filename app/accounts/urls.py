from django.urls import path, include, URLResolver, URLPattern
from rest_framework.routers import DefaultRouter

from .views import AccountViewSet, TransactionHistoryViewSet

router = DefaultRouter()
router.register(r'', AccountViewSet, basename='account')
router.register(r'transactions', TransactionHistoryViewSet, basename='transaction')

urlpatterns: list[URLResolver | URLPattern] = [
    path('', include(router.urls)),
]
# 구현할 URL 패턴들
#
# 구현해야 할 URL들:
# router = DefaultRouter()
# router.register(r'', AccountViewSet, basename='account')
# router.register(r'transactions', TransactionHistoryViewSet, basename='transaction')

