from django.contrib import admin
from .models import Analysis


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'analysis_period', 'total_income', 'total_expense', 'savings_amount', 'period_start', 'period_end']
    list_filter = ['analysis_period', 'period_start', 'period_end']
    search_fields = ['user__nickname', 'user__email', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'period_start'