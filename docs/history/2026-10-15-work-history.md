# 기존 작업 이력 색인 및 전환 추적

정리일: 2026-10-15. 저장소: https://github.com/loading1031/2nd-if

## 정리 원칙

과거 Git 커밋과 기존 문서를 기능 단위로 연결했다. 구현 이력 10건은 닫힌 이슈, 진행/후속 후보 8건은 열린 이슈다. 현재 기능 테스트·배포를 다시 검증한 결과가 아니며, 미커밋·stash 작업은 완료로 분류하지 않았다. 이번 정리에서 기존 커밋을 다시 쓰거나 브랜치·stash를 삭제하지 않았다.

## 과거 구현 이력

| 이슈 | 범위 | 이관 상태 |
|---|---|---|
| [#5](https://github.com/loading1031/2nd-if/issues/5) | 계정 인증·소셜 로그인·비밀번호 재설정 | 닫힘 — 과거 구현 기록 |
| [#6](https://github.com/loading1031/2nd-if/issues/6) | 작품·에피소드·분기·별점·라이선스 | 닫힘 — 과거 구현 기록 |
| [#7](https://github.com/loading1031/2nd-if/issues/7) | TipTap 에디터·이미지 업로드·패턴 라이브러리 | 닫힘 — 과거 구현 기록 |
| [#8](https://github.com/loading1031/2nd-if/issues/8) | 복사 방지·워터마크·핑거프린트·폰트 | 닫힘 — 과거 구현 기록 |
| [#9](https://github.com/loading1031/2nd-if/issues/9) | Polygon 결제·MetaMask·지갑·유료 열람 | 닫힘 — 과거 구현 기록 |
| [#10](https://github.com/loading1031/2nd-if/issues/10) | CS 1:1 관리자 채팅·Django admin·FAQ | 닫힘 — 과거 구현 기록 |
| [#11](https://github.com/loading1031/2nd-if/issues/11) | AI BYOK 설정·키 암호화·SSE 생성 | 닫힘 — 과거 구현 기록 |
| [#12](https://github.com/loading1031/2nd-if/issues/12) | Neo4j·Ollama 의존 구조에서 PostgreSQL 통합 | 닫힘 — 과거 구현 기록 |
| [#13](https://github.com/loading1031/2nd-if/issues/13) | 배포·모니터링·CI 구성의 변천 | 닫힘 — 과거 구현 기록 |
| [#14](https://github.com/loading1031/2nd-if/issues/14) | Unit·E2E 보강 및 async 오류 수정 | 닫힘 — 과거 구현 기록 |

## 진행 중·후속 후보

| 이슈 | 범위 | 이관 상태 |
|---|---|---|
| [#15](https://github.com/loading1031/2nd-if/issues/15) | [진행] 동적 리더 — Pretext·시네마틱 PoC·Blender 장면 | 열림 |
| [#16](https://github.com/loading1031/2nd-if/issues/16) | [진행] OCI 인프라·Blue-Green 배포의 잔여 작업 확인 | 열림 |
| [#17](https://github.com/loading1031/2nd-if/issues/17) | [진행] 세계관 WorldBible·AI 초안 연결 — 로컬 WIP | 열림 |
| [#18](https://github.com/loading1031/2nd-if/issues/18) | [진행] 스프라이트 생성 파이프라인 — 로컬 stash 복구 | 열림 |
| [#19](https://github.com/loading1031/2nd-if/issues/19) | [기획 후보] 표절 검사·신고·모더레이션 | 열림 |
| [#20](https://github.com/loading1031/2nd-if/issues/20) | [기획 후보] 포인트 보상·광고·수익 모델 후속 | 열림 |
| [#21](https://github.com/loading1031/2nd-if/issues/21) | [기획 후보] 다국어 지원 일괄 적용 | 열림 |
| [#22](https://github.com/loading1031/2nd-if/issues/22) | [기획 후보] SNS AutoDM·공유 카드·플랫폼 후속 범위 | 열림 |

## 원격·로컬 브랜치 감사

| 브랜치 | 2026-10-15 확인 상태 | 연결 |
|---|---|---|
| dev | 원격 존재, GitHub 기본 브랜치, 6e998bd | [브랜치](https://github.com/loading1031/2nd-if/tree/dev) |
| main | 원격 존재, bd9915c. 로컬 main/origin/main은 오래됨 | [브랜치](https://github.com/loading1031/2nd-if/tree/main) |
| feat/oci-infra | 원격 존재, 77ad030. dev 미포함 커밋 및 내용상 중복 작업 혼재 | [브랜치](https://github.com/loading1031/2nd-if/tree/feat/oci-infra), #16 |
| feature/ai-worldbible-draft | 로컬에만 존재, b481027 기준 미커밋 변경 | #17 |
| feature/gen-sprite-pipeline | 로컬에만 존재, stash dd8c299 보관 | #18 |

원격 목록은 GitHub API로 확인했다. 로컬에만 남은 브랜치에는 GitHub tree 링크를 만들지 않았다. 미래에 원격 브랜치를 만들거나 삭제하면 이 표의 날짜 이후 상태는 달라질 수 있다.

## 주요 방향 변화

| 시기 | 확인된 변화 | 기록 |
|---|---|---|
| 2026-01 ~ 03 | Django 기반 초기 구성, 인증·작품·분기·보호·배포 구축 | #5 ~ #14의 커밋 근거 |
| 2026-03-26 ~ 27 | Editor.js → TipTap, 분기 유사도·Polygon 결제·E2E 보강 | #6, #7, #9, #14 |
| 2026-04-12 ~ 13 | Dify 상담 → 관리자 1:1, AI BYOK, 동적 리더 재기획, FAQ | #10, #11, #15 |
| 2026-04-18 | 시네마틱 리더 PoC 및 PostgreSQL 통합 | #12, #15 |
| 2026-10-14 | Blender 장면 파이프라인·GLB/three.js PoC와 장면 레이어 기획 | #15 |
| 2026-10-15 로컬 감사 | 세계관 WIP, 스프라이트 stash, Codex 이관 불일치 확인 | #17, #18, #23 |

## 기존 PR

- [#1 Release 260322](https://github.com/loading1031/2nd-if/pull/1)
- [#2 Release 260322](https://github.com/loading1031/2nd-if/pull/2)
- [#3 Release v0.3.0: CS 상담 채팅 + 소셜 로그인 수정](https://github.com/loading1031/2nd-if/pull/3)
- [#4 Release v0.3.1: CI/CD 파이프라인 개선](https://github.com/loading1031/2nd-if/pull/4)

모두 병합된 PR이며 이번 요청에서 새 PR을 만들지 않았다. 과거 PR의 존재만으로 이후 dev 변경 전체가 main에 배포됐다고 판단하지 않는다.

## 문서 정합성 주의

- CS 채팅/FAQ의 개발 문서 미구현 표시는 실제 구현 커밋과 불일치한다.
- Neo4j·Ollama 서버 의존 설명은 PostgreSQL 통합 이후 코드와 대조해야 한다.
- 초기 CSS 기반 동적 리더 메모는 이후 Pretext 및 장면 파이프라인 기획에 의해 변경됐다.
- 세계관의 구조화/분기별 override와 현재 로컬 자유 텍스트 WorldBible v1을 구분한다.
- 스프라이트 stash에는 배포/Terraform 작업도 섞여 있다.
- 문서 인덱스의 분기 합치기·대시보드는 연결 대상 문서가 없어 미정 후보로 기록했다.
- 로컬 관리자 계정 문서 내용, 환경변수, Terraform plan/state, 키·자격증명은 이관 본문에 복사하지 않았다.

## 전환 계획

[#23 GitHub 이슈 중심 planning·Git 규칙 전환](https://github.com/loading1031/2nd-if/issues/23)

기존 문서는 보존하고 GitHub 이슈를 작업 상태/작업지시서로 사용한다. 주제별 지속 스펙은 저장소 마크다운에 남기고, Obsidian의 세 계층·역링크 의무를 해제하는 계획이다. 실제 규칙 교체·WIP 통합·원격 게시·브랜치 정리는 아직 실행하지 않았다.

GitHub의 게시된 색인: https://github.com/loading1031/2nd-if/issues/24
