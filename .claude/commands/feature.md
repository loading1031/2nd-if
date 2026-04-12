# /feature — 기획→디자인→테스트→개발 파이프라인

Feature 단위로 기획 문서 → UI 디자인 → 테스트 코드 → 서버 로직을 **병렬 에이전트**로 자동 실행한다.
메인 에이전트는 조율만 하고, 각 Step의 실제 작업은 worktree 에이전트가 수행한다.

## 사용법

```
/feature {이름}                — 전체 파이프라인 (docs→design→test→feat)
/feature {이름} docs           — 기획 문서만
/feature {이름} design         — 디자인만
/feature {이름} test           — 테스트 코드만
/feature {이름} feat           — 개발만
/feature {이름} status         — 현재 진행 상태 확인
```

## 실행 절차

### 0. 사전 준비
1. 사용자에게 Feature 개요를 확인 (어떤 기능인지, 어떤 앱에 속하는지)
2. `docs/specs/`에서 관련 기획 문서 존재 여부 확인
3. `feat/{이름}` 브랜치 생성 (dev에서 분기)

### 1. docs — 기획 문서 (병렬 에이전트)
**목표**: specs, design, dev 문서를 생성/업데이트

에이전트 분배:
- **Agent A**: `docs/specs/{이름}.md` 생성/업데이트 (사용자 플로우 포함: 정상/에러/엣지)
- **Agent B**: `docs/design/`, `docs/dev/` 문서 생성/업데이트 + 역링크

각 에이전트에게 전달할 정보:
- Feature 개요 (사용자 요청에서 추출)
- 기존 문서 내용 (있는 경우)
- 문서 템플릿 (docs.md 컨벤션 참조)
- **수정 허용 파일 목록 명시** (충돌 방지)

→ merge 후 커밋: `docs: {이름} 기획 작성`

### 2. design — UI 디자인 (병렬 에이전트)
**목표**: 템플릿 파일 생성 (DaisyUI + HTMX)

에이전트 분배: 페이지/컴포넌트 단위로 분리
- 각 에이전트는 자기가 담당하는 **템플릿 파일만** 생성/수정
- 공용 partial은 한 에이전트만 담당

각 에이전트에게 전달할 정보:
- 디자인 문서 (`docs/design/design-{이름}.md`)의 레이아웃/컴포넌트 섹션
- 기존 템플릿 패턴 (base.html extends, components include)
- DaisyUI 컨벤션 (daisyui.md)
- **수정 허용 파일 목록 명시**

→ merge 후 커밋: `design: {이름} UI 디자인`

### 3. test — 테스트 코드 (병렬 에이전트)
**목표**: TDD — 실패하는 테스트 먼저 작성

에이전트 분배:
- **Agent A**: Unit 테스트 (`apps/{앱}/tests.py`)
- **Agent B**: E2E 테스트 (`server/tests/e2e/test_{이름}.py`)

각 에이전트에게 전달할 정보:
- 기획 문서의 **사용자 플로우** (테스트 케이스 소스)
- 모델 스펙 (데이터 모델 섹션)
- URL 구조 (dev 문서)
- 기존 테스트 패턴 (conftest.py, fixture)
- **수정 허용 파일 목록 명시**

→ merge 후 커밋: `test: {이름} 테스트 케이스 작성`

### 4. feat — 개발 (병렬 에이전트)
**목표**: 테스트 통과할 때까지 구현

에이전트 분배: 레이어별로 분리
- **Agent A**: 모델 + 핵심 뷰 (models.py, 주요 views)
- **Agent B**: 보조 뷰 + URL (추가 views, urls.py)
- **Agent C** (선택): 프론트엔드 (JS, 외부 패키지)

각 에이전트에게 전달할 정보:
- dev 문서의 **구현 내용** 섹션
- 모델 스펙 + URL 구조
- Django 컨벤션 (django.md) — async ORM, request.user 패턴
- **수정 허용 파일 목록 명시**

→ merge 후:
  1. `makemigrations` + `migrate`
  2. `ruff check --fix` + `ruff format`
  3. 테스트 실행 (`pytest`)
  4. 실패 시 수정 → 재실행
  5. 커밋: `feat: {이름} 구현`

## 에이전트 프롬프트 규칙

모든 worktree 에이전트 프롬프트에 반드시 포함:
1. **프로젝트 기술 스택**: Django 6.0+ async, HTMX, DaisyUI
2. **해당 Step의 구체적 산출물** (파일 경로, 내용 스펙)
3. **수정 허용 파일 목록**: "X, Y 파일만 수정/생성. 다른 파일 수정 금지"
4. **관련 컨벤션 요약**: 해당 작업에 필요한 규칙만 발췌 전달
5. **기존 파일 내용**: 수정할 파일이 있으면 현재 내용을 프롬프트에 포함

## merge + 후처리 절차

각 Step 완료 후:
1. 워크트리에서 변경 파일을 메인 repo로 복사 (`cp`)
2. `ruff check --fix` + `ruff format` (Python 파일)
3. `git add` + `git commit` (커밋 접두어: docs/design/test/feat)
4. 워크트리 정리: `git worktree remove --force` + `git branch -D`

## 브랜치 전략

```
dev
└── feat/{이름}    ← /feature가 생성하는 브랜치
    각 Step의 worktree agent는 임시 브랜치 → feat/{이름}으로 merge
```

## 에러 시 중단 규칙

- 이전 Step 실패 시 **다음 Step 진행 금지**. 사용자에게 실패 내용 보고 후 대기
- 에이전트 실패 (빈 결과, 잘못된 파일 수정) 시: 해당 에이전트 결과 폐기, 메인이 직접 수행 또는 사용자에게 보고
- merge 충돌 시: `/merge` 스킬의 충돌 해결 전략 적용. 자동 해결 불가 시 사용자에게 보고 후 대기
- ruff/테스트 실패 시: 메인 에이전트가 직접 수정 (3회 시도 후에도 실패 시 사용자에게 보고)

## 주의사항
- 각 Step은 **이전 Step이 완료된 후** 순차 실행 (docs→design→test→feat)
- Step 내부의 에이전트들은 **병렬** 실행
- 공통 파일(urls.py, base.html 등)은 **한 에이전트만** 수정
- 에이전트 수는 **최소한**으로 (보통 2개, 복잡하면 3개)
- 테스트 실패 시 메인 에이전트가 직접 수정 (에이전트 재실행 아님)
