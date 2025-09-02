from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    커스텀 사용자 모델
    
    기본 Django User 모델을 확장하여 추가 필드를 포함합니다.
    """
    
    # 기본 정보
    email = models.EmailField('이메일', unique=True, db_index=True)
    nickname = models.CharField('닉네임', max_length=50, unique=True, db_index=True)
    name = models.CharField('이름', max_length=100)
    birth_date = models.DateField('생년월일', null=True, blank=True)
    phone = models.CharField('연락처', max_length=20, blank=True)
    
    # 프로필 관련
    profile_image = models.ImageField(
        '프로필 이미지', 
        upload_to='profiles/%Y/%m/', 
        null=True, 
        blank=True
    )
    bio = models.TextField('자기소개', max_length=500, blank=True)
    
    # 소셜 로그인 관련 (확장 가능)
    social_provider = models.CharField('소셜 제공자', max_length=20, blank=True)
    social_id = models.CharField('소셜 ID', max_length=100, blank=True)
    
    # 계정 상태 관리
    is_verified = models.BooleanField('이메일 인증', default=False)
    verification_token = models.CharField('인증 토큰', max_length=255, blank=True)
    
    # 활동 정보
    last_login_ip = models.GenericIPAddressField('최종 로그인 IP', null=True, blank=True)
    login_count = models.PositiveIntegerField('로그인 횟수', default=0)
    
    # 타임스탬프
    created_at = models.DateTimeField('생성일시', auto_now_add=True)
    updated_at = models.DateTimeField('수정일시', auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nickname', 'name']
    
    class Meta:
        db_table = 'users'
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['nickname']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.nickname} ({self.email})"
    
    @property
    def full_name(self):
        """전체 이름 반환"""
        return self.name or self.username
    
    def get_profile_image_url(self):
        """프로필 이미지 URL 반환"""
        if self.profile_image:
            return self.profile_image.url
        return None