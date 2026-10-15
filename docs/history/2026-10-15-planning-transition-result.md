# planning 전환 초기 로컬 적용 기록

이 문서는 최초 로컬 적용 시점의 기록이다. 이후 게시·병합·CI 결과와 완료 상태는 연결된 전환 이슈에서 확인한다.

정리일: 2026-10-15. 추적: [전환 이슈 #23](https://github.com/loading1031/2nd-if/issues/23).

## 적용한 내용

- 루트 `AGENTS.md`, `CLAUDE.md`가 `.claude/rules/CLAUDE.md`, `docs.md`, `workflow.md`의 공통 규칙을 읽도록 연결했다.
- 작업 상태·재개 지시·완료 기준은 GitHub 이슈, 지속적인 요구사항·주요 결정은 주제별 스펙으로 분리했다.
- 삼중 문서·양방향 역링크·백로그/로그/작업지시서 중복 갱신 의무를 해제했다. 기존 문서는 보존한다.
- `/doc`, `/feature`, `/scenario`, `/commit`, `/merge`, `/deploy`, `/monitoring` 절차를 공통 규칙에 맞췄다. Codex의 7개 `source-command-*` 스킬은 명령 파일을 읽는 얇은 진입점으로 만들었다.
- 자동 amend 판단, 허위 작성자, 강제 워크트리/브랜치 정리, 존재하지 않는 `.Codex/rules` 경로를 제거했다.
- 리더 모션·품질·화면 타깃에 대한 기존 메모리를 `docs/design/reader-experience-principles.md`에 옮겨 두 리뷰어가 같은 문서를 읽게 했다.
- 스펙 색인의 링크와 상태 관리 위치를 정리하고, CS 채팅/FAQ의 과거 미구현 표시는 구현 이력 있음으로 정정했다. 현재 기능 재검증 완료로 표시하지 않았다.
- Git 공통 검사 스크립트·로컬 설치 스크립트·PR 검사 workflow를 추가했다. 이 checkout에 commit-msg를 설치했고 기존 Ruff pre-commit은 유지했다.

## 검증

- `python3 -m unittest discover -s scripts/tests -p 'test_git_policy.py'`: 11건 통과.
- 변경된 Python 도구 3개 Ruff lint·format 검사 통과, `git diff --check` 통과.
- 실제 설치된 commit-msg가 올바른 메시지를 허용하고 잘못된 메시지를 거부함을 커밋 생성 없이 확인했다.
- 테스트용 Git 저장소에서 커밋 거부/허용, 기존 pre-commit 보존, 알 수 없는 commit-msg 덮어쓰기 거부, 정책 없는 과거 checkout 허용을 확인했다.
- 실제 Git 이력으로 PR 범위·dev → main 릴리스, 잘못된 base, fork의 dev를 통한 릴리스 거부, 과거 이관 스냅샷 제외와 이후 잘못된 커밋 거부를 확인했다.
- Git editor 주석이 있는 정상 메시지, 마지막 Refs trailer, 이슈 종료 키워드 위치를 확인했다.
- YAML·Codex 에이전트 TOML 파싱, 공통 규칙 로컬 링크와 7개 스킬 진입점을 확인했다.
- `server/` 기존 변경 파일 및 새 migration/template의 SHA-256, HEAD, 모든 로컬 브랜치 포인터와 stash 목록을 작업 전 스냅샷과 대조해 동일함을 확인했다.
- 제품 기능을 변경하지 않아 Django 전체 테스트·운영 배포 검증은 실행하지 않았다.

## 검토 범위

도구 코드·테스트·workflow와 공통 규칙을 직접 대조해 검토했다. 검토 중 릴리스 커밋을 직접 dev 커밋으로 오인하는 문제, 과거 이력 소급 검사, Git editor 주석, 공유 훅이 과거 checkout을 막는 문제를 수정하고 재검증했다.

독립 리뷰어에 의한 별도 검토는 수행하지 않았다. 현재 호스트의 Task 매핑은 메인 스레드 순차 수행이므로 ce-code-review의 독립 리뷰·분리된 합성 절차를 완료한 것으로 표시하지 않는다. 전용 코드 리뷰 완료 영수증이나 원격 CI 통과를 주장하지 않는다.

## 보존·게시 상태와 남은 일

- 세계관 WIP #17, 스프라이트 stash #18, 원격 OCI 작업 #16은 적용·병합·삭제하지 않았다. 문서/도구 전환은 이 WIP와 독립적인 파일에서 수행했다.
- 변경 파일은 현재 로컬 작업 트리에 있으며 이 작업에서 commit·push·PR·릴리스를 만들지 않았다. 현재 작업 브랜치를 설정 전환 목적으로 바꾸지 않았다.
- Git policy CI 파일은 로컬에서 검증했으며 GitHub에서 아직 실행되지 않았다. 원격 적용은 전환 파일만 별도 브랜치/커밋으로 분리해 dev 대상 PR로 게시하는 후속 단계다.
- GitHub required check 설정은 변경하지 않았다. 실제 CI 실행을 확인한 후 필요한 저장소 설정을 별도로 적용할 수 있다.
- #23은 원격 게시·통합 전까지 열린 상태로 유지한다. 기존 계획 문서는 변경하지 않고 실행 결과는 이 기록과 이슈 댓글에 둔다.
