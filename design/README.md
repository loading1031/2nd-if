# 로컬 화면 설계서

[index.html](index.html)을 브라우저로 연다. 로그인·앱 서버·외부 CDN 없이 동작한다. SVG 후보는 저장소의 `packages/codex-assets/` 에셋을 참조한다.

## 구성

- 전체 정보 구조(IA)와 주요 이동 흐름 → 왼쪽 화면 목록 → 화면별 설명과 SVG 와이어프레임.
- 12개 화면에 목적, 진입·복귀 흐름, 동작, 상태·권한, 확정 규칙과 열린 결정을 기록한다.
- 컴포넌트·토큰은 화면 목록 아래에서 확인한다.
- [prototype.html](prototype.html)은 `server/templates/components/`의 Django include를 렌더링해 Tailwind/daisyUI로 빌드한 동작 시안이다. 패턴 라이브러리와 같은 컴포넌트 원본을 쓴다. 인사이트, 회차 선택, 공개 설정, 설정집별 버전 검토·업데이트, 표현 매핑을 조작할 수 있다. 데이터는 예시이며 서버 저장/API는 연결하지 않는다.
- 작가 도구 공통 UI와 상태 패턴은 `server/templates/patterns/components/author_*` 및 `patterns/pages/author_tools/`에서 같은 컴포넌트를 전시한다. Django 개발 서버에서 `/pattern-library/`를 열면 데스크톱·모바일 배치와 변형을 확인할 수 있다.
- 와이어프레임은 PNG를 감싼 파일이 아닌 실제 SVG다. 좁은 화면에서도 글자를 축소하지 않고 그림 영역을 가로 스크롤하며, 각 그림의 원본 링크로 따로 열 수 있다.

`index.html`은 CSS·스크립트·SVG를 포함한다. 화면 IA와 흐름은 PR #34에서 승인됐고, 구현 패턴은 제품 동작의 백엔드 계약을 대신하지 않는다. 동작 시안은 패키지 SVG를 `../packages/codex-assets/src/codex_assets/static/assets/game-icons/`에서 읽으므로 프로젝트 안에서 연다.

## 수정

| 파일 | 역할 |
|---|---|
| `pages.json` | IA·화면별 설명·상태·규칙 원본 |
| `wireframes/*.svg` | IA 1개와 화면 12개의 벡터 원본 |
| `draw-wireframes.py` | SVG 생성 소스. 직접 수정한 SVG를 다시 생성하면 덮어쓰므로 편집 방식을 선택한다 |
| `guide.py` | 문서 화면 구성과 내비게이션 생성 |
| `app.ts` | 화면 전환 |
| `prototype.template.html`, `prototype.ts` | 제품 동작 시안 원본 |
| `input.css` | Tailwind CSS 4.1.18·daisyUI 5.5.14, light 테마 설정 |
| `build.py` | HTML·CSS·TypeScript 빌드 및 HTML에 자산 포함 |

프로젝트 루트에서 실행한다. 설치된 Django·Tailwind CLI·daisyUI·esbuild가 필요하다.

```sh
.venv/bin/python design/build.py
```

Tailwind CLI가 실행되지 않는 환경에서는 기존 CSS를 재사용해 HTML·TypeScript 미리보기만 갱신할 수 있다. 이 옵션은 CSS를 새로 검증한 빌드로 보지 않는다.

```sh
.venv/bin/python design/build.py --reuse-ui-css
```

독립형 Tailwind CLI 대신 공식 npm CLI를 사용하면 해당 패키지가 설치된 폴더를 지정한다.

```sh
.venv/bin/python design/build.py --tailwind-runtime /path/to/tailwind-runtime
```

개발 연결: [디자인 #31](https://github.com/loading1031/2nd-if/issues/31), [인사이트 #28](https://github.com/loading1031/2nd-if/issues/28), [설정집 #32](https://github.com/loading1031/2nd-if/issues/32).

## 확인 범위

`build.py --reuse-ui-css`로 Django include HTML과 TypeScript 번들을 갱신했다. 이 모드는 기존 `ui.css`를 재사용하며 Tailwind CSS를 새로 빌드하지 않는다. Django system check와 작가 도구 패턴 템플릿 렌더링은 통과했다. 브라우저의 로컬 파일 보안 정책으로 실제 화면을 열 수 없어 데스크톱·모바일 시각 검토와 상호작용 검증은 미완료다.
