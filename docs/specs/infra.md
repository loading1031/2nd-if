# 인프라

> 기획 문서

## 상태: 기획 완료

## 개요
2nd-if 플랫폼의 인프라 구성. 무료 티어 SaaS 중심으로 비용 $0 운영.

## 아키텍처

### 서비스 구성
| 서비스 | 호스팅 | 티어 | 비용 |
|--------|--------|------|------|
| Django (ASGI) | Fly.io | Free (256MB VM) | $0 |
| PostgreSQL | Fly.io Postgres | Free (256MB, 1GB disk) | $0 |
| Neo4j (그래프 DB) | Neo4j Aura | Free (200K nodes) | $0 |
| 메트릭/로그/대시보드 | Grafana Cloud | Free (10K series, 50GB logs) | $0 |
| 미디어 파일 | Fly.io Volume | 1GB | $0 |
| CI/CD | GitHub Actions | Free (2000분/월) | $0 |
| CDN | Fly.io 내장 | 글로벌 엣지 | $0 |

### 네트워크 흐름
```
User → Fly.io Edge (nrt) → Django (Gunicorn+Uvicorn)
                              ├── Fly Postgres (SQL)
                              ├── Neo4j Aura (Graph)
                              ├── Fly Volume (Media)
                              └── → Grafana Cloud (Metrics/Logs push)
```

## 환경변수
| 변수 | 설명 | 예시 |
|------|------|------|
| SECRET_KEY | Django 시크릿 키 | (자동 생성) |
| DATABASE_URL | PostgreSQL 연결 | postgres://... (Fly가 자동 설정) |
| NEO4J_BOLT_URL | Neo4j Aura 연결 | neo4j+s://...@xxx.databases.neo4j.io |
| ALLOWED_HOSTS | 허용 호스트 | .fly.dev,your-domain.com |
| DJANGO_SETTINGS_MODULE | 설정 모듈 | config.settings.prod |
| GRAFANA_CLOUD_API_KEY | Grafana Cloud API 키 | glc_... |
| GRAFANA_CLOUD_PROM_URL | Prometheus remote write URL | https://...grafana.net/api/prom/push |
| GRAFANA_CLOUD_LOKI_URL | Loki push URL | https://...grafana.net/loki/api/v1/push |

## 스케일링 계획
| 단계 | 트래픽 | 조치 |
|------|--------|------|
| MVP | ~100 DAU | 현재 구성 유지 |
| 성장기 | ~1K DAU | Fly VM 512MB로 업그레이드, Postgres 스케일업 |
| 확장기 | ~10K DAU | AWS 이전 (Terraform), 전용 DB |

## 의존성
- [[auth]] — 소셜 로그인 OAuth 설정
- [[monitoring]] — Grafana Cloud 연동
- [[story]] — Neo4j Aura 연결

## 디자인 문서
- (해당 없음 — 인프라는 디자인 문서 불필요)
