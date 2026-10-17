# 로컬 화면 설계서

[index.html](index.html)을 브라우저로 연다. 로그인·서버·외부 CDN 없이 동작한다.

## 구성

- 전체 정보 구조(IA)와 주요 이동 흐름 → 왼쪽 화면 목록 → 화면별 설명과 SVG 와이어프레임.
- 12개 화면에 목적, 진입·복귀 흐름, 동작, 상태·권한, 확정 규칙과 열린 결정을 기록한다.
- 컴포넌트·토큰은 화면 목록 아래에서 확인한다.
- [prototype.html](prototype.html)은 실제 Tailwind/daisyUI로 만든 보조 동작 시안이다. 인사이트, 공개 설정, 설정집별 버전 검토·업데이트, 표현 매핑을 조작할 수 있다. 데이터는 예시이며 서버 저장은 하지 않는다.
- 와이어프레임은 PNG를 감싼 파일이 아닌 실제 SVG다. 좁은 화면에서도 글자를 축소하지 않고 그림 영역을 가로 스크롤하며, 각 그림의 원본 링크로 따로 열 수 있다.

`index.html`은 CSS·스크립트·SVG를 포함한다. 다른 컴퓨터로 전달할 때는 원본 보기 링크와 동작 시안도 연결되도록 `design/` 폴더 전체를 전달한다. 최종 제품 디자인으로 승인된 상태는 아니다.

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

독립형 Tailwind CLI 대신 공식 npm CLI를 사용하면 해당 패키지가 설치된 폴더를 지정한다.

```sh
.venv/bin/python design/build.py --tailwind-runtime /path/to/tailwind-runtime
```

개발 연결: [디자인 #31](https://github.com/loading1031/2nd-if/issues/31), [인사이트 #28](https://github.com/loading1031/2nd-if/issues/28), [설정집 #32](https://github.com/loading1031/2nd-if/issues/32).

## 확인 범위

HTML 생성·CSS 빌드·TypeScript 번들을 수행했다. 브라우저 도구가 로컬 파일 관찰을 지원하지 않아 새 진입 화면의 브라우저 렌더링·클릭 검증은 완료로 표시하지 않는다.
