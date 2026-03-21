# /monitoring — 모니터링 확인

Grafana Cloud 모니터링 상태를 확인하고 관리한다.

## 사용법

```
/monitoring status — 헬스체크 + 모니터링 상태 확인
/monitoring dashboard — 대시보드 JSON 업데이트/Import 안내
```

## 실행 절차

### status
1. 프로덕션 헬스체크 확인:
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

### dashboard
1. `docs/grafana/dashboard.json` 파일 확인
2. 현재 수집 중인 메트릭 목록 안내
3. Grafana Cloud Import 방법 안내:
   - Dashboards → New → Import → JSON 붙여넣기

## Grafana Cloud 접속
- 대시보드: https://secondary.grafana.net
- Explore (메트릭): 데이터소스 secondary-prom → django_http_requests_total
- Explore (로그): 데이터소스 grafanacloud-logs → {app="2nd-if"}
