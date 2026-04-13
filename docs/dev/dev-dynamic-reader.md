# 동적 텍스트 리더 서버/클라이언트 로직

> 개발 문서

## 상태: 미구현 (Phase 1 재정의 후)

## 디자인
- [[design-dynamic-reader]] — 동적 텍스트 리더 디자인

## 기획
- [[dynamic-reader]] — 동적 텍스트 리더 기획

## 폐기된 이전 구현

아래 파일/설정은 Phase 1에서 제거됨. 재도입하지 말 것:

- `server/static/js/reader-fx.js` — 삭제됨
- `server/static/css/fx.css` — 삭제됨
- `apps/stories/forms.py`의 `"p": {"data-fx", "data-delay"}` 허용 — 제거됨
- `apps/stories/tests.py`의 `TestDynamicReaderSanitize` / `TestDynamicReaderEpisode` — 제거됨
- `server/tests/e2e/test_dynamic_reader.py` — 삭제됨

이유: CSS 텍스트 효과(shake/fade-in/rush/typewriter/float)는 제품 차별화 포인트인 Pretext 리플로우를 Phase 1에서 빠뜨린 잘못된 범위 분할이었음. 향후 필요하면 스킨 팩의 `text_effect` 에셋으로만 재도입.

## 구현 위치 (Phase 1)

### 모델
- `apps/stories/models.py` 또는 **신규 앱 `apps/skins/`**
  - `CharacterSprite(work, name, image, default_position, default_motion)`
  - `SkinPack(name, category, description, thumbnail, price, is_default, is_active)`
  - `SkinAsset(pack, asset_type, name, image, animation, config)`
  - `Work.genre` 필드 추가 (선택지: fantasy / romance / horror / daily / sf / mystery / history)

### 폼 / 새니타이징
- `apps/stories/forms.py`
  - `ALLOWED_TAGS`에 `div` 추가
  - `ALLOWED_ATTRIBUTES`에 다음 추가:
    ```python
    "div": {"class", "data-character", "data-object", "data-position", "data-motion"},
    "img": {"src", "alt"},  # 기존
    ```
  - `class` 허용은 `fx-object`만으로 제한하려면 별도 검증 필요 (nh3는 값 제한 불가 → 후처리 필요)

### 뷰 / URL
- `apps/stories/views/async_views.py`
  - `htmx_sprite_list(work_id)` — 작품에 연결된 캐릭터 + 장르 팩 오브젝트를 JSON으로 반환 (슬래시 메뉴용)
  - `htmx_sprite_upload(work_id)` — 캐릭터 스프라이트 업로드
- `apps/stories/urls.py`
  - `htmx/works/<int:work_id>/sprites/` (GET list, POST upload)

### 작품 생성 시 장르 기본 팩 자동 연결
- `apps/stories/signals.py` (신규) 또는 `Work.save()` 오버라이드
  - Work 생성 후 `SkinPack.objects.filter(category=work.genre, is_default=True, is_active=True)` 조회 → 별도 M2M(`Work.skin_packs`) 또는 동적 조회로 연결

### TipTap 에디터 확장
- `server/static/js/tiptap-editor.js`
  - `CharacterNode` 확장 추가 (atom block, 속성: `spriteId`/`assetId`, `position`, `motion`, `imageUrl`, `name`)
  - `renderHTML`: `<div class="fx-object" data-character data-position data-motion><img></div>`
  - `parseHTML`: `div.fx-object` 매칭
  - `/character` 슬래시 명령 추가 → `htmx_sprite_list` 호출 → 선택 UI → `editor.chain().focus().insertCharacter({...}).run()`
  - 에디터 내 표시: 썸네일 + 위치/모션 라벨 + 삭제 버튼 (NodeView)

### 리더 Pretext 런타임
- `server/static/js/reader-pretext.js` (신규)
  - `@chenglou/pretext` import
  - `document.querySelectorAll('.fx-object')` 수집
  - 이미지 preload 후 `pretext.layout(container, objects)` 호출
  - IntersectionObserver로 오브젝트 진입 감지 → `fx-enter` 클래스 토글
  - resize / htmx:afterSwap 시 재레이아웃 (디바운스 150ms)

### 번들 빌드
- `package.json` — `build:reader-pretext` 스크립트 추가
  - esbuild: `server/static/js/reader-pretext.js` → `server/static/js/reader-pretext-bundle.js`
  - 외부 의존성: `@chenglou/pretext` (npm 설치 필요)
- `package.json` 의존성 추가: `@chenglou/pretext`

### 템플릿
- `apps/stories/templates/stories/pages/episode_read.html`
  - `<script src="{% static 'js/reader-pretext-bundle.js' %}" defer></script>` 추가
- `apps/stories/partials/episode_content.html`
  - 본문 HTML은 그대로 출력 (이미 오브젝트 노드가 저장됨)
- CSS
  - `server/static/css/input.css`의 메인 레이어에 `.fx-object` 진입 모션 추가 (소량이라 별 파일 불필요)

## 구현 순서

1. **모델 + 마이그레이션**: `CharacterSprite`, `SkinPack`, `SkinAsset`, `Work.genre` → 장르별 기본 팩 시드 데이터 작성
2. **새니타이징 업데이트**: forms.py에 `div` 태그 + 오브젝트 속성 허용 + 후처리 검증
3. **스프라이트 업로드 뷰 + 템플릿**: 작가가 캐릭터 업로드 가능
4. **TipTap `CharacterNode` + `/character` 슬래시 메뉴**: 에디터에서 오브젝트 삽입
5. **Pretext 번들 + reader-pretext.js**: 리더에서 리플로우 작동
6. **진입 모션 CSS + IntersectionObserver**: 스크롤 진입 시 등장
7. **`prefers-reduced-motion` 폴백**: 모션 감도 사용자 대응

## 테스트 전략

- **Unit (apps/stories/tests.py)**:
  - `div.fx-object` 새니타이징 유지
  - `class`가 `fx-object` 외의 값이면 후처리에서 제거
  - Work 생성 시 장르 기본 팩 자동 연결
  - CharacterSprite 업로드 검증 (파일 크기, 확장자)
- **E2E (server/tests/e2e/)**:
  - 작가가 업로드 → `/character`로 삽입 → 발행 → 리더에서 이미지 로드 확인 (리플로우 자체는 Pretext 라이브러리에 위임, 우리 테스트에서는 DOM 존재만 확인)

## 의존성
- `@chenglou/pretext` (npm) — 약 15KB
- esbuild (이미 설치됨, TipTap 번들링에 사용 중)

## 선행 작업
- [[dev-story-episode-crud]] — 에피소드 CRUD (Episode.content HTML 저장)
- Work 모델에 `genre` 필드 추가 (별도 마이그레이션)
