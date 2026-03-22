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
- 없으면 생성

### 2. 플로우 확장
기존 플로우에 누락된 케이스를 추가:
- **정상 플로우**: 기본 성공 경로
- **에러 플로우**: 검증 실패, 권한 없음, 404 등
- **엣지 케이스**: 경계값, 중복 요청, 빈 입력 등

### 3. 테스트 도출
각 플로우 항목을 테스트 케이스로 변환:
- 정상/에러 → Unit 테스트 (`apps/{app}/tests.py`)
- UI 인터랙션이 필요한 플로우 → E2E 테스트 (`server/tests/e2e/`)

### 4. 테스트 작성
- Unit: `@pytest.mark.django_db(transaction=True)` + `async def`
- E2E: `@pytest.mark.django_db(transaction=True)` + Playwright `page`
- 기존 테스트와 중복되지 않도록 확인

### 5. 테스트 실행
```bash
python -m pytest server/apps/{app}/tests.py -v
python -m pytest server/tests/e2e/ -v -o "asyncio_mode=strict"
```

### 6. 결과 보고
- 새로 추가된 플로우 항목 목록
- 새로 추가된 테스트 목록
- 실패하는 테스트 목록 (TDD: 구현 전이므로 실패가 정상)

## 규칙
- 기획 문서를 먼저 업데이트, 그 다음 테스트 코드 생성
- 테스트는 구현 없이도 실행 가능해야 함 (실패 OK, 에러 NO)
- 기존 테스트를 수정하지 않고 추가만
- 커밋: `test: {기능명} 시나리오 테스트 추가`
