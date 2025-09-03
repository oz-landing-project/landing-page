from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.users'  # 수정: app.users로 변경
    verbose_name = '사용자 관리'