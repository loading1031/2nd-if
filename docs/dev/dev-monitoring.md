# 모니터링 시스템 개발 가이드

> 개발 문서

## 상태: 구현 완료

## 기획

- [[monitoring]] — 모니터링 시스템 기획 문서

## 구현 위치

- 앱: `server/apps/monitoring/`
- 미들웨어: `server/apps/monitoring/middleware.py`
- 커스텀 메트릭: `server/apps/monitoring/exporters.py`
- URL: `GET /metrics/`, `GET /health/`
- Docker 설정: `docker/monitoring/`
- Compose 파일: `docker-compose.monitoring.yml`

## 실행 방법

### 모니터링 서비스 시작

```bash
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up
```

> Docker Compose 오버라이드 방식으로, 기존 `docker-compose.yml`과 함께 모니터링 서비스를 추가로 실행한다.

모니터링만 단독 실행도 가능:

```bash
docker compose -f docker-compose.monitoring.yml up
```

### 접속 URL

| 서비스 | URL | 인증 |
|--------|-----|------|
| Django 메트릭 | http://localhost:8000/metrics/ | 없음 |
| Django 헬스체크 | http://localhost:8000/health/ | 없음 |
| Prometheus | http://localhost:9090 | 없음 |
| Grafana | http://localhost:3000 | admin / admin |

### Django 설정 (메인 에이전트가 통합)

다음 항목을 기존 설정 파일에 추가해야 한다:

1. `INSTALLED_APPS`에 `"apps.monitoring"` 추가
2. `MIDDLEWARE`에 `"apps.monitoring.middleware.PrometheusMetricsMiddleware"` 추가
3. `config/urls.py`에 `path("", include("apps.monitoring.urls"))` 추가
4. `pyproject.toml`에 `prometheus-client` 의존성 추가

## 커스텀 메트릭 추가 방법

### 1. exporters.py에 메트릭 정의

```python
from prometheus_client import Counter

MY_METRIC = Counter(
    "app_my_metric_total",
    "Description of what this metric tracks",
)
```

### 2. 애플리케이션 코드에서 메트릭 갱신

```python
from apps.monitoring.exporters import MY_METRIC

async def my_view(request):
    # 비즈니스 로직 실행 후
    MY_METRIC.inc()
    ...
```

### 3. Grafana 대시보드에 패널 추가

`docker/monitoring/grafana/dashboards/django-app.json`에 새 패널을 추가하거나, Grafana UI에서 직접 편집 후 JSON을 내보낼 수 있다.

## 메트릭 네이밍 규칙

| 접두어 | 용도 | 예시 |
|--------|------|------|
| `django_http_` | Django HTTP 인프라 메트릭 | `django_http_requests_total` |
| `app_` | 애플리케이션/비즈니스 메트릭 | `app_story_views_total` |

## 미들웨어 동작

`PrometheusMetricsMiddleware`는 모든 HTTP 요청에 대해:

1. 활성 요청 게이지 증가
2. 요청 시작 시간 기록
3. 응답 완료 후 지연시간 히스토그램 기록
4. method/path/status별 요청 카운터 증가
5. 활성 요청 게이지 감소

path는 `/stories/42/branches/7/` → `/stories/{id}/branches/{id}/`로 정규화하여 카디널리티를 제한한다.

## 선행 작업

- prometheus-client Python 라이브러리 설치
- Docker / Docker Compose 설치
