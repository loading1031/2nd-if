# 2nd-if 작업 지침

작업 전 공통 프로젝트 규칙인 [.claude/rules/CLAUDE.md](.claude/rules/CLAUDE.md)를 읽는다.
문서 작업은 [.claude/rules/docs.md](.claude/rules/docs.md), Git 작업은 [.claude/rules/workflow.md](.claude/rules/workflow.md)를 따른다.
이 세 파일이 Claude와 Codex의 공통 원본이다. 기술별 규칙은 공통 프로젝트 규칙의 표에 따라 필요한 것만 읽는다.

- 작업 상태·다음 행동·완료 기준은 GitHub 이슈에 기록한다. 추적 저장소는 `loading1031/2nd-if`다.
- 통합 브랜치는 `dev`, 릴리스 대상은 `main`이다. 새 Codex 브랜치는 `codex/<유형>/<이슈>-<주제>` 형식으로 만든다.
- 기존 미커밋 변경·stash·다른 작업 브랜치는 보존한다. 작업 범위 밖 파일을 커밋하지 않는다.
- `.agents/skills/source-command-*`는 `.claude/commands/`와 같은 절차의 Codex 진입점이다.
- Claude 도구 이름은 현재 환경에서 제공하는 도구로 해석한다. 사용할 수 없는 도구·서브에이전트를 실행했다고 표시하지 않는다.
- 별도 위임 요청이 없으면 메인 에이전트가 순차 수행한다. 병렬 실행은 필요한 파일 소유권과 실행 환경을 확인한 뒤에만 한다.
