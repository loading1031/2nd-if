# 2nd-if 작업 지침

작업 전 [.claude/rules/CLAUDE.md](.claude/rules/CLAUDE.md)를 읽는다.
문서·Git 절차는 공통 원본인 [.claude/rules/docs.md](.claude/rules/docs.md)와 [.claude/rules/workflow.md](.claude/rules/workflow.md)를 따른다.

## 기획 설정

- 기획 폴더: docs/specs
- 기준 문서: index.md
- 기본 브랜치: dev
- 개발 브랜치: 없음
- 릴리스 브랜치: main
- 작업지시서: issue
- 작업 추적: loading1031/2nd-if
- 합치기 방식: PR
- 금지어: 없음

이 저장소는 `planning` 원본의 명시적 프로젝트 예외를 사용한다. `backlog.md`/`work-orders.md`/결정 로그를 중복 생성하지 않고 GitHub 이슈에서 작업을 관리한다. 명령 실행 전 공통 문서·워크플로우 규칙을 읽고, 원본 절차의 백로그 ID는 이슈 번호로 대체한다. `개발 브랜치: 없음`은 별도의 통합 브랜치가 없다는 뜻이며 코드 작업을 dev에 직접 커밋해도 된다는 뜻이 아니다. 모든 작업 PR은 dev로 보내며 릴리스만 dev → main으로 보낸다.

Claude 전용 planning 훅과 Codex의 실행 지원은 동일하지 않다. 공통 Git 검사는 `scripts/check_git_policy.py`와 `.github/workflows/git-policy.yml`을 기준으로 한다.

## 디자인

- 문서: `design/index.html` (IA·화면 설명·SVG), 원본 `design/pages.json`·`design/wireframes/`
- 화면 구조 승인 기준: PR #34, `c74c536768fd37fb2bc0836c13048492e57cdf29` (dev 병합 `7c1bc0d153d145c26280baf9474f4d9912b92b37`)
- 토큰 원본: `server/static/css/input.css`에서 불러오는 Tailwind CSS·daisyUI light 테마. 값 복사나 별도 테마는 만들지 않는다.
- 컴포넌트 원본: `server/templates/components/`; 옵션·사용법은 각 원본의 헤더 주석
- 전시: Django 개발 서버의 `/pattern-library/` → tokens / components. `server/templates/patterns/`에서 실제 원본을 include한다.
- 실행: `uv run python server/manage.py tailwind build` 후 `uv run python server/manage.py runserver`. 전시 스크립트는 `npm run build:catalog`로 생성한다.
- `design/prototype.html`은 공유 원본으로 생성하는 기존 화면 조합 예시다. 컴포넌트 전시는 패턴 라이브러리에 유지하고 예시 데이터·모의 저장을 실제 서버 동작과 구분한다.
