# 동적 텍스트 리더

> 기획 문서

## 상태: 기획 완료

## 개요

Phase 1 — CSS 기반 텍스트 효과 + 스크롤 트리거. 에피소드 리더에서 작가가 지정한 효과가 스크롤 시 재생된다.
작가는 TipTap 에디터의 `/effect` 슬래시 메뉴로 텍스트에 효과를 지정하고, 독자가 에피소드를 읽을 때 Intersection Observer가 뷰포트 진입을 감지하여 CSS 애니메이션을 순서대로 재생한다.

## 요구사항

### 핵심
- 텍스트 효과 5종: shake(흔들림), fade-in(페이드인), rush(질주), typewriter(타이핑), float(떠오름)
- 스크롤 트리거: Intersection Observer로 뷰포트 진입 시 효과 재생
- TipTap 에디터에서 `/effect` 슬래시 메뉴로 효과 지정
- 에피소드 HTML에 `data-fx` 속성으로 저장 (별도 모델 없음)
- `prefers-reduced-motion` 미디어 쿼리 감지 시 정적 텍스트로 폴백
- nh3 새니타이징에 `data-fx`, `data-delay` 속성 허용 추가

### 확장성
- Phase 2: 캐릭터 스프라이트 등장 (Pretext + Canvas 2D)
- Phase 3: 애니메이션 스프라이트 (Rive/Lottie)
- 향후: 스킨 스토어 (장르별 효과 팩 판매)

## 데이터 모델

별도 모델 없음. 에피소드 HTML 내 `data-fx` 속성으로 저장한다.

```html
<p data-fx="fade-in" data-delay="0">어둠 속에서 눈을 떴다.</p>
<p data-fx="shake" data-delay="500">쾅!</p>
<p data-fx="rush">그는 달리기 시작했다.</p>
<p data-fx="typewriter">편지를 읽었다...</p>
<p data-fx="float">구름 위를 걷는 듯</p>
```

- `data-fx`: 효과 종류 (shake / fade-in / rush / typewriter / float)
- `data-delay`: 효과 시작 지연 시간 (ms, 선택, 기본값 0)

## 사용자 플로우

### 정상 - 작가 (에피소드 작성)
1. 작가 → 에피소드 작성 페이지에서 텍스트 작성
2. 효과를 적용할 텍스트 단락에 커서 놓고 `/effect` 입력
3. 슬래시 메뉴에서 효과 선택 (shake / fade-in / rush / typewriter / float)
4. 해당 단락에 `data-fx` 속성 자동 부여
5. 미리보기로 효과 확인
6. 에피소드 발행

### 정상 - 독자 (에피소드 읽기)
1. 독자 → 에피소드 읽기 페이지 접속
2. 스크롤하면 각 효과 단락이 뷰포트에 진입
3. Intersection Observer가 감지 → CSS 애니메이션 재생
4. 효과는 `data-delay`에 따라 순서대로 재생

### 에러 - 효과 미지원 브라우저
1. CSS 애니메이션 미지원 브라우저 → 정적 텍스트로 표시 (점진적 향상)
2. JavaScript 비활성화 → 효과 없이 텍스트만 표시

### 엣지 - 모션 감도 설정 사용자
1. `prefers-reduced-motion: reduce` 설정된 사용자 → 모든 효과 자동 비활성화
2. 텍스트는 즉시 최종 상태로 표시 (fade-in은 opacity:1, typewriter는 전체 텍스트 표시)

### 엣지 - 효과가 없는 에피소드
1. `data-fx` 속성이 없는 에피소드 → 기존과 동일하게 정적 텍스트 렌더링
2. reader-fx.js는 로드되지만 처리할 요소가 없으므로 아무 동작 않음

## 디자인 문서
- [[design-dynamic-reader]] - 동적 텍스트 리더 디자인

## 개발 문서
- [[dev-dynamic-reader]] - 동적 텍스트 리더 서버/클라이언트 로직

## 의존하는 기능
- [[story]] — 에피소드 시스템 (Episode.content HTML에 data-fx 저장)
