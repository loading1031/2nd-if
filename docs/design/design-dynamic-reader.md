# 동적 텍스트 리더 디자인

> 2026-10-17 변경: Blender 기반 장면·화면 반응 계획은 폐기했다. 시각 에셋 방향은 [작품별 수집 도감](../specs/collection-encyclopedia.md)과 이슈 #15/#33으로 대체한다. 아래 Blender 관련 내용은 과거 기획 이력이며 현재 구현 요구사항이 아니다. 설정집 권한·버전 및 텍스트 독서 요구사항은 별도 유지한다.

> 디자인 문서

## 상태: 이전 제안 (최신 독서 방향에 맞춘 재설계 필요)

> #26의 현재 방향은 페이지 단위 독서, 설정집 항목을 작품별로 채택·매핑하는 편집기 우측 패널, 표현을 눌렀을 때 열리는 선택형 시각 에셋이다. 독자는 시각 요소 표시를 끌 수 있다. 아래 Pretext 리플로우, 작품별 업로드, 장르 기본 팩은 이전 시안이며 최신 요구사항으로 확정된 디자인이 아니다. 현재 기준은 [페이지 리더](../specs/dynamic-reader.md), [설정집과 시각 에셋](../specs/setting-book.md)이다.

## 기획
- [페이지 리더](../specs/dynamic-reader.md) — 동적 텍스트 리더 기획

## 프로덕션 템플릿
- `apps/stories/templates/stories/pages/episode_read.html` — 리더 페이지
- `apps/stories/templates/stories/partials/episode_content.html` — 본문 partial (HTMX로 로드)
- `apps/stories/templates/stories/pages/episode_write.html` — 에디터 페이지

## 핵심 개념

본문 HTML 안에 **오브젝트 노드**(`<div data-character="..." data-position="left">`)가 삽입되면, 클라이언트에서 Pretext가 오브젝트 박스를 고려하여 주변 텍스트를 리플로우한다.

```
일반 DOM:
  [p]—기사가 동굴 앞에 섰다.—[p]
  [div.character knight @left]
  [p]—검을 들어올리자...—[p]

Pretext 적용 후 (리플로우 시뮬레이션):
  ┌─────────────┐
  │  🗡️ knight  │  기사가 동굴 앞에 섰다.
  │   sprite    │  검을 들어올리자 온 세계가
  │             │  그의 것이었다. 그는 두려움
  └─────────────┘  없이 발을 내디뎠다.
```

## 오브젝트 노드 마크업

```html
<div class="fx-object"
     data-character="{sprite_id}"     {# 또는 data-object="{asset_id}" #}
     data-position="left"             {# left / right / center #}
     data-motion="slide-in">          {# slide-in / fade #}
    <img src="/media/sprites/knight.webp" alt="기사">
</div>
```

- `fx-object` 클래스는 리더 JS가 잡아서 Pretext 레이아웃 대상에 등록
- 서버는 `<img>`만 렌더 (이미지 URL은 `CharacterSprite.image` 또는 `SkinAsset.image`)
- `data-character`/`data-object`는 참조용 메타데이터 (ID)

## 장르별 기본 팩 매트릭스 (Phase 1)

| 장르 | 기본 무료 팩 이름 | 포함 오브젝트 |
|------|-----------------|-------------|
| fantasy | 판타지 베이직 팩 | 검, 방패, 마법진, 두루마리 |
| romance | 로맨스 베이직 팩 | 꽃잎, 하트, 반지 |
| horror | 공포 베이직 팩 | 그림자, 눈동자, 촛불 |
| daily | 일상 베이직 팩 | 커피잔, 고양이, 우산 |
| sf | SF 베이직 팩 | 회로, 홀로그램, 우주선 |
| mystery | 미스터리 베이직 팩 | 돋보기, 발자국, 열쇠 |
| history | 역사 베이직 팩 | 두루마리, 붓, 촛대 |

각 오브젝트는 정적 PNG/WebP (투명 배경). 프리미엄 애니메이션은 Phase 2.

## TipTap `/character` 슬래시 메뉴

```
┌────────────────────────────────────┐
│ 캐릭터 / 오브젝트 삽입              │
│                                    │
│ [내 캐릭터]                         │
│   🛡️ 기사        (업로드한 스프라이트) │
│   🐉 드래곤                         │
│                                    │
│ [장르 팩 — 판타지 베이직]            │
│   ⚔️ 검                             │
│   🛡️ 방패                           │
│   ✨ 마법진                          │
│   📜 두루마리                        │
│                                    │
│ [+ 캐릭터 업로드]                   │
└────────────────────────────────────┘
```

선택 시 하단에 **위치/모션 선택** 모달:

```
┌────────────────────────────────┐
│ 📍 위치: [왼쪽] 오른쪽 중앙     │
│ 🎬 모션: [슬라이드인] 페이드    │
│                                │
│         [취소]  [삽입]          │
└────────────────────────────────┘
```

- 기본값: 스프라이트의 `default_position`, `default_motion`
- "삽입" → 에디터에 `CharacterNode` atom block 삽입 (썸네일 + 삭제 버튼)

## 에디터 내 오브젝트 표시

에디터에서는 실제 리플로우를 하지 않고 **썸네일 카드**로 표시:

```
…기사가 동굴 앞에 섰다.

┌──────────────────────┐
│ 🗡️ knight           │
│ left / slide-in      │
│                  [×] │
└──────────────────────┘

검을 들어올리자…
```

- 삭제 버튼으로 오브젝트 노드 제거
- 클릭 시 위치/모션 편집 모달 재오픈

## 리더 페이지 렌더링 흐름

```
1. 서버: 에피소드 HTML + Pretext 번들 script 태그 전송
2. 클라이언트: DOMContentLoaded
   └── reader-pretext.js 초기화
3. [data-character], [data-object] 노드 수집
4. 각 오브젝트 이미지 preload 완료 대기
5. Pretext.layout() 호출 → 오브젝트 박스 기준 텍스트 리플로우 계산
6. IntersectionObserver로 오브젝트 뷰포트 진입 감지
7. 진입 시 data-motion 대로 fx-enter 클래스 추가 (CSS 트랜지션)
8. 스크롤/리사이즈 시 디바운스된 재레이아웃
```

## 진입 모션 CSS (최소 세트)

```
.fx-object                 { opacity: 0; transition: opacity .6s, transform .6s; }
.fx-object.fx-enter        { opacity: 1; transform: none; }

.fx-object[data-motion="slide-in"][data-position="left"]  { transform: translateX(-40px); }
.fx-object[data-motion="slide-in"][data-position="right"] { transform: translateX(40px); }
.fx-object[data-motion="fade"]                            { transform: none; }

@media (prefers-reduced-motion: reduce) {
    .fx-object { opacity: 1 !important; transform: none !important; transition: none !important; }
}
```

## 사용 컴포넌트
- 기존 에피소드 리더 DaisyUI 레이아웃 그대로
- 신규: 에디터용 **오브젝트 썸네일 카드** (`components/fx_object_card.html`)
- 신규: `/character` 슬래시 메뉴 UI (TipTap 런타임 내부)

## 개발
- [[dev-dynamic-reader]] — 동적 텍스트 리더 서버/클라이언트 로직
- [[dev-reader-scene-pipeline]] — 움직이는 장면 파이프라인 (Blender → webm/glb → three.js), PoC
