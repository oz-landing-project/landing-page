#!/usr/bin/env bash
# ------------------------------------------------------------
# deploy.sh — Django(Gunicorn) + Nginx 배포 자동화 스크립트
#   - Ubuntu/Debian 기준
#   - 프로젝트 루트에서 실행
# ------------------------------------------------------------
set -euo pipefail

### ───────────────────────── 사용자 환경 변수 ─────────────────────────
# 프로젝트 이름(서비스/유닛/폴더명에 사용)
PROJECT_NAME="landing"
# 프로젝트 절대 경로(이 스크립트를 두고 실행할 경로)
PROJECT_DIR="/srv/landing"
# 배포 사용자(소스 소유자)와 그룹
RUN_USER="ubuntu"
RUN_GROUP="www-data"
# 도메인 또는 서버 공인 IP (Nginx server_name)
SERVER_NAME="example.com"          # 예: "myapp.com" 또는 "1.2.3.4"
# 바인딩 주소(내부 Gunicorn 리스닝 주소)
GUNICORN_BIND="127.0.0.1:8000"
# Gunicorn 워커 수
GUNICORN_WORKERS="3"
# WSGI 엔드포인트 (프로젝트에 맞게 수정)
WSGI_APP="config.wsgi:application"
# Django 설정 모듈 (prod 설정)
DJANGO_SETTINGS="config.settings.prod"

### ───────────────────────── 파생 경로(수정 불필요) ─────────────────────────
VENV_DIR="$PROJECT_DIR/.venv"
LOG_DIR="$PROJECT_DIR/logs"
STATIC_ROOT="$PROJECT_DIR/staticfiles"
MEDIA_ROOT="$PROJECT_DIR/media"
SYSTEMD_SERVICE="/etc/systemd/system/gunicorn-${PROJECT_NAME}.service"
NGINX_SITE="/etc/nginx/sites-available/${PROJECT_NAME}"
NGINX_SITE_LINK="/etc/nginx/sites-enabled/${PROJECT_NAME}"
ENV_DIR="/etc/${PROJECT_NAME}"
ENV_FILE="${ENV_DIR}/${PROJECT_NAME}.env"

echo "==> [1/9] 필수 패키지 설치 (sudo 필요)"
sudo apt-get update -y
sudo apt-get install -y python3-venv python3-pip nginx

echo "==> [2/9] 디렉터리 준비"
sudo mkdir -p "$PROJECT_DIR" "$LOG_DIR" "$STATIC_ROOT" "$MEDIA_ROOT" "$ENV_DIR"
sudo chown -R "$RUN_USER":"$RUN_GROUP" "$PROJECT_DIR"
sudo chown -R "$RUN_USER":"$RUN_GROUP" "$ENV_DIR"

# (선택) .env를 시스템 위치로 백업/복사
if [[ -f "$PROJECT_DIR/.env" ]]; then
  echo "==> .env -> $ENV_FILE 복사"
  sudo cp "$PROJECT_DIR/.env" "$ENV_FILE"
  sudo chown "$RUN_USER":"$RUN_GROUP" "$ENV_FILE"
fi

echo "==> [3/9] 파이썬 가상환경/의존성 설치"
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi
# 의존성 설치 (requirements.txt + gunicorn)
"$VENV_DIR/bin/pip" install --upgrade pip wheel
if [[ -f "$PROJECT_DIR/requirements.txt" ]]; then
  "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
fi
"$VENV_DIR/bin/pip" install gunicorn

echo "==> [4/9] Django 마이그레이션 & 정적파일 수집"
# DJANGO_SETTINGS_MODULE을 환경 변수로 주입
export DJANGO_SETTINGS="$DJANGO_SETTINGS"
cd "$PROJECT_DIR"
# .env가 있다면 로드(단순 키=값 라인만 대상으로 함)
if [[ -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
fi
# prod 설정 지정
export DJANGO_SETTINGS_MODULE="$DJANGO_SETTINGS"
"$VENV_DIR/bin/python" manage.py migrate --noinput
"$VENV_DIR/bin/python" manage.py collectstatic --noinput

echo "==> [5/9] systemd 서비스 파일 생성: $SYSTEMD_SERVICE"
sudo tee "$SYSTEMD_SERVICE" > /dev/null <<EOF
# /etc/systemd/system/gunicorn-${PROJECT_NAME}.service
[Unit]
Description=Gunicorn for ${PROJECT_NAME}
After=network.target

[Service]
User=${RUN_USER}
Group=${RUN_GROUP}
WorkingDirectory=${PROJECT_DIR}
Environment="DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS}"
EnvironmentFile=${ENV_FILE}
ExecStart=${VENV_DIR}/bin/gunicorn --workers ${GUNICORN_WORKERS} --bind ${GUNICORN_BIND} ${WSGI_APP}
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "==> [6/9] Nginx 서버 블록 생성: $NGINX_SITE"
sudo tee "$NGINX_SITE" > /dev/null <<'EOF'
# /etc/nginx/sites-available/landing
server {
    listen 80;
    server_name SERVER_NAME_PLACEHOLDER;

    # 접근/에러 로그
    access_log PROJECT_DIR_PLACEHOLDER/logs/nginx_access.log;
    error_log  PROJECT_DIR_PLACEHOLDER/logs/nginx_error.log;

    # 정적/미디어 파일
    location /static/ {
        alias PROJECT_DIR_PLACEHOLDER/staticfiles/;
    }
    location /media/ {
        alias PROJECT_DIR_PLACEHOLDER/media/;
    }

    # 애플리케이션 프록시 -> Gunicorn
    location / {
        proxy_pass http://GUNICORN_BIND_PLACEHOLDER;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60;
    }
}
EOF

# 자리표시자 치환
sudo sed -i "s|SERVER_NAME_PLACEHOLDER|$SERVER_NAME|g" "$NGINX_SITE"
sudo sed -i "s|PROJECT_DIR_PLACEHOLDER|$PROJECT_DIR|g" "$NGINX_SITE"
sudo sed -i "s|GUNICORN_BIND_PLACEHOLDER|$GUNICORN_BIND|g" "$NGINX_SITE"

echo "==> [7/9] Nginx 사이트 활성화"
# 기본 사이트 비활성화(있다면)
if [[ -f /etc/nginx/sites-enabled/default ]]; then
  sudo rm -f /etc/nginx/sites-enabled/default
fi
sudo ln -sf "$NGINX_SITE" "$NGINX_SITE_LINK"
sudo nginx -t

echo "==> [8/9] 서비스 기동/재시작"
sudo systemctl daemon-reload
sudo systemctl enable "gunicorn-${PROJECT_NAME}.service"
sudo systemctl restart "gunicorn-${PROJECT_NAME}.service"
sudo systemctl restart nginx

echo "==> [9/9] 상태 확인"
echo "---- Gunicorn ----"
sudo systemctl status "gunicorn-${PROJECT_NAME}.service" --no-pager || true
echo "---- Nginx ----"
sudo systemctl status nginx --no-pager || true

echo
echo "✅ 배포 완료!"
echo "브라우저에서:  http://${SERVER_NAME}/  확인하세요."
echo
echo "유용한 명령어:"
echo "  sudo journalctl -u gunicorn-${PROJECT_NAME} -f   # Gunicorn 로그 팔로우"
echo "  sudo tail -f ${LOG_DIR}/nginx_error.log         # Nginx 에러 로그"
