# 실행 방법

## 0. 포스트그래스@15버전 설치!!!!!!!!!!
brew install postgresql@15
brew services start postgresql@15

## 1. 환경 설정
```bash
cp .env.example .env
# .env 파일에서 DB_USER를 본인 사용자명으로 변경 (whoami 명령어로 확인)
```

## 2. 서버 실행
```bash
chmod +x scripts/run.sh && ./scripts/run.sh
```


