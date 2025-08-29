from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'message', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__nickname', 'user__email', 'message']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        for notification in queryset:
            notification.mark_as_read()
        self.message_user(request, f'{queryset.count()}개의 알림을 읽음으로 표시했습니다.')
    mark_as_read.short_description = '선택된 알림을 읽음으로 표시'