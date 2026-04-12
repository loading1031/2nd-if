# /monitoring — 모니터링 확인

Grafana Cloud 모니터링 상태를 확인하고 관리한다.

## 사용법

```
/monitoring status — 헬스체크 + 모니터링 상태 확인
/monitoring dashboard — 대시보드 JSON 업데이트/Import 안내
```

## 실행 절차

### 0. 전제조건 체크

1. **curl 가능 여부 확인**:
```bash
curl --version
```
- 실패 시: "curl이 설치되지 않았습니다." 안내 후 종료

2. **Railway 연결 상태 확인** (로그 확인이 필요한 경우):
```bash
$(yarn global bin)/railway whoami
```
- 실패 시: "Railway에 로그인되지 않았습니다. 로그 확인을 건너뜁니다." 안내 후 헬스체크만 진행

### status

1. 프로덕션 헬스체크 확인:
```bash
curl -s -o /dev/null -w "%{http_code}" https://2nd-if-production.up.railway.app/health/
```
- 200이면 상세 응답 확인:
```bash
curl -s https://2nd-if-production.up.railway.app/health/ | python -m json.tool
```

2. Railway 로그에서 Alloy 관련 에러 확인:
```bash
$(yarn global bin)/railway logs | grep -i "alloy\|metrics\|loki" | tail -20
```

3. 결과 보고:
   - `/health/` 응답 (db, neo4j 상태)
   - Alloy push 에러 유무
   - Grafana Cloud 대시보드 접속 URL 안내

#### 헬스체크 실패 시 대응 절차

헬스체크가 200이 아닌 경우 다음 순서로 대응:

1. **응답 코드별 판단**:
   - `000` (연결 불가): 서비스가 내려간 상태 → Railway 로그 즉시 확인
   - `500`: 서버 내부 에러 → 로그에서 traceback 확인
   - `502/503`: 서비스 재시작 중이거나 크래시 → Railway 배포 상태 확인

2. **Railway 로그 확인**:
```bash
$(yarn global bin)/railway logs --tail 50
```

3. **서비스 재시작 안내**:
   - "Railway 대시보드에서 서비스를 재시작할 수 있습니다."
   - Railway 대시보드 → 프로젝트 → Settings → Restart
   - 또는 최신 커밋으로 재배포: `railway up`

4. **에스컬레이션**:
   - 재시작 후에도 실패하면 `/deploy logs`로 상세 로그 확인 안내
   - DB 연결 실패인 경우 Railway 대시보드에서 DB 서비스 상태 확인 안내

### dashboard

1. `docs/grafana/dashboard.json` 파일 확인
2. 현재 수집 중인 메트릭 목록 안내
3. Grafana Cloud Import 방법 안내:
   - Dashboards → New → Import → JSON 붙여넣기

## 주요 메트릭 목록

현재 수집 중인 메트릭:

| 메트릭 | 설명 | 타입 |
|--------|------|------|
| `django_http_requests_total` | HTTP 요청 총 수 (method, status별) | Counter |
| `django_http_requests_latency_seconds` | HTTP 요청 응답 시간 | Histogram |
| `django_http_exceptions_total` | HTTP 예외 발생 수 | Counter |
| `django_db_query_duration_seconds` | DB 쿼리 실행 시간 | Histogram |
| `django_db_query_total` | DB 쿼리 총 수 | Counter |
| `process_cpu_seconds_total` | 프로세스 CPU 사용 시간 | Counter |
| `process_resident_memory_bytes` | 프로세스 메모리 사용량 | Gauge |

> 메트릭이 추가/변경되면 이 목록도 함께 갱신할 것.

## Grafana Cloud 접속
- 대시보드: https://secondary.grafana.net
- Explore (메트릭): 데이터소스 secondary-prom → django_http_requests_total
- Explore (로그): 데이터소스 grafanacloud-logs → {app="2nd-if"}

## 주의사항
- 헬스체크는 프로덕션 URL에만 수행 (dev 환경 아님)
- Grafana Cloud 접속 권한은 별도 관리
- 메트릭이 안 보이면 Alloy 설정 및 push 상태를 먼저 확인
- 헬스체크 실패 시 즉시 로그 확인 → 원인 파악 → 필요 시 재시작 순서로 대응
