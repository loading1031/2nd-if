# 리더 장면 파이프라인 (Blender → 웹)

> 2026-10-17 변경: Blender 기반 장면·화면 반응 계획은 폐기했다. 시각 에셋 방향은 [작품별 수집 도감](../specs/collection-encyclopedia.md)과 이슈 #15/#33으로 대체한다. 아래 Blender 관련 내용은 과거 기획 이력이며 현재 구현 요구사항이 아니다. 설정집 권한·버전 및 텍스트 독서 요구사항은 별도 유지한다.

> 개발 문서

## 상태: PoC 완료 (프로덕션 미연동)

## 디자인
- [[design-dynamic-reader]] — 동적 텍스트 리더 디자인 (상위 디자인. 장면 전용 디자인 문서는 아직 없음)

## 기획
- [[dynamic-reader]] — 동적 텍스트 리더 기획

> **Phase 배치 (2026-10-14 확정)**: ambient 루프 장면(webm) = Phase 1, 3D 탐색 모먼트(glb) = Phase 2.
> 장면 전용 디자인(배경/삽화 모드 레이아웃, `/scene` 메뉴)은 아직 디자인 문서에 없음.

## 개요

소설 리더에 글 뒤로 깔리는 **움직이는 장면**을 넣기 위한 제작 → 배포 → 재생 파이프라인.
장면은 Blender에서 **코드(컴포넌트 + 주기 함수)** 로 만들고, 결과물은 정적 파일로 배포한다.
서버(Django)는 3D 연산을 하지 않고 파일과 데이터만 내려준다.

두 가지 출력 형태:

| 형태 | 파일 | 용도 |
|------|------|------|
| ambient 루프 영상 | `<scene>.webm` (+ mp4 예정) | 글 뒤 배경 / 문단 사이 삽화. 저사양·폰 폴백 |
| 실시간 3D | `<scene>.glb` | 사물 클릭 → 원근 있는 카메라 이동(탐색 모먼트) |

## 아키텍처 흐름

```
[빌드 시점 — 개발자 PC 또는 CI]  ※ Blender는 여기서만 실행
  blender/scenes/<scene>.py  ──(컴포넌트 조립: blender/lib/twoif_blender)
      │  Blender -b -P <scene>.py            → 루프 검증 → PNG → <scene>.webm
      │  Blender -b -P <scene>.py -- --glb   → <scene>.glb
      ▼
  산출물: <scene>.webm / <scene>.glb / scene.json(예정: 클릭 가능 사물·분기 연결)
      │  업로드
      ▼
[저장소 — Django static 또는 R2/S3 + CDN]

[실행 시점]
  Django + HTMX (현행 그대로)
   └─ 회차 페이지 HTML + "이 회차의 장면 = candle_room" 데이터만 응답
        ▼
  브라우저 / 앱 웹뷰(Capacitor)
   ├─ webm 모드: <video autoplay loop muted playsinline>
   └─ 3D 모드: scene-bundle.js(three.js + loop.js + 인터랙션)
        → glb 로드 → WebGL 렌더 → 클릭 시 dolly / 분기 연결
```

### 결정 사항
- **WASM 불필요**: three.js는 일반 JS + WebGL. 무거운 작업(모델링·조명)은 빌드 시점에 끝남. (glb 압축 디코더 Draco/meshopt를 쓰게 되면 three.js가 제공하는 정적 wasm 파일만 함께 배포)
- **Next/React 전환 불필요**: 서버 렌더링(Django+HTMX) 유지. 오프라인 읽기 계획 없음.
- **앱**: Django 페이지를 웹뷰(Capacitor `server.url`)로 감싼다. WebGL·세션 쿠키 그대로 동작.

## 구현 위치

### 제작 (Blender) — 구현 완료
- `blender/lib/twoif_blender/components.py` — 컴포넌트: `candle`, `dust_motes`, `room`, `camera`, `world`, `material`
- `blender/lib/twoif_blender/motion.py` — `loop_noise`, `loop_wave`, `drive()` (드라이버 기반 주기 모션)
- `blender/lib/twoif_blender/render.py` — `setup`, `check_loop`(루프 불변식 검증), `render_loop`(PNG → webm), `export_glb`
- `blender/scenes/candle_room.py` — 데모 장면 (3초 루프)
- 규칙: `.claude/skills/blender-scene/SKILL.md`

### 재생 (웹) — PoC
- `blender/web/loop.js` — `motion.py` 주기 함수의 JS 포팅 (**수식 동기화 필수**)
- `blender/web/candle_room.{html,js}` — 실시간 3D PoC
  - 사물 클릭 → dolly-in, 빈 곳 클릭 → dolly-out / 복귀, ESC 복귀
  - `camera.setViewOffset`(렌즈 시프트)로 기본 시점에서 글 칸 확보, 탐색 중 글 숨김
  - 불꽃 bloom, PointLight 그림자, 촛불/먼지 모션은 Blender와 같은 seed

### 프로덕션 연동 — 미구현
- `server/static/js/scene-player.js` (신규) → esbuild 번들 `scene-bundle.js`
  - `package.json`에 `build:scene` 추가 (TipTap `build:editor`와 같은 방식, **CDN 금지 규칙** 준수)
- 모델: 회차 ↔ 장면 연결 (예: `Episode.scene` 또는 장면 블록 노드) — 기획 확정 후 결정
- `scene.json` 스키마: 장면 이름, 비율별 영상, 클릭 가능 사물 목록, 사물 → 분기 연결
- 템플릿: `episode_read.html`에 장면 컨테이너 + 번들 로드

## 구현 내용

### 1. 장면 제작 원칙
1. 장면 = 컴포넌트 함수 조립. 컴포넌트는 키워드 인자(props)만 받고 루트 오브젝트를 반환
2. 모션 = 주기 드라이버. 키프레임·비주기 노이즈 금지 → `period` 프레임마다 정확히 반복
3. 렌더 전 `check_loop()`가 frame 0과 frame `period`의 모든 드라이버 값을 비교, 불일치 시 실패
4. `.blend`는 빌드 산출물. 소스는 Python 코드만 커밋 (`blender/out/`은 gitignore)

### 2. 글과 장면의 겹침 처리
- 기본: 렌즈 시프트로 피사체를 글 반대쪽에 배치 (원근 왜곡 없음)
- 탐색 중(다가가기/물러나기): 글을 숨기고, 복귀 시 다시 표시
- 예정: Blender에서 피사체 화면 좌표(`world_to_camera_view`)를 메타데이터로 출력 → 비율별 배치 계산, 겹침 불가피하면 문단 사이 삽화로 전환
- 보조: 글 쪽 그라데이션 스크림 (주 해결책 아님)

### 3. 화면/기기별 모드
| 환경 | 모드 |
|------|------|
| PC·태블릿 | 3D 탐색 또는 webm 배경 |
| 폰 / 저사양 / `prefers-reduced-motion` | webm 문단 삽화 또는 정적 이미지 |
| iOS 웹뷰 | `allowsInlineMediaPlayback`, 자동재생 허용 설정 + mp4 폴백 |

### 4. 콘텐츠 운영 (예정)
- 작가는 장면 스크립트를 쓰지 않는다. **장면 템플릿**(촛불 방, 비 오는 창가 …)을 고르고, 클릭 사물 → 분기 연결만 지정
- 템플릿 제작은 개발/디자인 팀이 Blender 파이프라인으로 수행

## 실행 방법

```bash
B=/Applications/Blender.app/Contents/MacOS/Blender
$B -b --factory-startup --python-exit-code 1 -P blender/scenes/candle_room.py -- --still 0   # 스틸 확인
$B -b --factory-startup --python-exit-code 1 -P blender/scenes/candle_room.py              # webm (≈30초)
$B -b --factory-startup --python-exit-code 1 -P blender/scenes/candle_room.py -- --glb     # glb
python3 -m http.server 8765 --directory blender   # → http://localhost:8765/web/candle_room.html
```

## 검증 결과 (2026-10-14)
- Blender 5.2.2 LTS, EEVEE: 1280×720 72프레임 루프 렌더 ≈27초, webm ≈55KB, 드라이버 126개 루프 검증 통과
- glb ≈36KB, three.js r170에서 기본/다가가기/물러나기 3시점 정상 (Playwright 캡처 확인)
- 미검증: 태블릿·iOS 웹뷰 실기기 성능, Safari webm 재생

## 알려진 한계 / 다음 작업
- 비주얼 퀄리티: 기본 도형 수준. `reader-aesthetic-reviewer` 리뷰 필요
- 실시간 렌더는 그림자 경계·재질 표현이 EEVEE보다 약함 → 라이트 베이크 검토
- `scene.json` 스키마, 비율별 렌더, mp4 폴백, 프로덕션 번들 미구현

## 선행 작업
- 장면 전용 디자인 문서 (`design-reader-scene` 등) 작성
