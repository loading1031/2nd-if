# Railway 배포 가이드

> 개발 문서

## 상태: 미구현

## 기획
- [[infra]] — 인프라 기획

## 사전 준비

### 1. Railway CLI 설치
```bash
npm install -g @railway/cli
railway login
```

### 2. 프로젝트 생성
```bash
railway init
# 또는 Railway 대시보드에서 GitHub 리포 연결
```

### 3. Postgres 추가
Railway 대시보드 → 프로젝트 → **+ New** → **Database** → **PostgreSQL**
→ `DATABASE_URL`이 자동으로 환경변수에 추가됨

### 4. 환경변수 설정
Railway 대시보드 → 서비스 → **Variables** 탭:
```
SECRET_KEY=<python -c "import secrets; print(secrets.token_urlsafe(50))">
DJANGO_SETTINGS_MODULE=config.settings.prod
NEO4J_BOLT_URL=neo4j+s://neo4j:<PASSWORD>@<ID>.databases.neo4j.io
ALLOWED_HOSTS=.up.railway.app
PORT=8000
```

### 5. 마이그레이션
```bash
railway run python server/manage.py migrate
railway run python server/manage.py createsuperuser
```

## 배포

### 자동 배포 (권장)
Railway 대시보드에서 GitHub 리포 연결 → main push 시 자동 배포.

### 수동 배포
```bash
railway up
```

### GitHub Actions 자동 배포
1. Railway 대시보드 → **Settings** → **Tokens** → 토큰 생성
2. GitHub repo → **Settings** → **Secrets** → `RAILWAY_TOKEN` 추가
3. main push → CI 테스트 → Railway 배포

## 유용한 명령어
```bash
railway status          # 프로젝트 상태
railway logs            # 실시간 로그
railway run <command>   # 프로덕션에서 명령 실행
railway open            # 브라우저에서 앱 열기
railway variables       # 환경변수 확인
```

## 비용 관리
- Railway 대시보드 → **Usage** 탭에서 크레딧 소진량 확인
- $5 크레딧 중 Django + Postgres = 약 $2~3/월 (MVP 트래픽 기준)
- 크레딧 소진 시 서비스 중지, 다음 달 1일에 리셋

## 로컬 개발 vs 프로덕션
| | 로컬 | 프로덕션 |
|--|------|---------|
| Django | `docker compose -f docker-compose.dev.yml up` | Railway |
| PostgreSQL | SQLite (dev.py) | Railway Postgres |
| Neo4j | Docker 컨테이너 (localhost:7687) | Neo4j Aura Free |
| 미디어 | 로컬 디스크 | Railway Volume |
