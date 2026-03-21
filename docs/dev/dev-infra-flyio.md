# Fly.io 배포 가이드

> 개발 문서

## 상태: 구현 완료

## 기획
- [[infra]] — 인프라 기획

## 사전 준비

### 1. Fly.io CLI 설치
```bash
curl -L https://fly.io/install.sh | sh
flyctl auth login
```

### 2. 초기 설정
```bash
./scripts/fly-setup.sh
```

### 3. 환경변수 설정
```bash
flyctl secrets set \
  SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')" \
  NEO4J_BOLT_URL="neo4j+s://neo4j:PASSWORD@ID.databases.neo4j.io" \
  ALLOWED_HOSTS=".fly.dev"
```

### 4. 마이그레이션
```bash
flyctl ssh console -C 'cd /app/server && uv run python manage.py migrate'
flyctl ssh console -C 'cd /app/server && uv run python manage.py createsuperuser'
```

## 배포

### 수동 배포
```bash
flyctl deploy --remote-only
```

### 자동 배포
main 브랜치 push 시 GitHub Actions가 자동 배포.
`FLY_API_TOKEN` 시크릿을 GitHub repo에 설정 필요:
```bash
flyctl tokens create deploy -x 999999h
# → GitHub Settings > Secrets > FLY_API_TOKEN에 저장
```

## 유용한 명령어
```bash
flyctl status              # 앱 상태
flyctl logs                # 실시간 로그
flyctl ssh console         # SSH 접속
flyctl scale memory 512    # 메모리 스케일업
flyctl postgres connect -a 2nd-if-db  # DB 접속
```
