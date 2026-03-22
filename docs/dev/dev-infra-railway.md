# Railway 배포 가이드

> 개발 문서

## 상태: 구현 완료

## 기획
- [[infra]] — 인프라 기획

## 사전 준비

### 1. Railway CLI 설치
```bash
yarn global add @railway/cli
railway login
```

### 2. 프로젝트 연결
```bash
railway link    # 프로젝트 선택
railway service # 서비스 선택
```

### 3. 환경변수 설정
Railway 대시보드 → 서비스 → **Variables** 탭:

| 변수 | 값 |
|------|-----|
| `DJANGO_SETTINGS_MODULE` | `config.settings.prod` |
| `SECRET_KEY` | (랜덤 문자열) |
| `ALLOWED_HOSTS` | `.up.railway.app,healthcheck.railway.app,localhost` |
| `PORT` | `8000` |
| `NEO4J_BOLT_URL` | `neo4j+s://...@....databases.neo4j.io` |
| `GRAFANA_CLOUD_PROM_URL` | Prometheus remote write URL |
| `GRAFANA_CLOUD_PROM_USER` | Prometheus username (숫자 ID) |
| `GRAFANA_CLOUD_LOKI_URL` | Loki URL (호스트만, 경로 불포함) |
| `GRAFANA_CLOUD_LOKI_USER` | Loki username (숫자 ID) |
| `GRAFANA_CLOUD_API_KEY` | Access policy 토큰 |

### 4. Public Domain 생성
대시보드 → 서비스 → **Settings** → **Networking** → **Generate Domain**

## 배포

### 자동 배포
GitHub dev 브랜치 push → Railway 자동 빌드/배포.

### 배포 프로세스 (Dockerfile)
```
1. Builder: Python deps + Node deps + Tailwind CSS 빌드 + collectstatic
2. Runtime: Python deps + Alloy 바이너리 + 앱 코드
3. CMD: migrate → Alloy(백그라운드) → gunicorn(포그라운드)
```

### 수동 배포
```bash
railway up
```

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
- Hobby $5/월 크레딧 중 Django + SQLite = 약 $1~2/월 (MVP 트래픽)

## 로컬 개발 vs 프로덕션
| | 로컬 | 프로덕션 |
|--|------|---------|
| Django | `python manage.py runserver` | Railway (Gunicorn+Uvicorn) |
| DB | SQLite (server/db.sqlite3) | SQLite (Railway Volume /data/) |
| Neo4j | Docker 컨테이너 (localhost:7687) | Neo4j Aura Free |
| 모니터링 | docker-compose (로컬 Prometheus+Grafana) | Grafana Cloud + Alloy |
| 미디어 | 로컬 디스크 | Railway Volume /data/media |
