# 모니터링 시스템

> 기획 문서

## 상태: 구현 완료

## 개요

Grafana Cloud + Grafana Alloy 기반 모니터링 시스템.
Django 앱의 성능, 가용성, 비즈니스 메트릭을 수집하고 시각화한다.

## 아키텍처

```
Django App (:8000)
  ├── /metrics/  ← Prometheus 텍스트 포맷 노출
  ├── /health/   ← 헬스체크 JSON (DB + Neo4j)
  └── /data/logs/django.log ← 파일 로그 (RotatingFileHandler)

Grafana Alloy (사이드카, 같은 컨테이너)
  ├── localhost:8000/metrics/ scrape (60초) → Grafana Cloud Prometheus push
  └── /data/logs/django.log tail → Grafana Cloud Loki push

Grafana Cloud (SaaS, 영구 무료)
  ├── Prometheus — 메트릭 저장/조회 (10K series, 14일)
  ├── Loki — 로그 저장/조회 (50GB/월, 14일)
  └── Dashboard — 시각화/알림
```

## 의사결정 기록

### Alloy 사이드카 선택 이유
- 로컬 docker-compose: Prometheus가 `/metrics/`를 직접 pull (텍스트 포맷 OK)
- Grafana Cloud: push 필요 → Prometheus remote write (snappy+protobuf) 필수
- Django에서 직접 push 구현: 복잡 (protobuf 인코딩 필요)
- **Alloy**: 공식 경량 에이전트. pull→push 변환 자동 처리. 같은 컨테이너에서 백그라운드 실행

### 로그 수집: 파일 tail 방식
- Django logging → RotatingFileHandler (`/data/logs/django.log`, 10MB×3 백업)
- Alloy가 파일을 tail해서 Loki로 push
- 최대 디스크 사용: 40MB

## 수집 메트릭

### 인프라 메트릭 (미들웨어 자동 수집)

| 메트릭 | 타입 | 설명 |
|--------|------|------|
| `django_http_requests_total` | Counter | 총 HTTP 요청 수 (method, path, status별) |
| `django_http_request_duration_seconds` | Histogram | HTTP 요청 지연시간 |
| `django_http_requests_active` | Gauge | 현재 처리 중인 요청 수 |

### 비즈니스 메트릭 (애플리케이션 코드에서 수동 갱신)

| 메트릭 | 타입 | 설명 |
|--------|------|------|
| `app_story_views_total` | Counter | 작품 조회 수 |
| `app_branch_creations_total` | Counter | 분기 생성 수 |
| `app_story_ratings_total` | Counter | 평점 제출 수 |
| `app_active_users` | Gauge | 활성 사용자 수 (주기적 갱신) |

### 헬스체크 메트릭

| 메트릭 | 타입 | 설명 |
|--------|------|------|
| `app_db_up` | Gauge | Django DB 연결 상태 (1=정상, 0=장애) |
| `app_neo4j_up` | Gauge | Neo4j 연결 상태 (1=정상, 0=장애) |

## 구현 파일

| 파일 | 역할 |
|------|------|
| `server/apps/monitoring/middleware.py` | 요청 메트릭 수집 (PrometheusMetricsMiddleware) |
| `server/apps/monitoring/exporters.py` | 비즈니스/헬스 메트릭 정의 |
| `server/apps/monitoring/views.py` | `/health/`, `/metrics/` 엔드포인트 |
| `docker/alloy/config.alloy` | Alloy 설정 (scrape + tail → push) |
| `scripts/start.sh` | 컨테이너 시작 (migrate → Alloy → gunicorn) |
| `docs/grafana/dashboard.json` | Grafana 대시보드 JSON (Import용) |

## 알림 규칙 (향후 구현 예정)

| 조건 | 심각도 | 알림 채널 |
|------|--------|----------|
| 5xx 에러율 > 5% (5분간) | critical | Slack |
| p99 응답시간 > 5초 (5분간) | warning | Slack |
| Neo4j 연결 실패 (3분 이상) | critical | Slack |
| Django DB 연결 실패 (1분 이상) | critical | Slack |

## 의존성
- [[infra]] — Railway 배포, Grafana Cloud 계정

## 개발 문서
- [[dev-monitoring]] — 모니터링 시스템 개발 가이드
- [[dev-grafana-cloud]] — Grafana Cloud 연동 가이드
