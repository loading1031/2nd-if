# 인프라

> 기획 문서

## 상태: 기획 완료

## 개요
2nd-if 플랫폼의 인프라 구성. 무료 티어 SaaS 중심으로 비용 $0 운영.
규모 확장 시 AWS 이전(Terraform)을 염두에 두되, MVP 단계에서는 관리 부담을 최소화한다.

## 의사결정 기록

### Fly.io 선택 이유 (vs AWS EC2, Railway)
- **AWS EC2**: Terraform으로 완전한 IaC 가능하나, 프리티어 1년 한정. 1인 개발에 서버 관리 부담.
- **Railway**: Git push 배포로 간편하나 Terraform 미지원. 무료 $5 크레딧/월로 부족할 수 있음.
- **Fly.io**: Docker 배포 + 글로벌 엣지 + 256MB VM 무료. Terraform provider는 커뮤니티 수준이나 `fly.toml`로 충분. 규모 커지면 AWS 이전 용이 (Docker 기반이므로).

### Grafana Cloud 선택 이유 (vs 셀프호스팅 Prometheus+Grafana)
- 셀프호스팅 시 Prometheus(200MB) + Grafana(150MB) + Loki(200MB) = 550MB 추가. 256MB VM에서 불가능.
- Grafana Cloud Free 티어는 **영구 무료** (크레딧 소진 방식 아님). 10K series + 50GB 로그/월.
- 셀프호스팅 모니터링 코드는 로컬 개발용으로 유지 (`docker-compose.monitoring.yml`).

### Neo4j Aura 선택 이유 (vs 셀프호스팅 Neo4j)
- Neo4j 컨테이너는 최소 500MB RAM 필요. Fly 256MB VM에서 불가능.
- Aura Free: 200K 노드, 400K 관계, 영구 무료. MVP에 충분.

## 아키텍처

### 서비스 구성
| 서비스 | 호스팅 | 티어 | 월 비용 |
|--------|--------|------|---------|
| Django (ASGI) | Fly.io | Free (256MB VM, shared CPU) | $0 |
| PostgreSQL | Fly.io Postgres | Free (256MB, 1GB disk) | $0 |
| Neo4j (그래프 DB) | Neo4j Aura | Free (200K nodes, 400K rels) | $0 |
| 메트릭/로그/대시보드 | Grafana Cloud | Free (10K series, 50GB logs) | $0 |
| 미디어 파일 | Fly.io Volume | 1GB | $0 |
| CI/CD | GitHub Actions | Free (2000분/월) | $0 |
| CDN | Fly.io 내장 | 글로벌 엣지 | $0 |
| **합계** | | | **$0** |

### 네트워크 흐름
```
User → Fly.io Edge (nrt/Tokyo) → Django (Gunicorn+Uvicorn, 2 workers)
                                    ├── Fly Postgres (SQL, 같은 리전)
                                    ├── Neo4j Aura (Graph, 외부)
                                    ├── Fly Volume (Media, 1GB)
                                    └── → Grafana Cloud (Metrics/Logs push)
```

## 무료 티어 상세 한도

### Fly.io
| 항목 | 무료 한도 | 초과 시 |
|------|----------|---------|
| VM | shared-cpu-1x, 256MB × 3개 | $1.94/mo per 256MB |
| Bandwidth | 100GB outbound/월 | $0.02/GB |
| Volumes | 1GB (3개까지) | $0.15/GB/mo |
| Postgres | 256MB, 1GB disk (1 인스턴스) | 유료 플랜 전환 |

### Neo4j Aura
| 항목 | 무료 한도 | 초과 시 |
|------|----------|---------|
| 노드 | 200,000개 | 유료 플랜 ($65/mo~) |
| 관계 | 400,000개 | 유료 플랜 |
| 인스턴스 | 1개 | 유료 플랜 |
| RAM | 256MB | 유료 플랜 |
| 백업 | 자동 | - |
| 기간 | **영구 무료** | - |

### Grafana Cloud
| 항목 | 무료 한도 | 초과 시 |
|------|----------|---------|
| 메트릭 (Prometheus) | 10,000 active series, 14일 보존 | $8/1K series/mo |
| 로그 (Loki) | 50GB/월, 14일 보존 | $0.50/GB |
| 트레이스 (Tempo) | 50GB/월, 14일 보존 | $0.50/GB |
| 알림 | 무제한 | - |
| 대시보드 | 무제한 | - |
| 사용자 | 3명 | $8/user/mo |
| 기간 | **영구 무료** (크레딧 아님) | - |

### GitHub Actions
| 항목 | 무료 한도 | 초과 시 |
|------|----------|---------|
| 실행 시간 | 2,000분/월 (Linux) | $0.008/min |
| 스토리지 | 500MB (Artifacts) | $0.25/GB |

## 비용 시뮬레이션

### MVP (~100 DAU) — **$0/월**
모든 서비스 무료 한도 내. 별도 비용 없음.

### 성장기 (~1K DAU) — **$5~15/월**
| 항목 | 예상 변경 | 추가 비용 |
|------|----------|----------|
| Fly VM | 256MB → 512MB | ~$3.88/mo |
| Fly Postgres | 256MB → 512MB | ~$7/mo |
| Neo4j Aura | 무료 한도 내 (노드 ~50K) | $0 |
| Grafana Cloud | 무료 한도 내 | $0 |
| Bandwidth | ~50GB/월 | $0 |

### 확장기 (~10K DAU) — **$50~100/월, AWS 이전 검토**
| 항목 | 예상 변경 | 추가 비용 |
|------|----------|----------|
| 컴퓨팅 | Fly → AWS EC2 (t3.small) | ~$18/mo |
| DB | RDS PostgreSQL (db.t3.micro) | ~$15/mo |
| Neo4j | Aura Pro | ~$65/mo |
| 모니터링 | Grafana Cloud Free 유지 가능 | $0 |
| CDN | CloudFront | ~$5/mo |
| IaC | Terraform으로 전환 | - |

## 환경변수
| 변수 | 설명 | 예시 | 설정 방법 |
|------|------|------|----------|
| SECRET_KEY | Django 시크릿 키 | (자동 생성) | `flyctl secrets set` |
| DATABASE_URL | PostgreSQL 연결 | postgres://... | Fly가 `postgres attach` 시 자동 설정 |
| NEO4J_BOLT_URL | Neo4j Aura 연결 | neo4j+s://...@xxx.databases.neo4j.io | `flyctl secrets set` |
| ALLOWED_HOSTS | 허용 호스트 | .fly.dev,your-domain.com | `flyctl secrets set` |
| DJANGO_SETTINGS_MODULE | 설정 모듈 | config.settings.prod | `fly.toml` env |
| GRAFANA_CLOUD_API_KEY | Grafana Cloud API 키 | glc_... | `flyctl secrets set` |
| GRAFANA_CLOUD_PROM_URL | Prometheus remote write URL | https://...grafana.net/api/prom/push | `flyctl secrets set` |
| GRAFANA_CLOUD_LOKI_URL | Loki push URL | https://...grafana.net/loki/api/v1/push | `flyctl secrets set` |
| EMAIL_HOST_USER | SMTP 이메일 | noreply@2nd-if.com | `flyctl secrets set` |
| EMAIL_HOST_PASSWORD | SMTP 비밀번호 | (앱 비밀번호) | `flyctl secrets set` |

## 스케일링 계획
| 단계 | 트래픽 | 월 비용 | 조치 |
|------|--------|---------|------|
| MVP | ~100 DAU | $0 | 현재 구성 유지 |
| 성장기 | ~1K DAU | $5~15 | Fly VM/Postgres 스케일업 |
| 확장기 | ~10K DAU | $50~100 | AWS 이전 (Terraform), 전용 DB |
| 대규모 | ~100K DAU | $300~500 | K8s, 멀티 리전, CDN 강화 |

## 의존성
- [[auth]] — 소셜 로그인 OAuth 설정
- [[monitoring]] — Grafana Cloud 연동
- [[story]] — Neo4j Aura 연결

## 디자인 문서
- (해당 없음 — 인프라는 디자인 문서 불필요)

## 개발 문서
- [[dev-infra-flyio]] — Fly.io 배포 가이드
- [[dev-grafana-cloud]] — Grafana Cloud 연동 가이드
