#배포환경

from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = ['*']  # 실제 배포 도메인

# Swagger UI / Redoc 설정 (개발용)
SPECTACULAR_SETTINGS = {
    "TITLE": "Landing API",
    "DESCRIPTION": "가계부 API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {"persistAuthorization": True},

    # Sidecar 리소스 사용(템플릿/정적 파일 제공)
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",

    # (선택) API Key / 세션 쿠키 인증 스킴을 문서에 노출
    "SECURITY_SCHEMES": {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": os.getenv("API_KEY_HEADER", "X-API-Key"),
            "description": "형식: 키 값만 입력 (예: abc123)",
        },
        "CookieAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "sessionid",
        },
    },
    "SECURITY": [{"ApiKeyAuth": []}, {"CookieAuth": []}],
}
