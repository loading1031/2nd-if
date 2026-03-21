# /deploy — Railway 배포 관리

Railway 배포 관련 작업을 수행한다.

## 사용법

```
/deploy status — 배포 상태 확인
/deploy logs — 실시간 로그 확인
/deploy vars — 환경변수 확인
/deploy run <command> — 프로덕션에서 명령 실행
```

## 실행 절차

### status
```bash
$(yarn global bin)/railway status
```

### logs
```bash
$(yarn global bin)/railway logs
```

### vars
```bash
$(yarn global bin)/railway variables
```

### run
```bash
$(yarn global bin)/railway run <사용자가 지정한 명령>
```

## 주의사항
- `railway login`이 안 되어 있으면 먼저 로그인 안내
- `railway link`가 안 되어 있으면 프로젝트 연결 안내
- 환경변수 변경은 Railway 대시보드에서 직접 수행 (CLI로 하지 않음)
- 배포는 git push로 자동 트리거 (수동 배포: `railway up`)
