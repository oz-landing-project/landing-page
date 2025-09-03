# 배포환경
from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = ['3.107.1.63', 'localhost', '127.0.0.1']

# CSRF 설정
CSRF_TRUSTED_ORIGINS = [
    'http://3.107.1.63:8000',
    'https://3.107.1.63:8000',
]

# CORS 설정
CORS_ALLOWED_ORIGINS = [
    "http://3.107.1.63:8000",
    "https://3.107.1.63:8000",
]
CORS_ALLOW_CREDENTIALS = True

# 정적 파일 설정 (production용)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# WhiteNoise 설정
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# 로깅 레벨 조정 (경고 메시지 줄이기)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',  # INFO에서 ERROR로 변경
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',  # INFO에서 ERROR로 변경
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.staticfiles': {
            'handlers': ['console'],
            'level': 'ERROR',  # 정적 파일 경고 숨기기
            'propagate': False,
        },
    },
}
