from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, TransactionHistoryViewSet

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'transactions', TransactionHistoryViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
]