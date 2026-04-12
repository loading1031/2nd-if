# 동적 텍스트 리더 (Interactive Typography)

> MVP 기능

## 컨셉

소설 리더에서 텍스트가 정적 나열이 아니라, 장면/캐릭터 행동에 따라 동적으로 움직이는 읽기 경험.
작가가 캐릭터 스프라이트/삽화를 등록하면, 본문 중 캐릭터가 등장하는 장면에서 스프라이트가 나타나고 텍스트가 그 주위로 흘러감.

## 핵심 경험

### 캐릭터 등장
```
"기사가 검을 들어올렸다."

→ 기사 스프라이트가 페이지 왼쪽에서 슬라이드 인
→ 텍스트가 기사 주위로 리플로우 (Pretext 실시간 계산)
→ "검을 들어올렸다" 부분에서 검 올리는 애니메이션
```

### 장면 전환
```
"어둠이 걷히고 아침이 밝았다."

→ 배경이 점진적으로 밝아짐
→ 텍스트가 어둠→밝음 색상 전환
→ 태양 일러스트가 상단에서 떠오름
→ 텍스트가 태양 아래로 재배치
```

### 전투/액션
```
"드래곤이 불을 뿜었다."

→ 드래곤 스프라이트 등장 (우측)
→ 불꽃 파티클이 텍스트를 가로지름
→ 텍스트가 불꽃을 피해 흩어짐 (scatter 효과)
→ 잠시 후 텍스트가 원위치로 돌아옴
```

## 사용자 플로우

### 작가 (에피소드 작성 시)

1. TipTap 에디터에서 일반 텍스트 작성
2. 슬래시 메뉴 → "캐릭터 삽입" 선택
3. 등록된 캐릭터 목록에서 선택 (또는 새로 업로드)
4. 등장 위치(좌/우/중앙) + 모션 프리셋(slide-in, fade, bounce) 선택
5. 텍스트 효과: 단락 선택 → 효과 메뉴에서 지정 (shake, fade, rush 등)
6. 미리보기로 확인

### 독자 (에피소드 읽기 시)

1. 에피소드 페이지 접속
2. 스크롤하면 각 장면의 효과가 순서대로 재생
3. 캐릭터 스프라이트가 등장/퇴장
4. 텍스트가 스프라이트 주위로 동적 배치
5. `prefers-reduced-motion` 설정 시 정적 텍스트로 폴백

## 기술 아키텍처

```
서버 (Django)
  에피소드 HTML + 효과 메타데이터 + 캐릭터 스프라이트 URL
  ↓ (1회 전달, 웹소켓 불필요)
클라이언트 (브라우저)
  ├── Pretext (@chenglou/pretext, 15KB)
  │   └── 매 프레임: 스프라이트 위치 고려한 텍스트 레이아웃 계산 (0.05ms)
  ├── Canvas 2D / PixiJS
  │   └── 계산된 위치에 텍스트 + 스프라이트 렌더링
  ├── Rive / Lottie (선택)
  │   └── 캐릭터 스프라이트 애니메이션
  └── ScrollTrigger
      └── 스크롤 위치에 따라 장면 트리거
```

## 데이터 모델

### CharacterSprite (신규)
| 필드 | 타입 | 비고 |
|------|------|------|
| work | FK(Work) | 작품에 종속 |
| name | CharField | "기사", "드래곤" 등 |
| image | ImageField | 정적 이미지 (PNG/WebP) |
| animation | FileField(null) | Rive/Lottie 파일 (선택) |
| created_at | DateTimeField | 자동 |

### 에피소드 HTML 저장 형식

```html
<!-- 텍스트 효과 -->
<p data-fx="fade-in" data-delay="0">어둠 속에서 눈을 떴다.</p>
<p data-fx="shake" data-delay="500">쾅!</p>

<!-- 캐릭터 등장 -->
<div data-character="knight"
     data-position="left"
     data-motion="slide-in"
     data-trigger="scroll">
</div>
<p data-fx="reflow">기사가 검을 들어올렸다.</p>

<!-- 캐릭터 + 텍스트 상호작용 -->
<div data-character="dragon"
     data-position="right"
     data-motion="fade"
     data-action="breathe-fire">
</div>
<p data-fx="scatter" data-recover="2000">드래곤이 불을 뿜었다.</p>
```

`data-fx="reflow"` → Pretext가 캐릭터 스프라이트 주위로 텍스트 재배치
`data-fx="scatter"` → 텍스트가 흩어졌다가 `data-recover`ms 후 복구

## 구현 단계

### Phase 1: 텍스트 효과 (CSS, Pretext 불필요)
- `data-fx` 속성 파싱 + CSS 애니메이션 적용
- shake, fade-in, rush, typewriter, float
- 스크롤 트리거 (Intersection Observer)
- **의존성**: 없음 (순수 CSS + JS)
- **작업량**: 소
- → specs 참조: [[dynamic-reader]]

### Phase 2: 캐릭터 스프라이트 등장 (Pretext 도입)
- CharacterSprite 모델 + 이미지 업로드
- `data-character` 파싱 → 이미지 표시 + 모션
- Pretext로 스프라이트 주위 텍스트 리플로우
- TipTap 에디터에 캐릭터 삽입 메뉴
- **의존성**: `@chenglou/pretext`, Canvas 2D
- **작업량**: 중

### Phase 3: 애니메이션 스프라이트 (Rive/Lottie)
- 정적 이미지 대신 움직이는 스프라이트
- Rive/Lottie 파일 업로드 지원
- 스프라이트 액션 (검 올리기, 불 뿜기 등)
- 텍스트와 스프라이트 상호작용 (scatter, dodge)
- **의존성**: `@rive-app/canvas` 또는 `lottie-web`
- **작업량**: 대

## 작가 미리보기 (실시간)

에피소드 작성 페이지에서 TipTap 에디터와 Pretext 미리보기를 나란히 배치.

```
┌──────────────────────┬──────────────────────┐
│  TipTap 에디터        │  Pretext 미리보기     │
│                      │                      │
│  텍스트 작성 +        │  독자가 볼 화면 그대로 │
│  /character 삽입 +    │  캐릭터 등장 +        │
│  /effect 지정         │  리플로우 + 애니메이션 │
│                      │                      │
│  [HTML 소스]          │  [Canvas 렌더링]      │
└──────────────────────┴──────────────────────┘
모바일: 탭으로 전환 (편집 탭 / 미리보기 탭)
```

### 동작 원리
1. TipTap `onUpdate` 이벤트 → 현재 HTML 추출
2. HTML에서 `data-fx`, `data-character` 파싱
3. Pretext로 레이아웃 계산 (0.05ms) → Canvas에 렌더링
4. 타이핑하면서 미리보기가 실시간 업데이트

### 미리보기 컨트롤
- ▶ 재생: 스크롤 시뮬레이션 (효과 순서대로 재생)
- ⏸ 정지: 현재 프레임 고정
- ↻ 처음부터: 효과 초기화 후 재재생
- 📱/🖥 반응형 전환: 모바일/데스크톱 미리보기

## TipTap 에디터 확장

### 새 노드 타입: CharacterNode
```javascript
// TipTap Extension
const CharacterNode = Node.create({
  name: 'character',
  group: 'block',
  atom: true,
  addAttributes() {
    return {
      characterId: { default: null },
      position: { default: 'left' },
      motion: { default: 'slide-in' },
      trigger: { default: 'scroll' },
    }
  },
})
```

### 새 슬래시 메뉴 항목
- `/character` → 캐릭터 선택 모달
- `/effect` → 텍스트 효과 선택 (현재 단락에 적용)

## nh3 새니타이징 업데이트

허용 속성에 `data-fx`, `data-character`, `data-position`, `data-motion`, `data-trigger`, `data-delay`, `data-action`, `data-recover` 추가 필요.

## 수익 모델: 스킨 스토어

### 컨셉
스프라이트 + 텍스트 효과를 묶은 **스킨 팩**을 플랫폼에서 판매.
각 팩에 장르 카테고리를 부여하여, 작품 장르에 맞는 스킨이 **자동 적용**.
초기에는 플랫폼 제작 스킨만. 이후 사용자 커스텀 제작/판매 오픈.

### 장르 → 스킨 자동 매칭

```
작가: 작품 생성 (장르 = "판타지")
  ↓ 자동
플랫폼: 장르 매칭된 무료 기본 팩 자동 적용
  ↓ 에피소드 작성 시
TipTap: 해당 팩의 스프라이트/효과가 슬래시 메뉴에 표시
  ↓ 작가가 원하면
스킨 스토어: 같은 장르의 프리미엄 팩으로 교체/추가 구매
```

작가가 직접 스킨을 고르지 않아도 장르만 설정하면 기본 연출이 들어감.

### 장르-카테고리 매핑

| 장르 카테고리 | 기본 무료 팩 | 프리미엄 팩 (유료) |
|-------------|------------|-----------------|
| 판타지/무협 | 검, 방패, 마법진 (기본) | 기사 팩, 드래곤 팩, 마법사 팩 |
| 로맨스 | 꽃잎, 하트 (기본) | 벚꽃 팩, 별빛 팩, 웨딩 팩 |
| 공포/스릴러 | 그림자, 눈동자 (기본) | 귀신 팩, 좀비 팩, 심리공포 팩 |
| 일상/힐링 | 커피잔, 고양이 (기본) | 카페 팩, 여행 팩, 계절 팩 |
| SF/사이버 | 회로, 홀로그램 (기본) | 우주 팩, 로봇 팩, 디스토피아 팩 |
| 미스터리/추리 | 돋보기, 발자국 (기본) | 탐정 팩, 범죄현장 팩 |
| 역사 | 두루마리, 붓 (기본) | 조선 팩, 삼국지 팩, 중세 유럽 팩 |

### 스킨 팩 구성

| 팩 이름 | 스프라이트 | 텍스트 효과 | 배경 효과 |
|---------|-----------|-----------|----------|
| 판타지 기사 | 기사, 드래곤, 마법진, 성 | shake, scatter, reflow | 안개, 불꽃 파티클 |
| 로맨스 | 꽃잎, 하트, 캐릭터 실루엣 | fade-in, float, soft-glow | 벚꽃, 석양 그라데이션 |
| 공포/스릴러 | 귀신, 그림자, 눈동자 | glitch, flicker, distort | 안개, 비네팅, 화면 깨짐 |
| 일상/힐링 | 카페, 고양이, 날씨 아이콘 | typewriter, gentle-fade | 빗소리 효과, 따뜻한 톤 |
| SF/사이버 | 로봇, 우주선, 홀로그램 | matrix-rain, scan-line | 네온, 회로 패턴 |

### 데이터 모델

**SkinPack**
| 필드 | 타입 | 비고 |
|------|------|------|
| name | CharField | "판타지 기사 팩" |
| category | CharField | fantasy / romance / horror / daily / sf / mystery / history |
| description | TextField | 팩 설명 |
| thumbnail | ImageField | 스토어 미리보기 이미지 |
| price | DecimalField | 가격 (USDC/포인트, 0이면 무료) |
| is_default | BooleanField | 장르별 기본 무료 팩 여부 |
| is_active | BooleanField | 판매 중 여부 |
| created_at | DateTimeField | |

**SkinAsset** (팩에 포함된 개별 에셋)
| 필드 | 타입 | 비고 |
|------|------|------|
| pack | FK(SkinPack) | 소속 팩 |
| asset_type | CharField | sprite / text_effect / background |
| name | CharField | "기사", "shake" 등 |
| image | FileField(null) | 스프라이트/배경 이미지 |
| animation | FileField(null) | Rive/Lottie 파일 |
| css_class | CharField(null) | 텍스트 효과의 경우 CSS 클래스명 |
| config | JSONField | 효과 파라미터 (duration, intensity 등) |

**UserSkinPurchase**
| 필드 | 타입 | 비고 |
|------|------|------|
| user | FK(User) | 구매자 |
| pack | FK(SkinPack) | 구매한 팩 |
| purchased_at | DateTimeField | |
| tx_hash | CharField(null) | 결제 트랜잭션 (Polygon) |

### 사용 흐름

```
1. 작가: 작품 생성 시 장르 선택 (예: "판타지")
2. 플랫폼: 해당 장르의 기본 무료 팩 자동 연결
   └── SkinPack.objects.filter(category="fantasy", is_default=True)
3. 작가: 에피소드 작성 → 슬래시 메뉴에 해당 팩의 스프라이트/효과 자동 표시
4. 작가: (선택) 스킨 스토어에서 같은 장르 프리미엄 팩 구매 → 교체
5. 독자: 에피소드 읽을 때 스킨 효과 자동 적용
         (독자는 별도 구매 불필요 — 작가가 적용한 그대로 보임)
```

### 무료 기본 팩
- 기본 텍스트 효과 5종 (shake, fade-in, rush, typewriter, float)
- 범용 스프라이트 3종 (화살표, 별, 느낌표)
- 모든 작가가 사용 가능

### 가격 정책 (구상)
- 팩당 $1~5 (USDC) 또는 포인트
- 시즌 한정 팩 (할로윈, 크리스마스 등)
- 향후: 사용자 제작 스킨 마켓플레이스 (수수료 모델)

## 과제
- 모바일 성능 (Phase 1은 문제 없음, Phase 2부터 테스트 필요)
- 작가 UX (슬래시 메뉴로 최대한 간단하게)
- 접근성 (`prefers-reduced-motion` → 정적 텍스트 + 정적 이미지로 폴백)
- 캐릭터 스프라이트 가이드라인 (권장 크기, 투명 배경 등)
- SEO: Canvas 렌더링 시 원본 텍스트를 hidden DOM에 유지
- 스킨 에셋 CDN 배포 (로딩 속도)
- 스킨 불법 복제 방지 (에셋 URL 보호)

## 참고
- [Pretext GitHub](https://github.com/chenglou/pretext) — 텍스트 리플로우 계산
- [Pretext Umbrella Demo](https://pretextjs.dev/) — 오브젝트 주위 텍스트 리플로우
- [Rive](https://rive.app/) — 인터랙티브 애니메이션
- [Lottie](https://lottiefiles.com/) — After Effects → Web 애니메이션
- Instagram Reel (2026-04) — Pretext 소개 영상
