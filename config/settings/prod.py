# config/settings/prod.py
from .base import *
import os

DEBUG = False

# Render 도메인 허용 (.onrender.com 전체)
ALLOWED_HOSTS = [
    ".onrender.com",
    "localhost",
    "127.0.0.1",
]

# CSRF 설정 (Render 서비스 도메인 추가)
CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
]

# CORS 설정 (프론트엔드 배포 도메인 있으면 같이 추가)
CORS_ALLOWED_ORIGINS = [
    "https://*.onrender.com",
]
CORS_ALLOW_CREDENTIALS = True

# 정적 파일 설정 (production용)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# WhiteNoise 설정
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False   # 프로덕션에서는 보통 False로 두는 게 성능상 유리

# 로깅 레벨 조정 (배포에서는 ERROR 이상만 출력)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "ERROR",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "ERROR",
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.staticfiles": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
