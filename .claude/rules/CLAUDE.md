# Django Async + HTMX + django-editor-js 프로젝트 컨벤션

## 기술 스택
- **Django 6.0+** (Native Async ORM) → [상세 가이드](django.md)
- **HTMX** → [상세 가이드](htmx.md)
- **django-editor-js** → [상세 가이드](django-editor-js.md)
- **Tailwind CSS + DaisyUI** → [Tailwind 가이드](tailwind-css.md) | [DaisyUI 가이드](daisyui.md)
- **uv** (패키지 관리)

## 🔄 개발 워크플로우

> **Claude**가 컨벤션을 참고하여 코드 작성, 리뷰, 문서 관리를 모두 수행합니다.
>
> 자세한 워크플로우는 [개발 워크플로우](#개발-워크플로우-1) 섹션을 참고하세요.

## 📚 문서 구조

### [Django 컨벤션](django.md)
- 비동기 뷰 정의
- Native Async ORM 사용법
- 병렬 쿼리 실행
- 데이터베이스 쿼리 최적화
- 권한 검증
- 테스트 작성
- Python 코드 스타일

### [HTMX 컨벤션](htmx.md)
- HTML 속성 네이밍
- URL 패턴
- 뷰 패턴 (CRUD)
- 템플릿 구조
- 응답 헤더 활용
- 에러 핸들링
- CSRF 보호
- 디바운싱 및 최적화
- 네이밍 컨벤션

### [django-editor-js 컨벤션](django-editor-js.md)
- 모델 정의
- 폼 정의
- HTMX 통합
- 컨텐츠 렌더링
- 이미지 업로드
- 데이터 검증

### [Tailwind CSS 컨벤션](tailwind-css.md)
- 프로덕션 환경 설정
- Django 설정
- 클래스 순서 컨벤션
- 반응형 디자인
- 다크 모드

### [DaisyUI 컨벤션](daisyui.md)
- DaisyUI 우선 사용 원칙
- 주요 컴포넌트 (btn, card, modal, alert 등)
- 폼 컴포넌트 (input, select, checkbox 등)
- 테마 설정
- HTMX 통합

### [개발 워크플로우 컨벤션](workflow.md)
- Git 브랜치 전략 (main → dev → feat/fix)
- 병렬 작업: Worktree + Subagent 사용 기준
- 브랜치 네이밍 규칙

### [컴포넌트 & 패턴 라이브러리 컨벤션](pattern-library.md)
- Single Source of Truth 원칙 (components/ 디렉토리)
- 새 컴포넌트/페이지 추가 절차
- django-pattern-library 설정 및 사용법
- 패턴 라이브러리 접속: `/pattern-library/`

## 프로젝트 구조

```
project/
├── .claude/                       # Claude 설정
│   └── rules/                     # 컨벤션 문서
├── .gemini/                       # Gemini 설정
├── .venv/                         # Python 가상환경
├── .gitignore
├── .python-version
├── .env.example
├── README.md
├── pyproject.toml                 # Python 패키지 관리 (uv)
├── uv.lock
│
└── server/                        # Django 서버
    ├── config/                    # Django 프로젝트 설정
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── settings/
    │       ├── __init__.py
    │       ├── base.py           # 공통 설정
    │       ├── dev.py            # 개발 환경
    │       └── prod.py           # 프로덕션 환경
    ├── apps/                      # 기능별 앱 분리
    │   ├── core/                  # 핵심 기능, 기본 페이지
    │   │   ├── management/
    │   │   │   └── commands/
    │   │   │       └── tailwind.py
    │   │   ├── views/
    │   │   │   ├── __init__.py
    │   │   │   ├── sync_views.py
    │   │   │   └── async_views.py
    │   │   ├── templates/core/
    │   │   │   ├── pages/
    │   │   │   ├── partials/
    │   │   │   └── components/
    │   │   ├── models.py
    │   │   ├── urls.py
    │   │   └── ...
    │   ├── users/                 # 사용자 인증/계정
    │   │   ├── views/
    │   │   ├── templates/users/
    │   │   ├── models.py
    │   │   └── ...
    │   └── articles/              # 게시글/콘텐츠 (예시)
    │       └── ...
    ├── static/
    │   └── css/
    │       ├── input.css          # Tailwind v4 소스
    │       └── output.css         # 빌드된 CSS
    ├── templates/
    │   ├── base.html
    │   └── components/            # 전역 컴포넌트
    ├── media/                     # 업로드 파일
    ├── manage.py
    ├── db.sqlite3
    └── tailwindcss                # Tailwind v4 CLI 바이너리
```

## 개발 워크플로우

**Claude**가 코드 작성, 문서 관리, 리뷰를 모두 수행합니다.

### 🎨 개발 프로세스 (Design-First)

이 프로젝트는 **디자인 우선** 방식으로 개발됩니다.

```
1. [UI/디자인] editor-js로 화면 디자인
   └── 화면 레이아웃 및 UI 컴포넌트 구성
   └── 사용자 흐름 확인

2. [커밋] 디자인 확정 후 커밋
   └── feat: {기능명} UI 디자인

3. [문서화] 확정된 디자인의 스펙을 Notion에 기록
   └── 필드명, 데이터 타입, API 경로 등 명세 작성
   └── Gemini CLI를 통해 Notion의 '문서/페이지 명' 페이지 생성 혹은 업데이트

4. [서버 로직] 확정된 디자인에 맞춰 백엔드 구현
   └── Django 비동기 뷰
   └── 모델 및 비즈니스 로직
   └── HTMX 연동

5. [커밋] 서버 로직 완료 후 커밋
   └── feat: {기능명} 서버 로직 구현
```

> **핵심 원칙**: 화면(UI)이 먼저 확정된 후에 서버 로직을 구현합니다.
> 이를 통해 요구사항을 시각적으로 확인하고, 불필요한 재작업을 방지합니다.

### 📝 워크플로우 예시

```
1. [Claude] 컨벤션을 참고하여 코드 작성
   └── django.md, htmx.md, daisyui.md 등을 참고
   └── 기능 구현 완료

2. [Claude] 셀프 리뷰
   ├── 컨벤션 준수 확인
   ├── 코드 품질 검토
   ├── 보안 및 성능 체크
   └── 필요 시 즉시 수정

3. 사용자 확인 후 최종 확정
```

### ✅ 리뷰 체크리스트

#### Django
- [ ] Native Async ORM 메서드 사용 (`aget`, `alist`, `acreate`)
- [ ] `sync_to_async`는 필요한 경우에만 사용
- [ ] Type hints 적용
- [ ] 에러 핸들링 구현

#### HTMX
- [ ] URL 패턴: `/htmx/{model}s/{action}/`
- [ ] `hx-target` 명시
- [ ] CSRF 토큰 포함
- [ ] 로딩 인디케이터 제공

#### Tailwind CSS + DaisyUI
- [ ] DaisyUI 컴포넌트 클래스 우선 사용 (`btn`, `card`, `input` 등)
- [ ] Tailwind 유틸리티는 미세 조정에만 사용 (간격, 크기 등)
- [ ] 프로덕션 빌드 사용 (CDN 금지)
- [ ] 반응형 디자인 적용

#### django-editor-js
- [ ] 이미지 업로드 검증 (파일 크기, 확장자)
- [ ] JSON 데이터 검증
- [ ] XSS 방지

## 💡 Claude 작업 가이드

### 🛠 작업 수행 원칙

1. **상황 파악**: 사용자의 요청을 분석하고 관련 컨벤션을 확인합니다.
2. **코드 작성**: 컨벤션 문서(django.md, htmx.md, daisyui.md 등)를 참고하여 직접 구현합니다.
3. **셀프 리뷰**: [리뷰 체크리스트](#-리뷰-체크리스트)에 따라 검증 후 필요 시 즉시 수정합니다.
4. **사용자 확인**: 결과를 사용자에게 보고합니다.

---

**마지막 업데이트**: 2026-03-21
**관리**: Claude (코드 + 문서 + 리뷰)
