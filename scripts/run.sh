#!/bin/bash

echo "Django 개발 서버를 시작합니다"

# .env 파일이 없으면 생성
if [ ! -f .env ]; then
    echo ".env 파일을 생성합니다"
    cp .env.example .env
fi

# 의존성 설치
echo "의존성을 설치합니다"
uv sync

# PostgreSQL 자동 시작 (macOS)
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "PostgreSQL을 시작합니다"
    if command -v brew &> /dev/null; then
        brew services start postgresql@15 2>/dev/null || brew services start postgresql 2>/dev/null
        sleep 3
    fi
fi

# 데이터베이스 생성 (존재하지 않으면)
DB_NAME=${DB_NAME:-landing_project_db}
if ! psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME 2>/dev/null; then
    echo "데이터베이스를 생성합니다."
    createdb $DB_NAME 2>/dev/null || echo "데이터베이스가 이미 존재하거나 생성할 수 없습니다."
fi

# 마이그레이션
echo "마이그레이션을 실행합니다"
export DJANGO_SETTINGS_MODULE=config.settings.dev
uv run python manage.py makemigrations
uv run python manage.py migrate

# 서버 실행
echo "개발 서버를 시작합니다... (http://localhost:8000)"
uv run python manage.py runserver 0.0.0.0:8000