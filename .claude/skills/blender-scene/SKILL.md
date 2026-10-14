---
name: blender-scene
description: 2nd-if 리더용 움직이는 장면(ambient 루프 클립)을 Blender로 만들 때 사용. 컴포넌트 조립 + 주기 함수 드라이버로 모션을 만들고, 끊김 없는 webm 루프로 렌더한다. "Blender로 장면 만들어줘", "촛불/비/먼지 루프", "리더 배경 영상", blender/ 디렉토리 작업 시 트리거.
---

# Blender 장면 제작 (2nd-if)

리더에서 글 뒤에 깔리는 **미세한 ambient 루프 클립**을 만든다.
웹 개발의 컴포넌트 구조처럼 장면을 조립하고, 모션은 키프레임 대신 수학(주기 함수)으로 움직인다.

## 디렉토리

```
blender/
├── lib/twoif_blender/      ← 컴포넌트 라이브러리 (Single Source of Truth)
│   ├── components.py       ← candle, dust_motes, room, camera, world, material ...
│   ├── motion.py           ← loop_noise, loop_wave, drive()
│   └── render.py           ← setup, check_loop, render_loop (PNG → webm)
├── scenes/                 ← 장면 = 컴포넌트 조립 스크립트 (pages에 해당)
│   └── candle_room.py      ← 참고용 데모
└── out/                    ← 렌더 산출물 (gitignore)
```

- **소스는 Python 코드뿐**이다. `.blend` 파일은 빌드 산출물이므로 커밋하지 않고, GUI에서 수작업으로 고친 내용을 소스로 삼지 않는다.
- 장면 스크립트는 `reset_scene()`부터 시작해서 매번 처음부터 다시 만든다. 그래야 결과를 재현할 수 있다.

## 핵심 원칙

### 1. 컴포넌트 = 키워드 인자를 받는 함수
```python
def candle(*, period: int, location=(0,0,0), flicker: float = 0.18, seed: float = 0.0, ...) -> bpy.types.Object:
```
- 키워드 인자가 props 역할을 한다. 전역 상태에 의존하지 않는다.
- 하위 오브젝트를 루트 empty에 parent하고, 루트를 반환한다. 위치를 옮길 때는 루트만 움직인다.
- 움직이는 컴포넌트는 반드시 `period`를 인자로 받는다.
- 같은 메시를 여러 개 쓰면 메시 데이터를 공유한다. `dust_motes` 참고.
- 장면 스크립트에서 생 bpy 코드로 오브젝트를 만들지 않는다. 두 번 이상 쓸 것 같으면 `components.py`로 옮긴다.
- 지오메트리가 절차적이거나 인스턴스가 수백 개를 넘으면 **지오메트리 노드 그룹**으로 만들고, 그룹 입력을 Python 함수 인자로 노출한다. 노드 API는 `blender-skills` 플러그인의 `blender-geometry-nodes` 스킬을 참고한다.

### 2. 모션 = 주기 드라이버 (키프레임 금지)
```python
drive(light.data, "energy", f"{power} * (1 + {flicker} * loop_noise(frame, {period}, {seed}))")
drive(obj, "location", f"{base} + {amp} * loop_wave(frame, {period}, 1, {phase})", index=2)
```
- `loop_noise(frame, period, seed)`: 정수배 주파수 sin 합으로 만든 의사 노이즈. period마다 정확히 반복된다.
- `loop_wave(frame, period, cycles, phase)`: 단순 왕복 운동. **cycles는 반드시 정수**로 준다.
- 서로 연결된 움직임은 **같은 seed를 공유**해서 동기화한다. 예: 촛불 밝기와 불꽃 크기.
- 금지:
  - `keyframe_insert`
  - F-Curve의 Noise 모디파이어. 주기가 없어서 루프가 튄다.
  - `random()`을 표현식 안에서 직접 호출. 매 프레임 값이 달라진다.
  - 정수가 아닌 cycles 값.

### 3. 루프 불변식
- 프레임 `0 ~ period-1`을 렌더하고, `period` 프레임이 0 프레임과 같아야 한다.
- `render.render_loop()`가 렌더 전에 `check_loop()`로 모든 드라이버 값을 검증하고, 하나라도 다르면 실패시킨다. 이 검증을 끄지 않는다.

### 4. 미학: 글이 주인공
- 모션은 **알아챌 듯 말 듯한 수준**으로 만든다. 촛불 흔들림, 먼지, 빛의 호흡 정도가 적당하다.
- 캐릭터 애니메이션, 빠른 카메라 이동, 화려한 파티클은 넣지 않는다.
- 카메라 흔들림(`breathe`)은 0.002m 수준으로 둔다. 화면이 움직이는 게 의식되면 과한 것이다.
- 시각 결과는 `reader-aesthetic-reviewer` 에이전트로 검토받는다. 기술적으로 동작한다고 해서 완성은 아니다.

## 작업 흐름

Blender 실행 파일은 `/Applications/Blender.app/Contents/MacOS/Blender` (5.2 LTS)이다. 비대화형 셸에서는 PATH에 잡히지 않으므로 **전체 경로**로 실행한다.

```bash
B=/Applications/Blender.app/Contents/MacOS/Blender
# 1) 스틸 한 장 (수 초) → Read로 이미지 확인
$B -b --factory-startup --python-exit-code 1 -P blender/scenes/<scene>.py -- --still 0
# 2) 프리뷰 루프 (절반 해상도, 저샘플) → frames/에서 0, period/2 프레임 비교
$B -b --factory-startup --python-exit-code 1 -P blender/scenes/<scene>.py -- --preview
# 3) 최종 렌더 (1280x720, webm)
$B -b --factory-startup --python-exit-code 1 -P blender/scenes/<scene>.py
```
- `--factory-startup`: 사용자 설정과 애드온의 영향을 받지 않게 한다.
- `--python-exit-code 1`: 스크립트 에러를 종료 코드로 받는다.
- 결과물: `blender/out/<scene>/frames/####.png`, `blender/out/<scene>.webm` (VP9).
- 프레임 비교: `ffmpeg -i 0000.png -i 0036.png -filter_complex hstack cmp.png`로 붙여서 한 번에 확인한다.

## 새 컴포넌트 추가 절차
1. `components.py`에 함수를 추가한다. 키워드 인자만 받고, 기본값은 미세한 모션 수준으로 두고, docstring을 단다.
2. 움직이는 부분은 `drive()`와 `loop_noise`/`loop_wave`로만 만든다.
3. 데모 장면이나 새 장면에서 `--still`로 확인한 뒤 `--preview`로 루프를 확인한다.
4. 일반 bpy·노드 API는 `blender-skills` 플러그인 스킬을 참고하되, Blender 5.x 변경점은 아래 주의사항을 우선한다.

## Blender 5.2 주의사항 (실측)
- **`Action.fcurves`가 없다.** 5.x는 layered action 구조라서 옛날 예제의 `obj.animation_data.action.fcurves`는 깨진다. 이 프로젝트는 드라이버만 쓰므로 `anim.drivers`로 접근한다.
- **드라이버 함수는 세션마다 등록해야 한다.** `motion.register()`를 장면 스크립트 맨 앞에서 호출한다. 저장된 .blend를 다시 열면 함수가 없어서 드라이버가 에러 난다. .blend가 산출물로만 취급되는 이유다.
- 드라이버 표현식에서는 `frame`을 변수 없이 바로 쓸 수 있다.
- **라이트를 메시 안에 넣으면 빛이 갇힌다.** 예: 불꽃 구 안의 포인트 라이트. 감싸는 메시에 `visible_shadow = False`를 준다.
- EEVEE 샘플 설정은 `scene.eevee.taa_render_samples`이다. 프리뷰는 8, 최종은 32 이상을 쓴다. 샘플이 낮으면 그림자 경계가 거칠게 나온다.
- 색 관리는 `AgX`를 쓴다(기본값).

## 실시간 3D (웹) 내보내기
클릭으로 다가가거나 물러나는 인터랙션이 필요한 장면은 webm 대신 glb + three.js로 만든다.

```bash
$B -b --factory-startup --python-exit-code 1 -P blender/scenes/<scene>.py -- --glb   # → blender/out/<scene>.glb
python3 -m http.server 8765 --directory blender                                     # → /web/<scene>.html
```
- glb에는 지오메트리와 머티리얼만 들어간다. **드라이버와 라이트는 내보내지 않으므로** 웹에서 다시 만든다.
- 모션은 `blender/web/loop.js`(`motion.py`의 포팅)로 같은 수식, 같은 seed를 써서 재현한다. **두 파일의 수식은 항상 동기화**한다.
- 웹 코드는 오브젝트를 이름으로 찾는다(`candle_flame`, `dust_###`). 컴포넌트에서 오브젝트 이름을 바꾸면 웹 코드도 같이 고친다.
- 줌은 FOV나 CSS scale이 아니라 **카메라 위치를 옮기는 dolly**로 한다. 그래야 원근이 바뀐다.
- 글 칸은 `camera.setViewOffset`(렌즈 시프트)로 확보한다. 원근 왜곡 없이 피사체만 옆으로 밀린다.
- three.js 함정: PointLight 그림자 카메라의 `near` 기본값은 0.5m라서, 이 프로젝트 스케일(수십 cm)에서는 그림자가 사라진다. `0.005` 정도로 낮춘다.
