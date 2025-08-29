from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.notifications"

    def ready(self):
        # 시그널 등록
        from . import signals  # noqa: F401
