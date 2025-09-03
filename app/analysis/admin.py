from django.contrib import admin
from .models import Analysis

@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "about", "type", "period_start", "period_end", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("about", "user__email", "user__nickname")
    readonly_fields = ("created_at", "updated_at")
