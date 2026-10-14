# 동적 텍스트 리더

> 기획 문서

## 상태: 재기획 (Phase 1 재정의)

## 개요

소설 리더에서 텍스트가 정적으로 나열되지 않고, **캐릭터/오브젝트 스프라이트가 등장하면 본문이 그 주위로 자연스럽게 흘러가는** 읽기 경험.
차별화 포인트는 [Pretext](https://github.com/chenglou/pretext) 기반 **텍스트 리플로우** — 단순 CSS 애니메이션이 아닌, 장면 안에 오브젝트가 물리적으로 존재하는 것처럼 글이 배치된다.

**왜 Pretext가 핵심인가.**
CSS 애니메이션(흔들림/페이드인 등)은 어떤 플랫폼도 할 수 있지만, **오브젝트 주위 리플로우**는 이 제품을 이 제품답게 만드는 차별화 포인트다. Phase 1은 이 핵심부터 시작한다.

**장면 레이어.**
리플로우가 "글 속의 사물"이라면, 장면은 "글 뒤의 공간"이다. 촛불이 흔들리는 방, 먼지가 떠다니는 빛줄기처럼 **알아챌 듯 말 듯한 ambient 루프**를 글 뒤에 깔아 분위기를 만든다.
장면은 플랫폼이 Blender 파이프라인([[dev-reader-scene-pipeline]])으로 제작한 **템플릿**이고, 작가는 고르기만 한다. 모션은 미세해야 하며 글이 주인공이다.

## Phase 구조

| Phase | 내용 | 수익화 연결 |
|-------|------|------------|
| **Phase 1 (MVP)** | Pretext 리플로우 + 캐릭터 스프라이트 업로드 + 장르 기본 무료 팩 자동 매칭 + **ambient 루프 장면** (장르 팩 내장 템플릿) | 무료 기본 팩 (진입 장벽 제거) |
| Phase 2 | Rive/Lottie 애니메이션 스프라이트 + **3D 탐색 모먼트** (사물 클릭 → 원근 카메라 이동, 사물 → 분기 연결) + 프리미엄 스킨/장면 팩 **구매 플로우** | 팩당 $1~5 결제 |
| Phase 3 | 사용자 제작 스킨 마켓플레이스 | 수수료 모델 |

### 이전 Phase 1 (폐기)
CSS 텍스트 효과 5종(shake/fade-in/rush/typewriter/float)을 Phase 1로 잡았으나, 제품 차별화 포인트를 놓치는 범위 분할이라 폐기함.
관련 코드/테스트는 전부 제거. 향후 필요하면 **스킨 팩의 `text_effect` 에셋**으로 흡수(에셋 설계에 이미 포함됨).

## Phase 1 요구사항

### 핵심 — Pretext 리플로우
- 에피소드 본문 HTML에 오브젝트 노드(`<div data-character="...">` 또는 `<img data-object="...">`) 삽입 가능
- 리더 페이지 로딩 시 Pretext가 오브젝트 위치를 고려하여 본문 텍스트를 리플로우
- 스크롤에 따라 오브젝트가 뷰포트에 등장 (좌/우/중앙, 슬라이드/페이드 등 진입 모션)
- `prefers-reduced-motion` → 오브젝트 정적 배치 + 리플로우 없이 텍스트만 기본 흐름

### 핵심 — 캐릭터/오브젝트 등록
- 작가가 작품에 **캐릭터 스프라이트**를 업로드 (PNG/WebP, 투명 배경 권장)
- 필드: 이름, 이미지, (선택) 기본 등장 위치/모션
- 작품별 종속 (다른 작품 공유 안 함 — Phase 3에서 마켓 분리 시 고려)

### 핵심 — 장르 기본 무료 팩 자동 매칭
- 작품 생성 시 장르(판타지/로맨스/공포/일상/SF/미스터리/역사) 선택
- 플랫폼이 제작한 **장르별 기본 무료 팩**이 자동으로 해당 작품에 연결됨
- 작가는 추가 업로드 없이도 슬래시 메뉴에서 팩 내장 오브젝트를 바로 삽입 가능

### 핵심 — TipTap 에디터 확장
- `/character` 슬래시 메뉴: 작품에 등록된 캐릭터 + 장르 팩 오브젝트 목록에서 선택
- 선택 시 에디터에 **오브젝트 노드** 삽입 (`CharacterNode` atom block)
- 등장 위치(좌/우/중앙) + 모션 프리셋(slide-in / fade) 선택 UI

### 핵심 — ambient 루프 장면
- 장르 기본 팩에 **장면 템플릿** 1개 이상 포함 (예: 공포 → 촛불 방). 장면은 `SkinAsset(asset_type="scene")`
- 작가: `/scene` 슬래시 메뉴에서 장면 템플릿 선택 → 에피소드 본문에 **장면 블록** 삽입. 블록 이후 다음 장면 블록(또는 끝)까지가 그 장면의 구간
- 리더 표시 모드 (화면에 따라 자동 선택)
  - **배경 모드** (PC·태블릿 가로): 장면을 글 뒤에 깔고, 피사체는 글 반대쪽(`config.text_side`의 반대)에 오도록 배치
  - **삽화 모드** (폰·좁은 화면, 또는 글과 피사체가 겹칠 때): 장면 블록 위치에 문단 사이 삽화로 표시
- 재생 규칙: `autoplay muted loop playsinline`, 뷰포트 밖이면 일시정지, 한 번에 하나의 장면만 재생
- 파일: webm(VP9) + mp4(H.264, Safari/iOS 폴백) + 포스터 이미지
- 모션 원칙: 3~5초 끊김 없는 루프, 미세한 움직임만 (캐릭터 애니메이션·빠른 카메라 이동 금지)

### 새니타이징
- nh3 허용 속성: `data-character`, `data-object`, `data-position`, `data-motion`, `data-scene`
- 허용 태그 추가: `div` (오브젝트 컨테이너), `img` (이미 있음)

### 확장성 / 미포함
- **CSS 텍스트 효과 5종**: Phase 1 제외. 향후 스킨 팩의 `text_effect` 에셋으로 흡수
- **`scatter`/`dodge` 상호작용**: Phase 2 이상
- **3D 탐색 모먼트** (glb + three.js, 사물 클릭 → dolly-in/out, 사물 → 분기 연결): Phase 2. 파이프라인 PoC는 완료 ([[dev-reader-scene-pipeline]])
- **작가 직접 장면 제작**: 미포함. 장면은 플랫폼 제작 템플릿만
- **Canvas 2D 커스텀 렌더링**: Phase 2에서 필요하면 도입 (Phase 1은 DOM + Pretext로 시도)

## 데이터 모델

### CharacterSprite (신규)

| 필드 | 타입 | 비고 |
|------|------|------|
| work | FK(Work) | 작품에 종속 |
| name | CharField | 작가가 붙인 이름 ("기사", "용") |
| image | ImageField | 스프라이트 이미지 (PNG/WebP) |
| default_position | CharField | left / right / center (기본 left) |
| default_motion | CharField | slide-in / fade (기본 slide-in) |
| created_at | DateTimeField | |

### SkinPack (Phase 1에서도 정의하되, 판매는 Phase 2)

| 필드 | 타입 | 비고 |
|------|------|------|
| name | CharField | "판타지 기사 팩" |
| category | CharField | fantasy / romance / horror / daily / sf / mystery / history |
| description | TextField | |
| thumbnail | ImageField | |
| price | DecimalField | Phase 1은 0 (무료 기본 팩만) |
| is_default | BooleanField | True면 장르 자동 매칭 대상 |
| is_active | BooleanField | |
| created_at | DateTimeField | |

### SkinAsset

| 필드 | 타입 | 비고 |
|------|------|------|
| pack | FK(SkinPack) | |
| asset_type | CharField | sprite, scene (Phase 1) / text_effect / background (Phase 2+) |
| name | CharField | "기사", "드래곤" |
| image | FileField(null) | Phase 1은 정적 이미지 |
| animation | FileField(null) | Phase 2부터 Rive/Lottie |
| config | JSONField | 기본 position, motion 등. scene: `text_side`, `focus`(피사체 화면 영역), `period` |
| video_mp4 | FileField(null) | scene 전용 mp4 폴백 (webm은 `animation`, 포스터는 `image`) |

### 에피소드 HTML 저장 형식

```html
<p>기사가 동굴 앞에 섰다.</p>

<div data-character="knight" data-position="left" data-motion="slide-in"></div>

<p>검을 들어올리자 온 세계가 그의 것이었다. 그는 두려움 없이 발을 내디뎠다.</p>
```

- `data-character`: 작가가 업로드한 `CharacterSprite.id` 또는 장르 팩 `SkinAsset.id`
- `data-object`: 장르 팩에서 캐릭터가 아닌 오브젝트(검, 마법진 등)를 삽입할 때
- `data-position`: left / right / center
- `data-motion`: slide-in / fade
- `data-scene`: 장면 블록. 장면 `SkinAsset.id` (예: `<div data-scene="12"></div>`)

## 사용자 플로우

### 정상 — 작가
1. 작가 → 작품 생성 시 장르 선택 (예: 판타지)
2. 플랫폼 자동: 판타지 기본 무료 팩이 해당 작품에 연결됨
3. 작가 → 에피소드 작성 페이지에서 본문 작성
4. `/character` 입력 → 슬래시 메뉴에 본인 업로드 캐릭터 + 장르 팩 오브젝트 표시
5. 선택 → 에디터에 오브젝트 노드 삽입 (에디터에는 썸네일로 표시)
6. (선택) `/scene` 입력 → 장르 팩 장면 템플릿 목록(포스터 썸네일) → 선택 시 장면 블록 삽입
7. 발행

### 정상 — 독자
1. 독자 → 에피소드 페이지 접속
2. 페이지 로딩 시 Pretext가 오브젝트 위치 계산 → 텍스트 리플로우
3. 스크롤 → 오브젝트가 뷰포트에 진입하면 `data-motion`대로 등장
4. 본문은 오브젝트를 피해 자연스럽게 흘러감
5. 장면 블록 구간에 들어서면 장면이 배경(또는 삽화)으로 크로스페이드되어 루프 재생, 구간을 벗어나면 정지

### 에러 — Pretext 미지원/JS 비활성화
1. JS 비활성화 → 본문 텍스트는 정상 표시, 오브젝트는 기본 DOM 흐름대로 배치 (리플로우 없음)
2. 이미지 로드 실패 → 해당 오브젝트 자리만 비워짐, 텍스트는 기본 흐름
3. 장면 영상 로드 실패 / 자동재생 차단 → 포스터 이미지 정지 화면, 그것도 실패하면 장면 없이 텍스트만

### 엣지 — 모션 감도 설정 사용자
1. `prefers-reduced-motion: reduce` → 진입 모션 생략, 오브젝트는 즉시 최종 위치에 표시
2. 리플로우는 정적으로 1회만 계산 (스크롤 애니메이션 없음)
3. 장면은 영상 대신 포스터 이미지만 표시

### 엣지 — 장면
1. 좁은 화면(폰) → 배경 모드 대신 삽화 모드
2. 한 에피소드에 장면 블록 여러 개 → 현재 구간의 장면만 재생, 나머지는 로드 지연(lazy)
3. 장면 블록이 본문 맨 끝에 있어 구간이 비어 있음 → 삽화 모드로 1회 표시

### 엣지 — 오브젝트 없는 에피소드
1. `data-character` / `data-object` 없는 에피소드 → 기존과 동일 (Pretext 스크립트 로드는 되지만 처리할 노드가 없어 no-op)

### 엣지 — 장르 팩 미지정 작품
1. 기존에 생성된 작품이 장르를 갖지 않으면 기본 팩 미연결
2. 작가는 본인 업로드 캐릭터만 슬래시 메뉴에서 사용 가능

## 작가 미리보기

Phase 1 범위: TipTap 에디터 옆에 Pretext 프리뷰 영역을 **사후 MVP 확장**으로 둠. 첫 릴리즈는 에디터에 오브젝트 썸네일만 표시하고, 실제 리플로우는 **발행 후 리더 페이지에서 확인**하는 것으로 시작한다 (범위 통제).

## 디자인 문서
- [[design-dynamic-reader]] — 동적 텍스트 리더 디자인

## 개발 문서
- [[dev-dynamic-reader]] — 동적 텍스트 리더 서버/클라이언트 로직
- [[dev-reader-scene-pipeline]] — 장면 제작/배포 파이프라인 (Blender → webm/glb → 웹)

## 의존하는 기능
- [[story]] — 에피소드 시스템 (Episode.content HTML에 오브젝트 노드 저장)
- Work.genre 필드 (없으면 추가 필요)
