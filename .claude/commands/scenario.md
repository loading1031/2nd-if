# /scenario — UX 시나리오 확장 + 테스트 생성

기획 문서의 사용자 플로우를 확장하고, 그에 맞는 테스트 코드를 생성한다.

## 사용법

```
/scenario auth           — 인증 시나리오 확장 + 테스트 생성
/scenario stories        — 작품/에피소드 시나리오 확장 + 테스트 생성
/scenario branch         — 분기 시나리오 확장 + 테스트 생성
/scenario {spec_name}    — 해당 기획의 시나리오 확장 + 테스트 생성
```

## 실행 절차

### 1. 기획 문서 읽기
- `docs/specs/{spec_name}.md`의 `## 사용자 플로우` 섹션 확인
- **문서가 없는 경우**: 사용자에게 알리고 `/doc spec {spec_name}`으로 먼저 생성할지 확인. 사용자가 거부하면 중단
- **`## 사용자 플로우` 섹션이 없는 경우**: 빈 섹션을 생성하고 2단계로 진행

### 2. 플로우 확장 (메인 에이전트)
기존 플로우에 누락된 케이스를 추가:
- **정상 플로우**: 기본 성공 경로
- **에러 플로우**: 검증 실패, 권한 없음, 404 등
- **엣지 케이스**: 경계값, 중복 요청, 빈 입력 등

확장 후 기획 문서를 업데이트하고, 다음 단계에서 에이전트에 전달할 정보를 정리:
- 확장된 사용자 플로우 전문
- 관련 모델 스펙 (`apps/{app}/models.py` 내용)
- URL 패턴 (`apps/{app}/urls.py` 내용)

### 3. 테스트 도출 및 병렬 에이전트 분배

각 플로우 항목을 테스트 유형별로 분류한 뒤, **두 에이전트를 병렬로 실행**한다.

#### Unit 테스트 에이전트 (worktree)
**전달할 정보:**
- 확장된 사용자 플로우 (정상/에러/엣지)
- 모델 스펙: `server/apps/{app}/models.py`
- 뷰 스펙: `server/apps/{app}/views/async_views.py`
- 기존 테스트 파일: `server/apps/{app}/tests.py` (중복 방지)
- 컨벤션: `.claude/rules/django.md`의 테스트 섹션

**수정 허용 파일:**
- `server/apps/{app}/tests.py` — 기존 테스트 뒤에 추가만

**작성 규칙:**
- `@pytest.mark.django_db(transaction=True)` + `async def`
- 기존 fixture가 있으면 재사용, 없으면 `conftest.py`에 추가
- 테스트 함수명: `test_{플로우설명}` (snake_case)

#### E2E 테스트 에이전트 (worktree)
**전달할 정보:**
- UI 인터랙션이 필요한 플로우 목록
- URL 패턴: `server/apps/{app}/urls.py`
- 기존 E2E 테스트: `server/tests/e2e/` (패턴 참고 + 중복 방지)
- 기존 conftest: `server/tests/e2e/conftest.py` (fixture 재사용)

**수정 허용 파일:**
- `server/tests/e2e/test_{app}_flow.py` — 기존 테스트 뒤에 추가만
- `server/tests/e2e/conftest.py` — 새 fixture 필요 시 추가만

**작성 규칙:**
- `@pytest.mark.django_db(transaction=True)` + Playwright `page`
- `asyncio_mode=strict`
- 기존 E2E 테스트 패턴(페이지 이동, 폼 제출, 검증 순서)을 따름

### 4. 에이전트 결과 수집 및 병합
메인 에이전트가 두 워크트리의 결과를 수집:
1. 각 에이전트의 테스트 파일 변경 확인
2. 워크트리를 순차적으로 dev에 병합
3. 충돌 발생 시 사용자에게 보고

### 5. 테스트 실행
병합 후 전체 테스트 실행:
```bash
# Unit 테스트
python -m pytest server/apps/{app}/tests.py -v

# E2E 테스트
python -m pytest server/tests/e2e/test_{app}_flow.py -v -o "asyncio_mode=strict"
```

**실행 실패 시 대응:**
- **ImportError / ModuleNotFoundError**: 누락된 모듈 확인 후 사용자에게 보고. 구현 전이라면 정상
- **fixture 미발견**: conftest.py에 필요한 fixture 추가
- **DB 관련 에러**: `transaction=True` 누락 여부 확인
- **테스트 실패 (AssertionError)**: TDD이므로 실패는 정상. 에러(크래시)만 수정

### 6. 결과 보고
- 새로 추가된 플로우 항목 목록
- 새로 추가된 테스트 목록 (Unit / E2E 분리)
- 테스트 실행 결과:
  - 통과: N건
  - 실패 (TDD 의도된 실패): N건
  - 에러 (수정 필요): N건
- 워크트리 정리 완료 여부

## 규칙
- 기획 문서를 먼저 업데이트, 그 다음 테스트 코드 생성
- 테스트는 구현 없이도 실행 가능해야 함 (실패 OK, 에러 NO)
- 기존 테스트를 수정하지 않고 추가만
- 메인 에이전트는 플로우 확장 + 조율만 수행, 테스트 작성은 워크트리 에이전트가 담당
- 워크트리 에이전트는 수정 허용 파일만 변경 (다른 파일 수정 금지)
- 병렬 실행이 불필요한 소규모 작업(테스트 3건 이하)은 메인 에이전트가 직접 수행
- 커밋: `test: {기능명} 시나리오 테스트 추가`
- 워크트리 병합 후 즉시 정리 (`git worktree remove`)
