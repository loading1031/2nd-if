# 화면 설계·컴포넌트 연결

## 원본과 전시

| 관리 대상 | 원본 | 확인 위치 |
|---|---|---|
| IA·12개 화면·승인 흐름 | `pages.json`, `wireframes/*.svg`, `guide.py` | [index.html](index.html) |
| UI 토큰 | `server/static/css/input.css` → 설치된 Tailwind CSS·daisyUI light | Django 패턴 라이브러리 → Tokens |
| 공유 위젯 | `server/templates/components/` | Django 패턴 라이브러리 → Components |
| 컴포넌트 입력·사용법 | 각 공유 템플릿의 한 줄 헤더 주석 | 전시에 원본 주석을 직접 표시 |
| 예시 상태·데이터 | `server/templates/patterns/components/author_*/` | 위젯별 정상·로딩·빈 값·오류·권한·저장·비활성 예시 |
| 기존 화면 조합 예시 | `prototype.template.html`, `prototype.ts` | [prototype.html](prototype.html) |

`design/`에 별도 컴포넌트 전시나 토큰 값을 복제하지 않는다. `index.html`은 실제 카탈로그의 개별 항목과 공유 원본으로 연결한다. 전시와 기존 시안은 같은 Django include와 서비스 CSS를 사용한다. 페이지 조합은 카탈로그의 Pages → author_tools에도 있다.

화면 구조 승인 기준은 PR #34의 `c74c536768fd37fb2bc0836c13048492e57cdf29`이며 dev 병합은 `7c1bc0d153d145c26280baf9474f4d9912b92b37`이다. IA·승인 흐름은 유지한다.

## 카탈로그 실행

프로젝트 의존성을 설치한 환경에서 프로젝트 루트 기준:

```sh
uv sync
npm ci
npm run build:catalog
uv run python server/manage.py tailwind build
uv run python server/manage.py runserver
```

- 진입: <http://localhost:8000/pattern-library/> (개발 환경 전용)
- 토큰: <http://localhost:8000/pattern-library/pattern/patterns/tokens/theme/theme.html>
- 지표 카드: <http://localhost:8000/pattern-library/pattern/patterns/components/author_metric_card/author_metric_card.html>
- 모달: <http://localhost:8000/pattern-library/pattern/patterns/components/author_setting_update_dialog/author_setting_update_dialog.html>

CSS는 기존 `server/tailwindcss` CLI와 daisyUI 패키지가 필요하다. `output.css`는 Git에서 제외된 생성 파일이다. 전시 스크립트 원본은 `server/static/js/pattern-library.ts`, 생성 명령은 `npm run build:catalog`다. 토큰 목록 YAML은 변수 이름과 용도만 가지며, 표시 값은 실제 렌더된 CSS에서 읽는다.

## 설계 문서·기존 시안 재생성

```sh
.venv/bin/python design/build.py
```

서비스의 `server/static/css/input.css`를 빌드하고 같은 출력 CSS를 HTML에 포함한다. 별도 design 테마 진입점이나 UI CSS 사본을 관리하지 않는다. `pages.json`·SVG·TypeScript는 수정 가능한 원본이며 HTML/JS는 생성물이다. SVG는 실제 벡터이며 작은 문서 폭에서는 가로 스크롤할 수 있다. 에셋은 저장소의 `packages/codex-assets/` 원본을 참조한다.

독립형 CLI를 실행할 수 없는 환경은 같은 버전의 공식 npm CLI를 사용할 수 있다. 이 작업 환경에서는 Tailwind CSS 4.1.18·daisyUI 5.5.14를 사용했다.

```sh
.venv/bin/python design/build.py --tailwind-runtime /path/to/tailwind-runtime
```

의존성이 원래 체크아웃에만 있는 별도 워크트리는 `--runtime-root /path/to/checkout`을 함께 지정한다. `--reuse-ui-css`는 **기존 서비스 output.css**로 HTML/JS만 갱신하며 CSS 재빌드를 뜻하지 않는다. `guide.py`만 실행하면 CSS/JS 포함 전의 문서가 생성되므로 최종 생성은 `build.py`로 한다.

## 구현 경계

- 선택 그룹 이름과 패널·모달 ID는 호출자가 구분해 여러 인스턴스를 독립적으로 사용할 수 있다. 회차 선택은 options(value/label 목록)를 전달한다.
- 공통 버튼·입력·카드·모달 외형은 기존 daisyUI를 사용한다. 작가 도구에서 반복되는 도메인 UI만 공유 템플릿으로 둔다.
- 설정집 업데이트/유지는 해당 작품의 해당 설정집에만 적용한다. 목록 오른쪽의 작은 버전 업데이트 버튼을 유지한다.
- 지표 초대는 작품 열람·편집 권한과 분리한다. 전시의 상태는 표시 계약이며 실제 권한 검사나 저장을 수행하지 않는다.
- SVG 후보의 선택·연결됨·비활성, 출처·CC BY 3.0·팔레트를 전시한다. UI 테마 토큰과 에셋 팔레트는 구분한다.
- GA4·BigQuery·DB 저장·실제 채택/권한은 [#28](https://github.com/loading1031/2nd-if/issues/28)·[#32](https://github.com/loading1031/2nd-if/issues/32), 수집/스포일러/도감은 #15 범위다.

검증 기록과 남은 일은 [#31](https://github.com/loading1031/2nd-if/issues/31)·[PR #36](https://github.com/loading1031/2nd-if/pull/36)에서 관리한다. 빌드·템플릿 렌더·브라우저 배치/조작 확인은 구분해 기록한다.
