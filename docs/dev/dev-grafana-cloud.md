# Grafana Cloud 연동 가이드

> 개발 문서

## 상태: 미구현

## 기획
- [[monitoring]] — 모니터링 기획
- [[infra]] — 인프라 기획

## 개요
기존 셀프호스팅 Prometheus+Grafana를 Grafana Cloud Free 티어로 전환.
Django에서 메트릭과 로그를 Grafana Cloud로 push.

## 구현 위치
- 설정: `server/config/settings/prod.py`
- 로그: `server/apps/monitoring/log_config.py` (새 파일)
- 미들웨어: `server/apps/monitoring/middleware.py` (기존 유지)

## 설정 방법

### 1. Grafana Cloud 계정 생성
1. https://grafana.com/auth/sign-up/create-user 에서 가입
2. Stack 생성 (region: ap-southeast-1 또는 us-central-1)
3. API Key 발급 (Grafana.com > My Account > API Keys > Add API Key)

### 2. Prometheus Remote Write
Grafana Cloud에서 Prometheus 연결 정보 확인:
- Remote Write Endpoint: `https://prometheus-prod-xx.grafana.net/api/prom/push`
- Username: (숫자 ID)
- Password: API Key

### 3. Loki Log Push
별도 패키지 (python-logging-loki 등)로 Django 로그를 Loki에 push.

### 4. 환경변수
```bash
flyctl secrets set \
  GRAFANA_CLOUD_API_KEY="glc_..." \
  GRAFANA_CLOUD_PROM_URL="https://..." \
  GRAFANA_CLOUD_LOKI_URL="https://..."
```

## 무료 한도
| 항목 | 한도 |
|------|------|
| 메트릭 | 10,000 series, 14일 보존 |
| 로그 | 50GB/월, 14일 보존 |
| 트레이스 | 50GB/월 |
| 알림 | 무제한 |
| 사용자 | 3명 |
