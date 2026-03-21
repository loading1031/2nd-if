# Grafana Cloud 연동 가이드

> 개발 문서

## 상태: 구현 완료

## 기획
- [[monitoring]] — 모니터링 기획
- [[infra]] — 인프라 기획

## 개요
Grafana Alloy 사이드카가 Django `/metrics/` scrape + 로그 파일 tail → Grafana Cloud로 push.

## 아키텍처
```
Django /metrics/ ← Alloy scrape (60s) → Grafana Cloud Prometheus
Django /data/logs/django.log ← Alloy tail → Grafana Cloud Loki
```

## 구현 파일
| 파일 | 역할 |
|------|------|
| `docker/alloy/config.alloy` | Alloy 설정 (scrape + tail → push) |
| `scripts/start.sh` | Alloy 백그라운드 시작 |
| `server/apps/monitoring/middleware.py` | 요청 메트릭 수집 |
| `server/apps/monitoring/views.py` | `/health/`, `/metrics/` 엔드포인트 |
| `server/config/settings/prod.py` | 로깅 → 파일 출력 (RotatingFileHandler) |
| `docs/grafana/dashboard.json` | 대시보드 JSON (Import용) |

## Grafana Cloud 계정 설정

### 1. 가입
https://grafana.com/auth/sign-up/create-user

### 2. Access Policy 토큰 발급
대시보드 → **Administration** → **Access Policies** → **Create access policy**
- Scope: `metrics:write`, `logs:write`
- **Add token** → 토큰 복사

### 3. Prometheus 정보 확인
Grafana Cloud 대시보드 → Stack → **Prometheus** → **Details**
- Remote Write Endpoint URL
- Username (숫자 ID)

### 4. Loki 정보 확인
Stack → **Loki** → **Details**
- URL (호스트만, 경로 불포함)
- Username (숫자 ID)

### 5. Railway 환경변수
| 변수 | 예시 |
|------|------|
| `GRAFANA_CLOUD_API_KEY` | `glc_...` |
| `GRAFANA_CLOUD_PROM_URL` | `https://prometheus-prod-xx.grafana.net/api/prom/push` |
| `GRAFANA_CLOUD_PROM_USER` | `123456` |
| `GRAFANA_CLOUD_LOKI_URL` | `https://logs-prod-xx.grafana.net` |
| `GRAFANA_CLOUD_LOKI_USER` | `123456` |

## 대시보드 Import
1. Grafana 대시보드 → **Dashboards** → **New** → **Import**
2. `docs/grafana/dashboard.json` 내용 붙여넣기
3. Import

## 조회 방법
- **메트릭**: Explore → secondary-prom → `django_http_requests_total`
- **로그**: Explore → grafanacloud-logs → `{app="2nd-if"}`
- **대시보드**: Dashboards → 2nd-if Django

## 무료 한도
| 항목 | 한도 |
|------|------|
| 메트릭 (Prometheus) | 10,000 series, 14일 보존 |
| 로그 (Loki) | 50GB/월, 14일 보존 |
| 알림 | 무제한 |
| 사용자 | 3명 |
| 기간 | **영구 무료** (크레딧 아님) |
