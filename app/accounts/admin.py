from django.contrib import admin
from .models import Account, TransactionHistory


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_number', 'bank_code', 'account_type', 'balance', 'created_at']
    list_filter = ['account_type', 'bank_code', 'created_at']
    search_fields = ['user__nickname', 'user__email', 'account_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TransactionHistory)
class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ['account', 'transaction_type', 'amount', 'balance_after', 'transaction_date']
    list_filter = ['transaction_type', 'detail_type', 'transaction_date']
    search_fields = ['account__user__nickname', 'transaction_detail']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'transaction_date'