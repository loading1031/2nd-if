# 동적 텍스트 리더 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[dynamic-reader]] - 동적 텍스트 리더 기획

## 프로덕션 템플릿
- `apps/stories/templates/stories/pages/episode_read.html`

## 효과 프리셋

| 효과 | data-fx 값 | CSS 설명 | 예시 텍스트 |
|------|-----------|---------|------------|
| 흔들림 | shake | 좌우 진동 keyframes (transform: translateX) | "쾅!" |
| 페이드인 | fade-in | opacity 0→1 (0.8s ease-in) | "어둠 속에서 눈을 떴다" |
| 질주 | rush | 우→좌 슬라이드 + 가속 (translateX + ease-in) | "그는 달리기 시작했다" |
| 타이핑 | typewriter | 글자 하나씩 표시 (clip + steps) | "편지를 읽었다..." |
| 떠오름 | float | 느린 상하 반복 (translateY infinite) | "구름 위를 걷는 듯" |

## TipTap /effect 메뉴 UI

에디터에서 `/effect` 입력 시 표시되는 슬래시 메뉴:

```
┌──────────────────────────┐
│ 텍스트 효과               │
│                          │
│ 〰️ 흔들림 (shake)        │
│ 🌅 페이드인 (fade-in)     │
│ 💨 질주 (rush)           │
│ ⌨️ 타이핑 (typewriter)   │
│ ☁️ 떠오름 (float)        │
└──────────────────────────┘
```

- 각 항목: 아이콘 + 효과 이름 (한국어) + data-fx 값 (영어)
- 선택 시 현재 단락(블록)에 `data-fx` 속성 부여
- 이미 효과가 있는 단락 재선택 시 효과 교체

## 에피소드 리더에서의 동작

### Intersection Observer 동작 흐름

```
1. 페이지 로드 → reader-fx.js 초기화
2. [data-fx] 요소 수집
3. 각 요소에 Intersection Observer 등록 (threshold: 0.3)
4. 요소가 뷰포트 30% 이상 진입 → "fx-active" 클래스 추가
5. CSS 애니메이션 자동 재생
6. 한 번 재생된 효과는 재트리거하지 않음 (1회성)
```

### 효과별 CSS 상세

#### shake (흔들림)
```
초기 상태: 정적
활성화: 0.5s 동안 좌우 2px 진동 (3회 반복 후 정지)
```

#### fade-in (페이드인)
```
초기 상태: opacity: 0
활성화: 0.8s ease-in으로 opacity: 1
```

#### rush (질주)
```
초기 상태: translateX(100px), opacity: 0
활성화: 0.6s ease-in으로 원위치 + opacity: 1
```

#### typewriter (타이핑)
```
초기 상태: 텍스트 숨김 (clip)
활성화: 글자 수 기반 steps()로 한 글자씩 표시 + 커서 깜박임
```

#### float (떠오름)
```
초기 상태: 정적
활성화: 2s infinite ease-in-out으로 ±5px 상하 반복
```

### prefers-reduced-motion 처리

```
@media (prefers-reduced-motion: reduce) 적용 시:
- 모든 애니메이션 duration → 0s
- 모든 요소 즉시 최종 상태로 표시
- float infinite 반복 → 정지
```

## 사용 컴포넌트

### DaisyUI
- 기존 에피소드 리더 컴포넌트 그대로 사용
- 추가 DaisyUI 컴포넌트 없음 (순수 CSS 애니메이션)

### 신규
- `reader-fx.js` — Intersection Observer + data-fx 파싱
- `input.css` @layer components — data-fx 애니메이션 정의

## 개발
- [[dev-dynamic-reader]] - 동적 텍스트 리더 서버/클라이언트 로직
