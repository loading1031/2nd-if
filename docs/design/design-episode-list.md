# 에피소드 목록 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[story]] - 작품/에피소드 시스템 (에피소드 데이터 구조)
- [[branch]] - 분기 시스템 (분기 관계, BRANCHES_FROM)

## 패턴 라이브러리
- `/pattern-library/` → pages → episode_list

## 프로덕션 템플릿
- (추후 구현)

## 레이아웃

작품 상세 페이지의 "에피소드 목록" 탭에 표시되는 에피소드 리스트이다.
원작 경로(is_original=true인 NEXT 관계)를 기본 뼈대로 보여주고, 분기가 존재하는 화에 배지를 표시하여 아코디언으로 펼칠 수 있게 한다.

### 전체 구조

```
[원작 경로]
┌─────────────────────────────────────────────────┐
│ 1화  시작            👁 1,234  ★ 4.2            │
├─────────────────────────────────────────────────┤
│ 2화  전개            👁 1,100  ★ 4.5  [분기 2] ▼│
│  ├ "A 생존 루트" by 작가A — 3화                  │
│  └ "로맨스 엔딩" by 작가B — 2화                  │
├─────────────────────────────────────────────────┤
│ 3화  반전            👁 980   ★ 4.8             │
├─────────────────────────────────────────────────┤
│ 4화  결말            👁 870   ★ 4.1  [분기 1] ▼│
│  └ "빌런 시점" by 작가C — 1화                    │
├─────────────────────────────────────────────────┤
│ 5화  에필로그        👁 750   ★ 3.9             │
└─────────────────────────────────────────────────┘
```

### 에피소드 행 (episode_row)

각 원작 에피소드 행은 한 줄로 표시된다.

| 요소 | 위치 | 설명 |
|------|------|------|
| 화 번호 | 좌측 | `badge badge-primary badge-sm` — "N화" 형태 |
| 제목 | 화 번호 우측 | 에피소드 제목, 클릭 시 에피소드 리더로 이동 |
| 유료 배지 | 제목 우측 (선택) | `badge badge-warning badge-sm` — 유료 에피소드일 때만 표시 (가격) |
| 조회수 | 우측 영역 | 눈 아이콘 + 숫자 |
| 평균 별점 | 조회수 우측 | 별 아이콘 + 점수 (미등록 시 "-") |
| 분기 배지 | 최우측 | `badge badge-accent badge-sm` — "분기 N개" + 펼침 화살표, 분기 있을 때만 표시 |

모바일에서는 조회수/별점을 제목 아래 줄로 내린다.

### 분기 펼침 영역 (branch_list)

분기 배지 클릭 시 해당 행 아래에 들여쓰기된 분기 목록이 펼쳐진다.

| 요소 | 설명 |
|------|------|
| 분기 작품 제목 | 분기 작품명, 링크 |
| 작가명 | "by 작가명" |
| 에피소드 수 | 해당 분기의 총 에피소드 수 |
| 방향 설명 | 분기 작품의 description 첫 줄 (truncate, 선택) |

분기 목록은 engagement_score(= visit_count) 내림차순으로 정렬한다.

## DaisyUI 컴포넌트 매핑

### 에피소드 행
- 전체 리스트: `div` with `divide-y divide-base-200` (구분선)
- 각 행: 일반 `div` — `flex items-center gap-2 px-4 py-3 hover:bg-base-200 transition-colors cursor-pointer`
- 화 번호: `badge badge-primary badge-sm`
- 유료 배지: `badge badge-warning badge-sm`
- 분기 배지: `badge badge-accent badge-sm cursor-pointer` + 화살표 아이콘

### 분기 펼침
- DaisyUI `collapse` 또는 순수 HTML details/summary는 행 내 배치가 어려우므로, HTMX `hx-get`으로 분기 목록을 lazy-load하는 방식을 사용한다.
- 분기 배지 클릭 시 `hx-get`으로 해당 에피소드의 분기 목록 partial을 불러와 행 아래에 삽입한다.
- 펼침 영역: `bg-base-200 rounded-lg ml-8 my-1 p-3` — 들여쓰기 + 배경색으로 시각적 구분
- 각 분기 항목: `flex items-center gap-2 py-2` — 분기 아이콘(트리 라인) + 정보

### 빈 상태
- 에피소드가 없을 때: `text-center py-12 text-base-content/50` — "아직 에피소드가 없습니다."

## HTMX 동작

### 에피소드 목록 로드
- 작품 상세 페이지 진입 시 `hx-get`으로 에피소드 목록 partial 로드
- `hx-target="#episode-list"`, `hx-swap="innerHTML"`
- `hx-indicator` — 로딩 스피너

### 분기 목록 토글
- 분기 배지 클릭 시:
  - 닫힌 상태: `hx-get="/works/{work_id}/htmx/episodes/{episode_id}/branches/"` → 분기 목록 partial 삽입
  - 열린 상태: JavaScript로 분기 목록 영역 제거 (서버 요청 없음)
- `hx-target="#branches-{episode_id}"`, `hx-swap="innerHTML"`
- 화살표 아이콘 회전으로 열림/닫힘 상태 표시

## 반응형

### 데스크톱 (md 이상)
- 화 번호, 제목, 유료 배지, 조회수, 별점, 분기 배지가 한 줄에 표시
- 최대 너비 `max-w-4xl`

### 모바일 (md 미만)
- 첫 줄: 화 번호 + 제목 + 분기 배지
- 둘째 줄: 조회수 + 별점 + 유료 배지
- 분기 펼침 영역의 들여쓰기 축소 (`ml-4`)

## 사용 컴포넌트
- `components/episode_row.html` - 에피소드 행 (기존 work_detail에서도 사용)
- `components/branch_list_item.html` - 분기 항목 (신규)

## 개발
- (추후 추가)
