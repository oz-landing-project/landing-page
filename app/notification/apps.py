from django.apps import AppConfig


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.notification'  # 수정: app.notification으로 변경
    verbose_name = '알림'

    def ready(self):
        import app.notification.signals  # 수정: 경로도 변경