# config/settings/prod.py
from .base import *
import os

# ---- 기본 플래그 ------------------------------------------------------------
# 배포에선 기본 False, 필요 시 Render Env에서 DEBUG=True 로 임시 변경 가능
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ---- 호스트/도메인 ----------------------------------------------------------
# Render 기본 도메인 허용 (+ 로컬 확인용)
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    ".onrender.com,localhost,127.0.0.1"
).split(",")

# CSRF (Swagger/프론트 접속 도메인 추가 가능: 콤마로 여러 개)
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS",
    "https://*.onrender.com"
).split(",")

# CORS (필요 시 프론트 배포 도메인 추가)
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "https://*.onrender.com"
).split(",")
CORS_ALLOW_CREDENTIALS = True

# ---- 보안 헤더 (프록시 뒤 HTTPS 환경) ---------------------------------------
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# ---- 정적 파일 (WhiteNoise) ------------------------------------------------
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False  # 프로덕션 캐시 성능 ↑

# ---- 데이터베이스 -----------------------------------------------------------
# base.py에서 ENV로 DATABASES를 구성하도록 돼 있음.
# Render Postgres는 일반적으로 SSL 필요 → sslmode=require 강제
if DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
    # sslmode이 이미 지정되어 있지 않다면 추가
    opts = DATABASES["default"].setdefault("OPTIONS", {})
    opts.setdefault("sslmode", "require")

# ---- 로깅 (프로덕션: ERROR 이상만) ------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler", "level": "ERROR"},
    },
    "root": {"handlers": ["console"], "level": "ERROR"},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "django.staticfiles": {"handlers": ["console"], "level": "ERROR", "propagate": False},
    },
}
