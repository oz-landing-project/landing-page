#!/bin/bash

# 배포 스크립트
echo "🚀 배포를 시작합니다..."

# 1. 의존성 설치
echo "📦 의존성 설치 중..."
pip install -r requirements.txt

# 2. 데이터베이스 마이그레이션
echo "🗄️ 데이터베이스 마이그레이션 중..."
python manage.py migrate --settings=config.settings.prod

# 3. 정적 파일 수집
echo "📁 정적 파일 수집 중..."
python manage.py collectstatic --noinput --settings=config.settings.prod

# 4. 서버 시작
echo "🌟 서버 시작..."
gunicorn --workers 3 --bind 0.0.0.0:8000 config.wsgi:application --env DJANGO_SETTINGS_MODULE=config.settings.prod

echo "✅ 배포 완료!"