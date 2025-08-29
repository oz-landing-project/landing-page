from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """커스텀 사용자 모델 - 이메일을 기본 인증 필드로 사용"""

    email = models.EmailField('이메일', unique=True)
    nickname = models.CharField('닉네임', max_length=50, unique=True)
    name = models.CharField('이름', max_length=100)
    birth_date = models.DateField('생년월일', null=True, blank=True)
    phone = models.CharField('연락처', max_length=20, blank=True)
    profile_image = models.ImageField('프로필 이미지', upload_to='profiles/', null=True, blank=True)

    # 소셜 로그인 관련 필드
    social_provider = models.CharField('소셜 제공자', max_length=20, blank=True)
    social_id = models.CharField('소셜 ID', max_length=100, blank=True)

    # 계정 상태 관리
    is_verified = models.BooleanField('이메일 인증', default=False)
    verification_token = models.CharField('인증 토큰', max_length=255, blank=True)

    # 계정 활동 정보
    last_login_ip = models.GenericIPAddressField('최종 로그인 IP', null=True, blank=True)
    login_count = models.PositiveIntegerField('로그인 횟수', default=0)

    created_at = models.DateTimeField('생성일시', auto_now_add=True)
    updated_at = models.DateTimeField('수정일시', auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nickname', 'name']

    class Meta:
        db_table = 'users'
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'

    def __str__(self):
        return f"{self.nickname} ({self.email})"