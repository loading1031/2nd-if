# 분기 생성 페이지 디자인 v2

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[branch]] - 분기 시스템 (분기 방향 + AI 유사도 검사 추가)
- [[story]] - 작품/에피소드 시스템
- [[license]] - 라이선스 표시

## 변경 이력
- v1 → v2: 분기 방향 입력 필드 및 AI 유사도 검사 결과 표시 영역 추가

## 패턴 라이브러리
- `/pattern-library/` → pages → branch_create

## 프로덕션 템플릿
- `apps/stories/templates/stories/pages/branch_create.html`

## 레이아웃

### 전체 구조 (위→아래)

1. **Breadcrumb**: 작품명 > 원점 에피소드 > 새 분기
2. **분기 원점 정보 카드**: 작품명, 화 번호, 작가, 라이선스 배지
3. **info alert**: "이 분기는 {작품명} {N}화에서 시작됩니다"
4. **카드 폼**:
   - 분기 방향 입력 (NEW)
   - AI 유사도 검사 결과 (NEW)
   - divider
   - 제목 입력
   - TipTap 본문 영역
   - 유료/무료 토글 → 가격 입력
5. **액션**: 취소 (ghost) / 분기 발행 (primary)

### 상세 레이아웃

```html
<!-- Breadcrumb -->
<div class="breadcrumbs text-sm">
    <ul>
        <li><a>{작품명}</a></li>
        <li><a>{N}화 - {에피소드 제목}</a></li>
        <li>새 분기</li>
    </ul>
</div>

<!-- 분기 원점 정보 카드 -->
<div class="card bg-base-100 shadow-sm">
    <div class="card-body">
        <div class="flex items-center justify-between">
            <div>
                <h2 class="card-title text-lg">{작품명}</h2>
                <p class="text-sm text-base-content/60">{N}화 · {작가명}</p>
            </div>
            <span class="badge badge-outline">{라이선스 타입}</span>
        </div>
    </div>
</div>

<!-- info alert -->
<div class="alert alert-info">
    <span>이 분기는 {작품명} {N}화에서 시작됩니다</span>
</div>

<!-- 카드 폼 -->
<div class="card bg-base-100 shadow-xl">
    <div class="card-body">
        <form>
            <!-- [NEW] 분기 방향 입력 -->
            <label class="form-control w-full">
                <div class="label">
                    <span class="label-text font-semibold">분기 방향 <span class="text-error">*</span></span>
                    <span class="label-text-alt">이 분기가 원작과 어떻게 달라지는지 한 줄로 설명하세요</span>
                </div>
                <input
                    type="text"
                    name="direction"
                    class="input input-bordered w-full"
                    placeholder="이 분기의 방향을 한 줄로 설명하세요"
                    required
                    maxlength="100"
                    hx-post="/stories/htmx/branch/check-similarity/"
                    hx-trigger="keyup changed delay:500ms"
                    hx-target="#similarity-result"
                    hx-indicator="#similarity-loading"
                    hx-include="[name='episode_id']" />
                <div class="label">
                    <span class="label-text-alt text-base-content/50">
                        예: "캐릭터 A가 살아남는 루트", "빌런 시점에서 다시 보는 이야기"
                    </span>
                </div>
            </label>

            <!-- [NEW] AI 유사도 검사 결과 -->
            <div id="similarity-result" class="mt-2">
                <!-- 상태별 콘텐츠가 HTMX로 교체됨 -->
            </div>

            <!-- 검사 중 로딩 -->
            <div id="similarity-loading" class="htmx-indicator mt-2">
                <div class="flex items-center gap-2 text-sm text-base-content/60">
                    <span class="loading loading-spinner loading-sm"></span>
                    <span>유사 분기 검사 중...</span>
                </div>
            </div>

            <div class="divider"></div>

            <!-- 제목 입력 -->
            <label class="form-control w-full">
                <div class="label">
                    <span class="label-text font-semibold">분기 제목 <span class="text-error">*</span></span>
                </div>
                <input
                    type="text"
                    name="title"
                    class="input input-bordered w-full"
                    placeholder="분기 에피소드 제목을 입력하세요"
                    required />
            </label>

            <!-- TipTap 본문 영역 -->
            <label class="form-control w-full mt-4">
                <div class="label">
                    <span class="label-text font-semibold">본문 <span class="text-error">*</span></span>
                </div>
                <div id="tiptap-editor" class="min-h-[400px] border border-base-300 rounded-lg p-4">
                    <!-- TipTap 에디터 마운트 영역 -->
                </div>
            </label>

            <!-- 유료/무료 토글 -->
            <div class="flex items-center gap-4 mt-6">
                <label class="label cursor-pointer gap-2">
                    <span class="label-text">유료 에피소드</span>
                    <input type="checkbox" name="is_paid" class="toggle toggle-primary" />
                </label>
                <!-- 유료 선택 시 표시 -->
                <label class="form-control w-32" id="price-field" style="display: none;">
                    <input
                        type="number"
                        name="price"
                        class="input input-bordered input-sm"
                        placeholder="가격"
                        min="100"
                        step="100" />
                </label>
            </div>

            <!-- 액션 버튼 -->
            <div class="card-actions justify-end mt-8">
                <button type="button" class="btn btn-ghost">취소</button>
                <button type="submit" class="btn btn-primary">분기 발행</button>
            </div>
        </form>
    </div>
</div>
```

## AI 유사도 검사 상태별 UI

방향 입력 후 500ms 디바운스로 HTMX 요청을 보내고, 서버 응답에 따라 `#similarity-result` 영역이 교체된다.

### 1. 검사 중 (htmx-indicator)

```html
<div class="flex items-center gap-2 text-sm text-base-content/60">
    <span class="loading loading-spinner loading-sm"></span>
    <span>유사 분기 검사 중...</span>
</div>
```

### 2. 통과 (유사 분기 없음)

```html
<!-- partials/similarity_pass.html -->
<div class="alert alert-success">
    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
    <span>새로운 방향입니다!</span>
</div>
```

### 3. 유사 분기 발견

```html
<!-- partials/similarity_warning.html -->
<div class="alert alert-warning">
    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
    <div class="flex flex-col">
        <span>비슷한 분기가 있습니다: <strong>{기존 분기 제목}</strong> by {작가명}</span>
        <a href="/stories/{work_id}/branches/{branch_id}/continue/"
           class="link link-primary text-sm mt-1">
            이어쓰기 →
        </a>
    </div>
</div>
```

### 4. 입력 너무 짧음 (서버 측 최소 길이 미달 시)

```html
<!-- partials/similarity_info.html -->
<div class="alert alert-info">
    <span>방향 설명을 좀 더 구체적으로 입력해주세요 (최소 5자)</span>
</div>
```

## HTMX 연동

| 요소 | 속성 | 값 |
|------|------|----|
| 방향 입력 | `hx-post` | `/stories/htmx/branch/check-similarity/` |
| | `hx-trigger` | `keyup changed delay:500ms` |
| | `hx-target` | `#similarity-result` |
| | `hx-indicator` | `#similarity-loading` |
| | `hx-include` | `[name='episode_id']` (원점 에피소드 ID) |

## 필드 정의

| 필드 | 타입 | 필수 | placeholder | 검증 |
|------|------|------|-------------|------|
| direction | text input | 필수 | "이 분기의 방향을 한 줄로 설명하세요" | maxlength=100, 최소 5자 |
| title | text input | 필수 | "분기 에피소드 제목을 입력하세요" | maxlength=200 |
| content | TipTap editor | 필수 | - | 빈 값 불가 |
| is_paid | toggle | 선택 | - | - |
| price | number input | is_paid=true일 때 필수 | "가격" | min=100, step=100 |

## 사용 컴포넌트
- DaisyUI: card, input, toggle, btn, breadcrumbs, badge, alert, divider, loading, link, form-control, label

## 개발
- (추후 추가)
