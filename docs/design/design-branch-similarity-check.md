# 유사 분기 안내 컴포넌트 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[branch]] - 분기 시스템 (유사도 검사는 [[plagiarism]]과 연계, MVP 이후)

## 패턴 라이브러리
- `/pattern-library/` → components → branch_similarity_result

## 프로덕션 템플릿
- (추후 구현)

## 개요

분기 생성 페이지([[design-branch-create]])에서 사용자가 "방향(direction)" 텍스트를 입력하면, HTMX 디바운스로 서버에 유사도 검사를 요청하고 결과를 실시간으로 표시하는 컴포넌트.

같은 에피소드에서 이미 분기된 기존 분기들의 방향과 비교하여, 중복 분기 생성을 사전에 안내한다.

## 컴포넌트

### 이름
`branch_similarity_result`

### 위치
`templates/components/branch_similarity_result.html`

### 파라미터

| 파라미터 | 필수 | 타입 | 설명 |
|---------|------|------|------|
| `status` | Y | string | `loading`, `pass`, `similar`, `empty` |
| `similar_branches` | N | list | 유사 분기 목록 (status=similar일 때) |
| `episode_id` | N | int | 현재 분기 원점 에피소드 ID |

### similar_branches 항목 구조

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | int | 분기 ID |
| `direction` | string | 분기 방향 설명 텍스트 |
| `author_nickname` | string | 작가 닉네임 |
| `episode_count` | int | 해당 분기의 에피소드 수 |
| `similarity_score` | float | 유사도 점수 (0.0~1.0) |
| `url` | string | 해당 분기로 이동하는 URL |

## HTMX 통합

### 트리거 (분기 생성 페이지 내 direction 입력 필드)

```html
<label class="form-control w-full">
    <div class="label">
        <span class="label-text">분기 방향</span>
        <span class="label-text-alt text-base-content/50">이 분기의 스토리 방향을 한 줄로 설명해주세요</span>
    </div>
    <input
        type="text"
        name="direction"
        placeholder="예: 주인공이 마왕과 화해하는 루트"
        class="input input-bordered w-full"
        hx-get="/htmx/branches/similarity-check/"
        hx-trigger="keyup changed delay:500ms"
        hx-target="#similarity-result"
        hx-indicator="#similarity-loading"
        hx-include="[name='episode_id']"
        required />
</label>

<div id="similarity-result">
    <!-- HTMX 응답이 여기에 swap됨 -->
</div>
```

### HTMX 속성 요약

| 속성 | 값 | 설명 |
|------|---|------|
| `hx-get` | `/htmx/branches/similarity-check/` | 유사도 검사 엔드포인트 |
| `hx-trigger` | `keyup changed delay:500ms` | 500ms 디바운스 |
| `hx-target` | `#similarity-result` | 결과 표시 영역 |
| `hx-indicator` | `#similarity-loading` | 로딩 인디케이터 |
| `hx-include` | `[name='episode_id']` | 분기 원점 에피소드 ID 함께 전송 |

### 엔드포인트

- **URL**: `GET /htmx/branches/similarity-check/?direction={text}&episode_id={id}`
- **응답**: `branch_similarity_result` 컴포넌트의 partial HTML

## 상태별 UI 상세

### 1. 검사 중 (status=loading)

로딩 인디케이터가 표시된다. `htmx-indicator` 클래스를 활용한다.

```html
<div id="similarity-loading" class="htmx-indicator mt-3">
    <div class="flex items-center gap-2 text-base-content/60 text-sm">
        <span class="loading loading-spinner loading-sm"></span>
        <span>분기 방향을 확인하고 있습니다...</span>
    </div>
</div>
```

- DaisyUI `loading loading-spinner loading-sm` 사용
- 텍스트: "분기 방향을 확인하고 있습니다..."
- 색상: `text-base-content/60` (반투명 텍스트)

### 2. 통과 (status=pass)

유사한 분기가 없을 때 표시된다.

```html
<div class="alert alert-success mt-3">
    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-5 w-5" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
    <span>새로운 방향입니다! 분기를 생성할 수 있습니다.</span>
</div>
```

- DaisyUI `alert alert-success` 사용
- 체크 아이콘 + 메시지 텍스트
- 분기 발행 버튼은 활성 상태 유지

### 3. 유사 분기 발견 (status=similar)

비슷한 방향의 기존 분기가 있을 때 표시된다.

```html
<div class="mt-3 space-y-3">
    <!-- 경고 알림 -->
    <div class="alert alert-warning">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-5 w-5" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span>비슷한 방향의 분기가 이미 있습니다</span>
    </div>

    <!-- 유사 분기 카드 목록 -->
    <div class="space-y-2">
        <!-- 각 유사 분기 카드 (반복) -->
        <div class="card card-compact bg-base-200">
            <div class="card-body">
                <div class="flex items-start justify-between gap-4">
                    <div class="flex-1 min-w-0">
                        <p class="font-medium text-base-content truncate">
                            주인공이 마왕과 협상하는 루트
                        </p>
                        <div class="flex items-center gap-2 mt-1 text-sm text-base-content/60">
                            <span>작가닉네임</span>
                            <span class="badge badge-sm badge-ghost">3화</span>
                            <span class="badge badge-sm badge-warning">유사도 85%</span>
                        </div>
                    </div>
                    <a href="#" class="btn btn-sm btn-outline btn-primary shrink-0">
                        이어쓰기
                    </a>
                </div>
            </div>
        </div>
        <!-- /각 유사 분기 카드 -->
    </div>

    <!-- 그래도 새 분기 만들기 -->
    <div class="text-center">
        <button type="button" class="btn btn-ghost btn-sm text-base-content/50" onclick="this.closest('form').querySelector('[type=submit]').disabled = false; this.closest('#similarity-result').innerHTML = '';">
            그래도 새 분기 만들기
        </button>
    </div>
</div>
```

#### 유사 분기 카드 구성

| 요소 | DaisyUI 클래스 | 설명 |
|------|---------------|------|
| 카드 컨테이너 | `card card-compact bg-base-200` | 배경색으로 구분 |
| 분기 방향 텍스트 | `font-medium text-base-content truncate` | 한 줄 말줄임 |
| 작가 닉네임 | `text-sm text-base-content/60` | 보조 텍스트 |
| 에피소드 수 배지 | `badge badge-sm badge-ghost` | "3화" 형태 |
| 유사도 배지 | `badge badge-sm badge-warning` | "유사도 85%" 형태 |
| 이어쓰기 버튼 | `btn btn-sm btn-outline btn-primary` | 해당 분기로 이동 |

#### "그래도 새 분기 만들기" 동작

- `btn btn-ghost btn-sm text-base-content/50` 스타일 (의도적으로 눈에 덜 띄게)
- 클릭 시: 유사도 결과 영역 초기화, 분기 발행 버튼 활성화
- 분기 발행 버튼을 비활성화하지는 않음 (경고만 제공, 차단하지 않음)

### 4. 입력 없음 (status=empty)

direction 필드가 비어있거나 너무 짧을 때 (3자 미만).

- 아무것도 표시하지 않음 (빈 응답)
- 서버에서 빈 HTML 반환

## 분기 생성 페이지 내 배치

[[design-branch-create]]의 레이아웃에서 direction 입력 필드 바로 아래에 배치:

```
┌─────────────────────────────────────┐
│ Breadcrumb: 작품명 > N화 > 새 분기    │
├─────────────────────────────────────┤
│ [분기 원점 정보 카드]                  │
│ info alert: "이 분기는 ... 시작됩니다"  │
├─────────────────────────────────────┤
│ 카드 폼                              │
│ ┌─────────────────────────────────┐ │
│ │ 분기 방향: [__________________ ] │ │
│ │                                 │ │
│ │ ┌── #similarity-result ──────┐  │ │
│ │ │ (유사도 검사 결과 영역)       │  │ │
│ │ └────────────────────────────┘  │ │
│ │                                 │ │
│ │ 제목: [______________________ ] │ │
│ │ EditorJS 본문 영역               │ │
│ │ 유료/무료 토글                    │ │
│ │ 가격 입력                        │ │
│ │                                 │ │
│ │ [취소]            [분기 발행]     │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## 사용 컴포넌트

- DaisyUI: `alert`, `card`, `badge`, `btn`, `loading`, `form-control`, `input`
- HTMX: `hx-get`, `hx-trigger`, `hx-target`, `hx-indicator`, `hx-include`

## UX 고려사항

1. **비차단 경고**: 유사 분기가 발견되어도 분기 생성을 차단하지 않음. 안내만 제공.
2. **이어쓰기 유도**: 유사 분기 카드에 "이어쓰기" 버튼을 제공하여, 기존 분기에 기여하도록 유도.
3. **디바운스 500ms**: 타이핑 중 과도한 서버 요청 방지.
4. **최소 입력 길이**: 3자 미만이면 검사하지 않음 (서버 부하 방지).
5. **유사도 임계값**: 서버에서 결정 (디자인에서는 결과만 표시). 예상 임계값: 0.7 이상.

## 개발
- (추후 추가)
