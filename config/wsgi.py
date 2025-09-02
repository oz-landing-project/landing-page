"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# ---- Python Path 추가 (app 폴더 인식) ----
BASE_DIR = Path(__file__).resolve().parent.parent
app_path = BASE_DIR / "app"
if str(app_path) not in sys.path:
    sys.path.insert(0, str(app_path))

# ---- Django Settings 모듈 지정 ----
# 기본값: 배포환경(prod)
# 로컬 개발 시 환경변수 DJANGO_SETTINGS_MODULE=config.settings.dev 로 덮어쓰기 가능
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

# ---- WSGI Application ----
application = get_wsgi_application()
