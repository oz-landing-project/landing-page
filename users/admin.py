from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """커스텀 사용자 관리자"""

    list_display = (
        'email', 'nickname', 'name', 'is_verified',
        'is_active', 'login_count', 'created_at'
    )
    list_filter = (
        'is_verified', 'is_active', 'is_staff',
        'social_provider', 'created_at'
    )
    search_fields = ('email', 'nickname', 'name', 'username')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('개인정보', {'fields': ('username', 'nickname', 'name', 'birth_date', 'phone', 'profile_image')}),
        ('소셜 로그인', {'fields': ('social_provider', 'social_id')}),
        ('계정 상태', {'fields': ('is_active', 'is_verified', 'verification_token')}),
        ('권한', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('활동 정보', {'fields': ('last_login', 'last_login_ip', 'login_count', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'nickname', 'name', 'password1', 'password2'),
        }),
    )