# 2nd-if 공통 프로젝트 규칙

이 파일은 Claude·Codex가 함께 사용하는 프로젝트 지침이다.

## 작업과 문서

- 요청과 관련된 GitHub 이슈를 읽고 목표·완료 기준·다음 행동을 확인한다. 작업 추적 저장소는 `loading1031/2nd-if`다.
- 작업 상태는 이슈, 지속적인 요구사항·주요 결정은 `docs/specs/`의 주제별 마크다운에 둔다.
- 문서 운영: [docs.md](docs.md). 브랜치·커밋·PR: [workflow.md](workflow.md).
- 기존 코드 변경·stash·다른 작업의 파일은 보존한다. 작업과 무관한 수정이나 자동 stash를 하지 않는다.
- 기존 문서는 일괄 이동·삭제하지 않는다. 문서 상태보다 최신 커밋·구현과 실제 검증 결과를 우선한다.

## 기술별 규칙 — 관련 작업 전에 읽기

| 작업 | 규칙 |
|---|---|
| Python·Django·모델·뷰·테스트 | [django.md](django.md) |
| HTML·HTMX·부분 응답 | [htmx.md](htmx.md) |
| 에피소드 에디터·번들·HTML 저장 | [tiptap.md](tiptap.md) |
| HTML·CSS·테마 | [tailwind-css.md](tailwind-css.md), [daisyui.md](daisyui.md) |
| UI 컴포넌트·페이지 | [pattern-library.md](pattern-library.md) |
| 리더 시각·모션·화면 크기 | [리더 경험 기준](../../docs/design/reader-experience-principles.md), [스타일 가이드](../../docs/design/design-visual-style.md) |

기본 구성은 Django 서버·Django 템플릿·Tailwind CSS·DaisyUI다. 새 기능은 일반적인 Django 뷰·폼을 우선하고, 기존 async/HTMX 동작은 보존한다. 의존성 버전은 `pyproject.toml`과 `uv.lock`으로 확인한다. async를 사용하는 경우 ORM은 `aget`/`acreate`/`async for` 등을 쓰며 `alist()`는 사용하지 않는다. 그래프·유사도 구현은 PostgreSQL 통합 이후 코드를 확인하고 과거 Neo4j 설명을 그대로 구현하지 않는다.

## 구현과 검증

- UI 변경은 관련 사용자 흐름과 화면 상태를 먼저 확인하고 기존 컴포넌트를 재사용한다. 별도 디자인 문서 생성이나 커밋을 모든 작업에 강제하지 않는다.
- 기능·버그 수정은 정상·오류·권한 경로를 확인하고 변경 동작을 검증하는 테스트를 추가/갱신한다. 작은 문구·스타일 변경에 동작을 복제하는 테스트를 만들지 않는다.
- 패키지는 uv로 관리한다. Python 확인은 `uv run ruff check <변경 파일>` 및 `uv run ruff format --check <변경 파일>`을 사용한다.
- Unit: `uv run python -m pytest server/apps/`. E2E는 기존 `server/tests/e2e/`가 있는지 확인한 뒤 해당 경로를 실행한다. 문서에만 있고 없는 경로를 실행했다고 보고하지 않는다.
- 환경·DB가 없어서 수행하지 못한 검증은 명시한다. 과거 커밋의 테스트 개수를 현재 통과 수로 보고하지 않는다.
- 제품 UI에 내부 도구·구현 절차를 노출하지 않는다.

## 진입점

기존 `/doc`, `/feature`, `/scenario`, `/commit`, `/merge`, `/deploy`, `/monitoring`은 `.claude/commands/`의 프로젝트 절차를 따른다. Codex에서는 같은 이름의 `source-command-*` 스킬 또는 자연어 요청으로 실행한다.

[이력 색인](../../docs/history/2026-10-15-work-history.md) · [전환 추적 이슈](https://github.com/loading1031/2nd-if/issues/23)
