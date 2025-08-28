from django.urls import path
from .views import UserTransactionHistoryView, AdminTransactionHistoryView, AnalysisView

urlpatterns = [
    path('api/transaction/', UserTransactionHistoryView.as_view(), name='user-transaction'),
    path('api/transaction/admin/', AdminTransactionHistoryView.as_view(), name='admin-transaction'),
]
