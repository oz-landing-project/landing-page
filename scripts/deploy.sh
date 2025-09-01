#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/ubuntu/landing"  # 서버의 프로젝트 경로
VENV_DIR="$APP_DIR/.venv"
DJANGO_SETTINGS="config.settings.prod"

cd "$APP_DIR"
source "$VENV_DIR/bin/activate"

# 패키지 동기화 (uv 사용 시)
if command -v uv >/dev/null 2>&1; then
  uv pip install -r requirements.txt
else
  pip install -r requirements.txt
fi

python manage.py migrate --settings="$DJANGO_SETTINGS"
python manage.py collectstatic --noinput --settings="$DJANGO_SETTINGS"

sudo systemctl restart gunicorn
sudo systemctl reload nginx || true

echo "✅ Deploy done."
