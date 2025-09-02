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
