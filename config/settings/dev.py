#개발환경

from .base import *

DEBUG = True
ALLOWED_HOSTS = []


# config/settings/dev.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # 필수: PostgreSQL 사용
        'NAME': 'landing_project_db',               # 데이터베이스 이름
        'USER': 'postgres',                         # 사용자
        'PASSWORD': '@qwer@1',                     # 비밀번호
        'HOST': '127.0.0.1',                        # 또는 'localhost'
        'PORT': '5432',                             # Postgres 포트
    }
}
