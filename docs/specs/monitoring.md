# 모니터링 시스템

> 기획 문서

## 상태: 기획 완료

## 개요

Prometheus + Grafana 기반 모니터링 시스템으로 2nd-if 플랫폼의 성능, 가용성, 비즈니스 메트릭을 수집하고 시각화한다.

## 아키텍처

```
Django App (:8000)
  ├── /metrics/  ← Prometheus 스크래핑 엔드포인트
  └── /health/   ← 헬스체크 엔드포인트 (JSON)

Prometheus (:9090)
  └── 15초 간격으로 /metrics/ 스크래핑

Grafana (:3000)
  └── Prometheus를 데이터소스로 대시보드 시각화
```

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

## Grafana 대시보드 패널

1. **Request Rate** — 초당 요청 수 (method별)
2. **Response Time** — p50, p95, p99 응답 시간
3. **Error Rate** — 4xx, 5xx 에러 비율
4. **Active Users** — 활성 사용자 수
5. **Story Views per hour** — 시간당 작품 조회 수
6. **Branch Creation Rate** — 시간당 분기 생성 수
7. **Neo4j Health** — Neo4j 연결 상태
8. **Database Health** — Django DB 연결 상태
9. **Database Query Time** — 평균 요청 처리 시간

## 알림 규칙 (향후 구현 예정)

| 조건 | 심각도 | 알림 채널 |
|------|--------|----------|
| 5xx 에러율 > 5% (5분간) | critical | Slack |
| p99 응답시간 > 5초 (5분간) | warning | Slack |
| Neo4j 연결 실패 (3분 이상) | critical | Slack |
| Django DB 연결 실패 (1분 이상) | critical | Slack |

## 디자인 문서

- (해당 없음 — 인프라 기능이므로 UI 디자인 불필요)

## 개발 문서

- [[dev-monitoring]] — 모니터링 시스템 개발 가이드
