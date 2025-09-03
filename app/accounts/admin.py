from django.contrib import admin
from .models import Account, TransactionHistory


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_number', 'bank_code', 'account_type', 'balance', 'created_at']
    list_filter = ['account_type', 'bank_code', 'created_at']
    search_fields = ['account_number']  # 일단 user 관련 검색 제거
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TransactionHistory)
class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ['account', 'transaction_type', 'amount', 'balance_after', 'transaction_date']
    list_filter = ['transaction_type', 'detail_type', 'transaction_date']
    search_fields = ['description']  # 일단 account__user 관련 검색 제거
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'transaction_date'