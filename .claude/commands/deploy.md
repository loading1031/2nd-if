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

### 0. 전제조건 체크

모든 하위 명령 실행 전 아래 항목을 순서대로 확인:

1. **Railway CLI 설치 확인**:
```bash
$(yarn global bin)/railway version
```
- 실패 시: "Railway CLI가 설치되지 않았습니다. `yarn global add @railway/cli`로 설치하세요." 안내 후 종료

2. **로그인 상태 확인**:
```bash
$(yarn global bin)/railway whoami
```
- 실패 시: "Railway에 로그인되지 않았습니다. `railway login`을 실행하세요." 안내 후 종료

3. **프로젝트 연결 확인**:
```bash
$(yarn global bin)/railway status
```
- 연결된 프로젝트가 없으면: "Railway 프로젝트가 연결되지 않았습니다. `railway link`로 프로젝트를 연결하세요." 안내 후 종료

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

**시크릿 마스킹**: 출력에서 다음 변수는 값을 `***`로 마스킹하여 표시:
- `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`
- `_KEY`, `_SECRET`, `_TOKEN`, `_PASSWORD`가 포함된 변수명
- 사용자에게 보여줄 때 변수명만 표시하고 값은 마스킹

### run
```bash
$(yarn global bin)/railway run <사용자가 지정한 명령>
```

**안전 장치**: `railway run` 실행 전 반드시 사용자 확인 요청:
- 실행할 명령을 출력하고 "이 명령을 프로덕션 환경에서 실행합니다. 진행할까요?" 확인
- 특히 위험한 명령 (migrate, flush, shell, 데이터 삭제 관련) 시 추가 경고:
  "이 명령은 프로덕션 데이터에 영향을 줄 수 있습니다. 정말 실행할까요?"

### 배포 실패 시 대응

배포 실패가 확인되면 다음 순서로 대응:

1. **로그 확인**:
```bash
$(yarn global bin)/railway logs --tail 50
```

2. **일반적인 실패 원인 점검**:
   - 빌드 에러: 로그에서 `error`, `failed` 키워드 확인
   - 환경변수 누락: `railway variables`로 필수 변수 확인
   - 헬스체크 실패: `/health/` 엔드포인트 응답 확인

3. **롤백 안내**:
   - "Railway 대시보드에서 이전 배포로 롤백할 수 있습니다."
   - Railway 대시보드 URL: `https://railway.com/dashboard` → 프로젝트 → Deployments → 이전 배포 선택 → Rollback

## 주의사항
- `railway login`이 안 되어 있으면 먼저 로그인 안내
- `railway link`가 안 되어 있으면 프로젝트 연결 안내
- 환경변수 변경은 Railway 대시보드에서 직접 수행 (CLI로 하지 않음)
- 배포는 git push로 자동 트리거 (수동 배포: `railway up`)
- `railway run`은 프로덕션 환경에서 실행되므로 반드시 사용자 확인 후 실행
